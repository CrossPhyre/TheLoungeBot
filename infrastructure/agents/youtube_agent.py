from __future__ import unicode_literals
from os import path
import shared
import youtube_dl
from infrastructure import helpers
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
        # regular expresstions used to validate urls
        self.video_url_re = re.compile(r"^(?:https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?:v=[a-zA-Z0-9\-_]+)(?:&list=[a-zA-Z0-9\-_]+)?$")
        self.playlist_url_re = re.compile(r"^(?:https?:\/\/)?(?:www\.)?youtube.com\/watch\?(?:v=[a-zA-Z0-9\-_]+)(?:&list=[a-zA-Z0-9\-_]+)$")


    # mostly added this in case having this hook is useful for the future
    def __youtube_dl_progress_hook__(self, d):
        if d["status"] == "finished":
            print("Finished YT audio download. Beginning conversion.")


    # removes the "list" parameter of the url (sometimes this causes errors)
    def __clean_video_url__(self, url):
        return url[:url.index("&list=")] if self.is_valid_playlist_url(url) else url


    # attempts to download the metadata for the videos in a playist at a url
    def get_yt_playlist_meta(self, url):
        meta = None
        ydl_opts = {
            "logger": self.YoutubeDLLogger(),
            "socket_timeout": 10,
            "quiet": True
        }

        success = False
        num_attempts = 0

        while not success and num_attempts < 3:
            num_attempts += 1

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=False)

                    if "entries" in result:
                        # create a list of information for each video in the playlist
                        meta = [{
                            "url": e["webpage_url"],
                            "stream_url": e["formats"][0]["url"],
                            "title": e["title"],
                            "duration": e["duration"]}
                            for e in result["entries"]]

                    success = True
            except Exception:
                pass

        return meta if success else None


    # attempts to download the metadata for the video at a url
    def get_yt_video_meta(self, url):
        url = self.__clean_video_url__(url)

        meta = None
        ydl_opts = {
            "logger": self.YoutubeDLLogger(),
            "socket_timeout": 10,
            "quiet": True
        }

        success = False
        num_attempts = 0

        while not success and num_attempts < 3:
            num_attempts += 1

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=False)
                    meta = {
                        "title": result["title"],
                        "duration": result["duration"],
                        "stream_url": result["formats"][0]["url"]
                    }
                    success = True
            except Exception:
                pass

        return meta if success else None


    # returns whether the url is a valid video url
    def is_valid_video_url(self, url):
        return self.video_url_re.match(url) is not None


    # returns whether the url is a valid playlist url
    def is_valid_playlist_url(self, url):
        return self.playlist_url_re.match(url) is not None
