from discord.ext.commands import command, Cog
from bot import helpers
import math

class YodelCog(Cog):
    def __init__(self, bot, yodel_service):
        self._bot = bot
        self._yodel_service = yodel_service
        self._true_flags = (True, 'True', 'true', 'TRUE', 'T', 't', 'Yes', 'yes', 'YES', 'Y', 'y')


    def __draw_yodel_table__(self, yodels):
        if yodels:
            columns = [{'attr': 'icon', 'header': ' '},
                       {'attr': 'position', 'header': 'pos', 'align': 'right'},
                       {'attr': 'yodel_id', 'header': 'id'},
                       {'attr': 'title'},
                       {'attr': 'duration', 'format': helpers.format_timespan, 'align': 'right'},
                       {'attr': 'autoqueue'}]

            s = ''
            if helpers.prepare_table_columns(columns, yodels):
                s += helpers.draw_table(columns, yodels)
            else:
                s = 'I\'m having trouble displaying this table for some reason...'
        else:
            s = 'There\'s nothing in the queue! You should fix that, Boss!'

        return s


    @command(name='ydl-add', help='(url, [autoqueue]) Adds the audio from a YT video to the queue.')
    async def ydl_add(self, context, url, autoqueue=False):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            autoqueue = autoqueue in self._true_flags
            success, message = self._yodel_service.add(url, autoqueue)

        await context.send(message)


    @command(name='ydl-add-pl', help='(url, [autoqueue]) Adds the audio from all YT videos in a YT playlist to the queue.')
    async def ydl_add_playlist(self, context, url, autoqueue=False):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            autoqueue = autoqueue in self._true_flags
            success, message = self._yodel_service.add_playlist(url, autoqueue)

        await context.send(message)


    @command(name='ydl-autoqueue', help='(id, [autoqueue]) Sets the \'autoqueue\' value for the specified item.')
    async def ydl_autoqueue(self, context, yodel_id, autoqueue=True):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            autoqueue = autoqueue in self._true_flags
            success, message = self._yodel_service.set_autoqueue(int(yodel_id), autoqueue)

        await context.send(message)


    @command(name='ydl-clear', help='(none) Clears the remainder of the queue.')
    async def ydl_clear(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.clear()

        await context.send(message)


    @command(name='ydl-init', help='(none) Sets the text and voice channels based on the current context.')
    async def ydl_init(self, context):
        success, message = self._yodel_service.set_text_channel(context.channel)

        if success:
            if context.author.voice:
                voice_channel = context.author.voice.channel
                success, message = await self._yodel_service.set_voice_channel(voice_channel)
            else:
                message = 'You need to be in a channel for me to join you, Boss!'

        await context.send(message)


    @command(name='ydl-move', help='(id, position) Moves an item to the specified position (0-based) in the queue.')
    async def ydl_move(self, context, yodel_id, position):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.move(int(yodel_id), int(position))

        await context.send(message)


    @command(name='ydl-move-next', help='(id) Moves an item to next in the queue.')
    async def ydl_move_next(self, context, yodel_id):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.move_next(int(yodel_id))

        await context.send(message)


    @command(name='ydl-move-now', help='(id) Stops playing the current audio and plays the item specified.')
    async def ydl_move_now(self, context, yodel_id):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.move_now(int(yodel_id))

        await context.send(message)


    @command(name='ydl-next', help='(none) Plays the next item in the queue.')
    async def ydl_next(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.next()

        await context.send(message)


    @command(name='ydl-pause', help='(none) Pauses the current audio playback.')
    async def ydl_pause(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.pause()

        await context.send(message)


    @command(name='ydl-play', help='(none) Resumes playing the queue at the current position.')
    async def ydl_play(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.play()

        await context.send(message)


    @command(name='ydl-quit', help='(none) Stops playing music and disconnects from the voice channel.')
    async def ydl_quit(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = await self._yodel_service.quit()

        await context.send(message)


    @command(name='ydl-remove', help='(id) Removes an item from the queue.')
    async def ydl_remove(self, context, yodel_id):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.remove(int(yodel_id))

        await context.send(message)


    @command(name='ydl-requeue', help='(id) Re-adds an item to the bottom of the queue.')
    async def ydl_requeue(self, context, yodel_id):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.requeue(int(yodel_id))

        await context.send(message)


    @command(name='ydl-shuffle', help='(none) Shuffles the reamainder of the queue.')
    async def ydl_shuffle(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.shuffle()

        await context.send(message)


    @command(name='ydl-surprise-me', help='(none) Wouldn\'t you like to know...')
    async def ydl_surprise_me(self, context):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            success, message = self._yodel_service.surprise_me()

        await context.send(message)


    @command(name='ydl-view', help='([page_no]) Views the current player progress and the list of queued audio.')
    async def ydl_view(self, context, page_no=1):
        success, message = self._yodel_service.check_channels(context.channel)

        if success:
            yodels = self._yodel_service.get_yodels()
            current_yodel = self._yodel_service.get_current_yodel()
            current_yodel_index = None

            if current_yodel:
                current_yodel_index = yodels.index(current_yodel)

                duration = current_yodel.duration
                playtime = self._yodel_service.get_playtime()

                progress_percentage = (playtime / duration) * 100

                duration_f = helpers.format_timespan(duration)
                progress_f = helpers.format_timespan(playtime)
                remaining_f = helpers.format_timespan(duration - playtime)
                progress_bar_f = '=' * int(progress_percentage)
                remaining_bar_f = ' ' * (100 - int(progress_percentage))

                progress_bar = f'{progress_f} [{progress_bar_f}{remaining_bar_f}] {remaining_f}'
                await context.send(f'```{current_yodel.title} [{duration_f}]\n{progress_bar}```')

            num_pages = math.ceil(len(yodels) / 10) - 1
            page_no = min(max(page_no - 1, 0), num_pages)
            min_i = page_no * 10
            max_i = min_i + 9

            table_yodels = \
                [{'icon': '>' if y == current_yodel else '',
                  'position': '' if current_yodel_index is None or i < current_yodel_index else str(i - current_yodel_index),
                  'yodel_id': y.yodel_id,
                  'title': y.title,
                  'duration': y.duration,
                  'autoqueue': y.autoqueue}
                 for i, y in enumerate(yodels) if min_i <= i <= max_i]

            await context.send(self.__draw_yodel_table__(table_yodels))

            if num_pages and yodels:
                await context.send(f'```Displaying {min_i + 1} through {max_i + 1} of {len(yodels)} records.\nDisplaying page {page_no + 1} of {num_pages + 1}.```')
        else:
            await context.send(message)
