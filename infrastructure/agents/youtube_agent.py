from __future__ import unicode_literals
from os import path
import shared
import youtube_dl
from infrastructure import helpers
from time import sleep
from datetime import datetime, timedelta
from queue import Queue
import threading
import re

class YoutubeAgent:
    # mostly added this in case having this hook is useful for the future
    class YoutubeDLLogger(object):
        def debug(self, msg):
            pass


        def warning(self, msg):
            pass


        def error(self, msg):
            print(msg)


    def __init__(self):
        # a few directories and filepaths for use in later code
        self._audio_dir = path.join(shared.root_dir, 'shared\\cache\\audio')
        self._pl_info_fp = path.join(shared.root_dir, 'shared\\cache\\temp\\pl_info.exe')
        self._ffmpeg_fp = path.join(shared.root_dir, 'shared\\dependencies\\ffmpeg\\ffmpeg.exe')

        self.video_url_re = re.compile(r'^(?:https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?:v=[a-zA-Z0-9\-_]+)(?:&list=[a-zA-Z0-9\-_]+)?$')
        self.playlist_url_re = re.compile(r'^(?:https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?:v=[a-zA-Z0-9\-_]+)(?:&list=[a-zA-Z0-9\-_]+)$')

        helpers.cleanup_dir(self._audio_dir)

        # this dictionary allows the code to pass in a url string and get out a filepath string
        self._url_fp_map = {}

        # this queue represents a set of urls that need to be loaded by the background task
        # notably, each item is a tuple in the format (url, num_attempts)
        self._urls_to_load = Queue()

        # used to determine how long (in seconds) the downloader should wait
        # before timing out based on the number of attempts it has made
        self._dl_timeouts = [10, 10, 30, 90, 600]

        # set up the background thread
        # this background thread reads from the queue _urls_to_load and performs the work
        # of actually downloading the urls to mp3 files
        self._loading_thread = threading.Thread(target=self.__loading_loop__, args=())
        self._loading_thread.daemon = True
        self._loading_thread.start()


    # given a url, returns a hashed name of the file
    # security is not the purpose of this hash; the purpose is only to consistently
    # provide the same (valid) name of a file given the same url
    #
    # NOTE: this only provides the same filepath during the same instance; if the
    # bot restarts, the hashing will be reseeded
    def __get_audio_fp__(self, url):
        return path.join(self._audio_dir, helpers.hash(url) + '.mp3')


    # the background (infinite) loop that checks for any urls that are queued to be
    # downloaded and downloads them; if none exist, it sleeps
    def __loading_loop__(self):
        while True:
            if self._urls_to_load.empty():
                # nothing to load, take a nap
                sleep(0.1)
            else:
                # pull the url and num_attempts out of the queue
                url, num_attempts = self._urls_to_load.get()

                # decide on how long to wait before timing out
                # the logic here is "if there is another URL waiting, do not
                # take the number of attempts into account, else progressively
                # increase the amount of time before timing out"
                timeout = self._dl_timeouts[min(num_attempts, 4) if self._urls_to_load.empty() else 0]

                if url and url not in self._url_fp_map:
                    # set up the options for the download
                    audio_fp = self.__get_audio_fp__(url)
                    ydl_opts = {
                        'ffmpeg_location': self._ffmpeg_fp,
                        'format': 'bestaudio/best',
                        'logger': self.YoutubeDLLogger(),
                        'noplaylist': True,
                        'outtmpl': audio_fp,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'socket_timeout': timeout,
                        'progress_hooks': [self.__youtube_dl_progress_hook__]
                    }

                    try:
                        # attempt to download
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])

                        # successfully downloaded; add the fp to the list for use
                        self._url_fp_map[url] = audio_fp
                    except Exception:
                        # if an error occurs, add it back to the bottom of the list
                        # with another attempt recorded
                        # TODO: does this handle timeouts?
                        self._urls_to_load.put((url, num_attempts + 1))


    # mostly added this in case having this hook is useful for the future
    def __youtube_dl_progress_hook__(self, d):
        if d['status'] == 'finished':
            print('Finished YT audio download. Beginning conversion.')


    # removes the "list" parameter of the url (sometimes this causes errors)
    def __clean_video_url__(self, url):
        return url[:url.index('&list=')] if self.is_valid_playlist_url(url) else url


    # returns the filepath to the mp3, if available
    # this will wait up to [timeout] seconds for it to finish loading
    def get_yt_audio_fp(self, url, timeout=10):
        url = self.__clean_video_url__(url)
        timeout = max(timeout, 0)

        if url not in self._url_fp_map:
            # the url has not been loaded yet; initiate loading
            self.load_yt_audio(url)
        elif not path.exists(self._url_fp_map[url]):
            # we have a filepath, but it doesn't exist
            # this should not ever happen, but if it does
            # remove the url, and load it again
            self._url_fp_map.pop(url)
            self.load_yt_audio(url)

        if url not in self._url_fp_map and timeout:
            # url not loaded yet; time to wait
            start_time = datetime.now()
            timeout = timedelta(seconds=timeout)

            while url not in self._url_fp_map and datetime.now() - start_time < timeout:
                # url (still) not loaded; take a nap
                sleep(0.1)

        return self._url_fp_map[url] if url in self._url_fp_map else None


    # attempts to download the metadata for the videos in a playist at a url
    def get_yt_playlist_meta(self, url):
        meta = None
        ydl_opts = {
            'logger': self.YoutubeDLLogger(),
            'outtmpl': self._pl_info_fp,
            'socket_timeout': 10,
            'quiet': True
        }

        success = False
        num_attempts = 0

        while not success and num_attempts < 3:
            num_attempts += 1

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, False)

                    if 'entries' in result:
                        meta = [{'url': e['webpage_url'], 'title': e['title'], 'duration': e['duration']} for e in result['entries']]

                    success = True
            except Exception:
                pass

        return meta if success else None


    # attempts to download the metadata for the video at a url
    def get_yt_video_meta(self, url):
        url = self.__clean_video_url__(url)

        meta = None
        ydl_opts = {
            'logger': self.YoutubeDLLogger(),
            'outtmpl': self._pl_info_fp,
            'socket_timeout': 10,
            'quiet': True
        }

        success = False
        num_attempts = 0

        while not success and num_attempts < 3:
            num_attempts += 1

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, False)
                    meta = {'title': result['title'], 'duration': result['duration']}
                    success = True
            except Exception:
                pass

        return meta if success else None


    # returns whether the url is a valid video url
    def is_valid_video_url(self, url):
        return self.video_url_re.match(url) is not None


    # returns whether the url is a valid video url
    def is_valid_playlist_url(self, url):
        return self.playlist_url_re.match(url) is not None


    # initiates loading the video(s)
    def load_yt_audio(self, url):
        if isinstance(url, list):
            urls = url
        else:
            urls = [url]

        for url in urls:
            url = self.__clean_video_url__(url)
            self._urls_to_load.put((url, 0))
