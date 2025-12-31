import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import fetch_data as f

class Bot:

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
            print(f"MARNIE BOT fully operational!")

        @self.bot.command()
        async def dt(ctx, *, query):

            # pokemon = pokemon.strip()
            # pokemon = pokemon.replace(" ", "-")

            # if pokemon.split("-")[0] == "mega":
            #     pokemon = pokemon.split("-")[1] + "-" + pokemon.split("-")[0]
            
            await ctx.send(self.fetcher.dt(query))

    def start(self):
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)