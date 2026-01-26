import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os, fetch_data as f, server

class Bot:
    '''The Bot Class represents your Discord Bot. Start it using the run() function. 
    It reads the proper token from the .env file. It'''

    def __init__(self):
        '''Creates a bot. Please note - DISCORD_ENV is not included in this repo, 
        because I don't wanna give out bot access for free!'''
        '''If you wanna fork my project, please remember to not commit your .env file to the repo! :3'''

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
            '''A message to be printed to standard out indicating the bot started successfully.'''
            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.command()
        async def dt(ctx, *, query):
            '''Handles dt commands by invoking the dt() function on the fetcher object.'''

            await ctx.send(self.fetcher.dt(query))

    def start(self):
        '''Executes the bot.'''

        server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)