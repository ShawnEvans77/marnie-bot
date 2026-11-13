from discord.ext import commands
from ..constants.output import command
from ..servers import web_server
from .cogs import ALL_COGS
from dotenv import load_dotenv
import discord, logging, os

class Marnie:
    '''The Marnie Class represents your Discord Bot. Its commands live in the cogs in src/bot/cogs/.'''

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix=command.prefix, intents=self.intents, help_command=None)
        self.bot.setup_hook = self.load_cogs

        @self.bot.event
        async def on_ready():
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

    async def load_cogs(self):
        '''Adds every cog to the bot. discord.py calls this once while logging in.'''

        for cog in ALL_COGS:
            await self.bot.add_cog(cog(self.bot))

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        web_server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)
