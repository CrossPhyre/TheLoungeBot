from discord.ext.commands import command, Cog

class ChatCog(Cog):
    def __init__(self, bot):
        self._bot = bot


    @command(name="c-hi", help="(none) Says hello.")
    async def c_say_hello(self, context):
        user = context.author
        await context.send(f"Hello, {user.name}!")
