import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os, fetch_data as f, server
import random
import constants
import datetime as d

class Bot:
    '''The Bot Class represents your Discord Bot.'''

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents, help_command=None)
        self.fetcher = f.FetchData()

        @self.bot.event
        async def on_ready():            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.command()
        async def dt(ctx, *, query: str):
            await ctx.send(self.fetcher.dt(query))

        @self.bot.command()
        async def pick(ctx, *, query: str):
            await ctx.send(f"i randomly selected: {random.choice(query.split(",")).strip()}")

        @self.bot.command()
        async def randmon(ctx):
            await ctx.send(self.fetcher.dt(str(constants.pokemon.randmon())))

        @self.bot.command()
        async def help(ctx):
            await ctx.send(constants.help)

        @self.bot.command()
        async def muted(ctx):
            response = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    response += f"{member.global_name.lower()} is muted for"
                    total = int((member.timed_out_until-d.datetime.now(d.UTC)).total_seconds())

                    hours, rem_min = total // 3600, total % 3600
                    minutes, rem_sec = rem_min // 60, rem_min % 60

                    response += f" {Bot.plural(hours, "hour")}, {Bot.plural(minutes, "minute")}, and {Bot.plural(rem_sec, "second")}\n"

            await ctx.send(response if len(response) != 0 else "nobody is muted right now")

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)

    @staticmethod
    def plural(value: int, value_name: str) -> str:
        '''Useful for writing unit names with appropiate plurality.'''

        return f"{str(value)} {value_name}{"s" if value != 1 else ""}"