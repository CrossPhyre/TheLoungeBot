from random import randrange
import discord
from core.models import Yodel
from time import sleep
import threading
from os import path
import shared
from datetime import datetime


class YodelService:
    def __init__(self, youtube_agent):
        self._youtube_agent = youtube_agent
        self._text_channel = None
        self._voice_channel = None
        self._voice_client = None
        self._queue = []
        self._queue_index = 0
        self._playtime = 0
        self._last_tick = None

        self._ffmpeg_fp = path.join(shared.root_dir, 'shared\\dependencies\\ffmpeg\\ffmpeg.exe')
        self._ffmpeg_before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        self._ffmpeg_options = '-vn'
        # to see why these two sets of options are necessary for playback, see @MrSpaar's answer at
        # https://stackoverflow.com/questions/61959495/when-playing-audio-the-last-part-is-cut-off-how-can-this-be-fixed-discord-py

        self._halt_playback = False
        self._loading_thread = threading.Thread(target=self.__player_loop__, args=())
        self._loading_thread.daemon = True
        self._loading_thread.start()

        self._surprise_me_urls = \
            [
                'https://www.youtube.com/watch?v=vQhqikWnQCU',
                'https://www.youtube.com/watch?v=j4_KUs-Y-Fg',
                'https://www.youtube.com/watch?v=GLsCR2RMBak',
                'https://www.youtube.com/watch?v=N1l87Wzselg',
                'https://www.youtube.com/watch?v=ug_KiyZfPrI',
                'https://www.youtube.com/watch?v=4IRdw_Qgwqc',
                'https://www.youtube.com/watch?v=9q3zj37LCio',
                'https://www.youtube.com/watch?v=VY14zcUM9SI',
                'https://www.youtube.com/watch?v=yYtMYspzKBg',
                'https://www.youtube.com/watch?v=DcJFdCmN98s',
                'https://www.youtube.com/watch?v=XfMcM3tLhXo',
                'https://www.youtube.com/watch?v=b0PpsQ3wcUc',
                'https://www.youtube.com/watch?v=0v8Oenh0vWA',
                'https://www.youtube.com/watch?v=xyNW_evwoRA',
                'https://www.youtube.com/watch?v=BSDg2oSazNc',
                'https://www.youtube.com/watch?v=qVH40cnJ0us',
                'https://www.youtube.com/watch?v=WYS5NtRXlZQ',
                'https://www.youtube.com/watch?v=tloVHJtrJ_k',
                'https://www.youtube.com/watch?v=AVy7YPNP_zI',
                'https://www.youtube.com/watch?v=lOfZLb33uCg'
            ]


    def __get_next_yodel_id__(self):
        return (max([y.yodel_id for y in self._queue]) + 1) if self._queue else 1


    def __get_yodel_by_id__(self, yodel_id):
        for index, yodel in enumerate(self._queue):
            if yodel.yodel_id == yodel_id:
                return index, yodel

        return -1, None


    # the background (infinite) loop that controls the playback of the audio
    # if nothing needs played, it sleeps
    def __player_loop__(self):
        while True:
            if self._voice_client is None or self._queue_index == len(self._queue):
                # nothing to play or nowhere to play it, take a nap
                sleep(0.1)
            else:
                y = self._queue[self._queue_index]

                # begin streaming the audio
                self._last_tick = datetime.now()
                self._playtime = 0
                self._voice_client.play(discord.FFmpegOpusAudio(y.stream_url, executable=self._ffmpeg_fp, before_options=self._ffmpeg_before_options, options=self._ffmpeg_options))

                # loop while audio is playing
                # continuously updates playback time and waits for the audio
                # to finish playing
                while self._voice_client and (self._voice_client.is_playing() or self._voice_client.is_paused() or self._halt_playback):
                    sleep(0.1)

                    if self._voice_client and self._voice_client.is_playing():
                        # if the player is playing, record the elapsed time
                        n = datetime.now()
                        self._playtime += (n - self._last_tick).total_seconds()
                        self._last_tick = n

                if self._voice_client is not None and self._queue_index < len(self._queue):
                    if y.autoqueue:
                        # re-add song to end of queue; either the song autoqueues or failed to play
                        y2 = Yodel(self.__get_next_yodel_id__(), y.url, y.stream_url, y.title, y.duration, y.autoqueue)
                        self._queue.append(y2)

                    if self._queue_index == 2:
                        # remove the oldest song in the queue; this ensures that the queue
                        # only shows 2 songs that have already been played
                        self._queue.pop(0)
                    else:
                        # limit of 2 played songs not yet reached; just increment the index
                        self._queue_index += 1



    def add(self, url, autoqueue):
        success = False
        message = None

        if self._youtube_agent.is_valid_video_url(url):
            meta = self._youtube_agent.get_yt_video_meta(url)

            if not meta:
                message = 'I don\'t know what happened...I couldn\'t add that song...'
            else:
                y = Yodel(self.__get_next_yodel_id__(), url, meta['stream_url'], meta['title'], meta['duration'], autoqueue)
                self._queue.append(y)

                success = True
                message = f'Successfully added "{y.title}" to the queue!'
        else:
            message = 'Don\'t be mad, but I didn\'t recognize that URL format...'

        return success, message


    def add_playlist(self, url, autoqueue):
        success = False
        message = None

        if self._youtube_agent.is_valid_playlist_url(url):
            videos = self._youtube_agent.get_yt_playlist_meta(url)

            if not videos:
                message = 'Soooo...I didn\'t find any videos in that playlist...maybe I had an error? idk...'
            else:
                success = True

                for video in videos:
                    y = Yodel(self.__get_next_yodel_id__(), video['url'], video['stream_url'], video['title'], video['duration'], autoqueue)

                    self._queue.append(y)

                message = f'Successfully added {len(videos)} videos to the queue!'
        else:
            message = 'Don\'t be mad, but I didn\'t recognize that URL format...'

        return success, message


    def check_channels(self, text_channel):
        success = False
        message = None

        if self._text_channel is None or self._voice_channel is None:
            message = 'I\'m not ready for that command yet! I need you to set me up using the "$ydl-initiate" command.'
        elif self._text_channel.id != text_channel.id:
            message = f'Actually, Boss, I\'m looking for my commands from the "{self._text_channel.name}" channel. This is awkward...'
        else:
            success = True

        return success, message


    def clear(self):
        self._halt_playback = True

        if self._queue_index >= len(self._queue):
            message = 'Good news, I guess. There was nothing left in the queue to clear.'
        else:
            self._queue = self._queue[:self._queue_index + 1]
            message = 'I cleared out the queue for ya, Boss!'

        self._halt_playback = False

        return True, message


    def get_current_yodel(self):
        return self._queue[self._queue_index] if self._queue_index < len(self._queue) else None


    def get_playtime(self):
        return round(self._playtime)


    def get_yodels(self):
        return self._queue


    def move(self, yodel_id, position):
        self._halt_playback = True

        i, y = self.__get_yodel_by_id__(yodel_id)

        if not y:
            message = 'I couldn\'t find the item you were looking for...sorry...'
        elif i <= self._queue_index:
            message = 'You can only move items that haven\'t been played yet, Boss.'
        else:
            new_i = position + self._queue_index

            if i == new_i:
                message = 'It\'s already in that position, Boss!'
            elif new_i <= self._queue_index:
                message = 'You can\'t move an item to that position!'
            else:
                y = self._queue.pop(i)
                self._queue.insert(new_i, y)

                message = 'Got it moved!'

        self._halt_playback = False

        return True, message


    def move_next(self, yodel_id):
        return self.move(yodel_id, 1)


    def move_now(self, yodel_id):
        success, message = self.move_next(yodel_id)

        if success:
            self.next()

        return success, message



    def next(self):
        self._voice_client.stop()
        return True, 'Yeah, I didn\'t like that one either. On to the next, on, on to the next one!'


    def pause(self):
        self._voice_client.pause()
        return True, 'I paused the playback, Boss!'


    def play(self):
        self._voice_client.resume()
        return True, 'I resumed the playback, Boss!'


    async def quit(self):
        channel_name = self._voice_channel.name

        vc = self._voice_client
        self._voice_client = None
        vc.stop()

        self._queue = []
        self._queue_index = 0

        await vc.disconnect()
        self._voice_channel = None

        return True, f'I\'m out! I have disconnected from the "{channel_name}" channel and cleared the queue.'


    def remove(self, yodel_id):
        self._halt_playback = True

        i, y = self.__get_yodel_by_id__(yodel_id)

        if not y:
            message = 'I couldn\'t find the item you were looking for...sorry...'
        elif i <= self._queue_index:
            message = 'You can only remove items that haven\'t been played yet, Boss.'
        else:
            self._queue.pop(i)
            message = 'Cleaned up the rubish!'

        self._halt_playback = False

        return True, message


    def requeue(self, yodel_id):
        self._halt_playback = True

        i, y = self.__get_yodel_by_id__(yodel_id)

        if not y:
            message = 'I couldn\'t find the item you were looking for...sorry...'
        elif i >= self._queue_index:
            message = 'That item hasn\'t been played yet, Boss.'
        else:
            y2 = Yodel(self.__get_next_yodel_id__(), y.url, y.stream_url, y.title, y.duration, y.autoqueue)
            self._queue.append(y2)
            message = 'Got it back in the lineup, Boss!'

        self._halt_playback = False

        return True, message


    def set_autoqueue(self, yodel_id, autoqueue):
        self._halt_playback = True

        i, y = self.__get_yodel_by_id__(yodel_id)

        if not y:
            message = 'I couldn\'t find the item you were looking for...sorry...'
        elif i < self._queue_index:
            message = 'That item has already been played, Boss. If you would like to replay it, check out the "$ydl-requeue" command.'
        else:
            y.autoqueue = autoqueue
            message = 'Got it set, Boss!'

        self._halt_playback = False

        return True, message


    def set_text_channel(self, channel):
        self._text_channel = channel
        return True, f'Your wish is my command! I will now use the "{channel.name}" channel for my text IO.'


    async def set_voice_channel(self, channel):
        if self._voice_channel is not None:
            success = False
            message = 'I\'m already doing the thing, Boss! Do you want me to disconnect? If so, use the "$ydl-quit" command.'
        else:
            self._voice_channel = channel
            self._voice_client = await self._voice_channel.connect()

            success = True
            message = f'I\'m in! I have connected to the "{channel.name}" channel.'

        return success, message


    def shuffle(self):
        self._halt_playback = True

        num_remaining = len(self._queue) - self._queue_index - 1

        if num_remaining == 0:
            message = 'There\'s nothing to shuffle, Boss.'
        elif num_remaining == 1:
            message = 'I got that playlist of one item shuffled up for ya, Boss!'
        else:
            if num_remaining == 2:
                y = self._queue.pop(self._queue_index + 1)
                self._queue.insert(self._queue_index + 2, y)
            else:
                for x in range(num_remaining * 3):
                    i1 = randrange(num_remaining) + self._queue_index + 1
                    i2 = randrange(num_remaining) + self._queue_index + 1

                    if i1 != i2:
                        y = self._queue.pop(i1)
                        self._queue.insert(i2, y)

            message = 'Got it shuffled up, Boss!'

        self._halt_playback = False

        return True, message


    def surprise_me(self):
        url = self._surprise_me_urls[randrange(len(self._surprise_me_urls))]
        return self.add(url, False)
