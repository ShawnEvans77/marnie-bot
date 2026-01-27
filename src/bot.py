import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os, fetch_data as f, server

class Bot:
    '''The Bot Class represents your Discord Bot.'''

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()

        self.intents.message_content = True
        self.intents.members = True

        self.bot = commands.Bot(command_prefix='!', intents=self.intents)
        self.fetcher = f.FetchData()

        @self.bot.event
        async def on_ready():            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.command()
        async def dt(ctx, *, query):
            await ctx.send(self.fetcher.dt(query))

    def start(self):
        '''Causes the bot to go online and start accepting commands.'''

        server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)