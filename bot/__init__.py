from discord.ext.commands import Bot
import shared
from . import helpers
from .cogs import ChatCog, TaskCog, YodelCog
from core.services import TaskService, YodelService
from infrastructure.agents import TaskAgent, YoutubeAgent

class TheLoungeBot:
    def __init__(self):
        self._bot = Bot(command_prefix="$")
        self.__add_cogs__()
        self.__add_events__()


    def __add_cogs__(self):
        self._bot.add_cog(ChatCog(self._bot))
        self._bot.add_cog(TaskCog(self._bot, TaskService(TaskAgent())))
        self._bot.add_cog(YodelCog(self._bot, YodelService(YoutubeAgent())))


    def __add_events__(self):
        @self._bot.event
        async def on_command_error(context, error):
            await context.send(f"Beep boop. I did not understand that command. Maybe this error message will help...\n```{error}```")


        @self._bot.event
        async def on_ready():
            print(f"Logged in as {self._bot.user}")


    def run(self):
        self._bot.run(shared.secrets.bot_token)
