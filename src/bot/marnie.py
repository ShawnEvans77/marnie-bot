import discord, logging, os, random, datetime, io, aiohttp
from discord.ext import commands
from ..constants.output import help as h
from ..constants.structs import objects
from ..utils import fetcher, weak_finder
from ..servers import web_server
from dotenv import load_dotenv

class Marnie:
    '''The Marnie Class represents your Discord Bot.'''

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents, help_command=None)
        self.fetcher = fetcher.Fetcher()
        self.weak_finder = weak_finder.Weak()

        @self.bot.event
        async def on_ready():            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.command()
        async def dt(ctx, *, query: str):
            await ctx.send(self.fetcher.dt(query))

        @self.bot.command()
        async def weak(ctx, *, query: str):
            tokens = query.split(",").strip()

            if len(tokens) == 1 or len(tokens) == 2:
                await ctx.send(self.weak_finder.weak(query))
            else:
                await ctx.send("!weak requires one or two types as arguments, try again")

        @self.bot.command()
        async def pick(ctx, *, query: str):
            await ctx.send(f"i randomly selected: {random.choice(query.split(",")).strip()}")

        @self.bot.command()
        async def randmon(ctx):
            await ctx.send(self.fetcher.dt(str(objects.pokemon.randmon())))

        @self.bot.command()
        async def help(ctx):
            await ctx.send(h.command)

        @self.bot.command()
        async def muted(ctx):
            answer = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    answer += f"{member.global_name.lower()} is muted for"
                    total = int((member.timed_out_until-datetime.datetime.now(datetime.UTC)).total_seconds())

                    hours, rem_min = total // 3600, total % 3600
                    minutes, rem_sec = rem_min // 60, rem_min % 60

                    answer += f" {Marnie.plural(hours, "hour")}, {Marnie.plural(minutes, "minute")}, and {Marnie.plural(rem_sec, "second")}\n"

            await ctx.send(answer if len(answer) != 0 else "nobody is muted right now")

        @self.bot.command()
        async def sprite(ctx, *, query):
            answer = self.fetcher.sprite(query, shiny=False)

            if isinstance(answer, list):
                await ctx.send(file=(await Marnie.sprite_handler(*answer)))
            else:
                await ctx.send(answer)

        @self.bot.command()
        async def shiny(ctx, *, query):
            answer = self.fetcher.sprite(query, shiny=True)

            if isinstance(answer, list):
                await ctx.send(file = (await Marnie.sprite_handler(*answer)))
            else:
                await ctx.send(answer)

        @self.bot.command()
        async def randsprite(ctx):
            rand_sprite = self.fetcher.sprite(str(objects.pokemon.randmon()), shiny=False)
            await ctx.send(file = (await Marnie.sprite_handler(*rand_sprite)))

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        web_server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)

    @staticmethod
    def plural(value: int, value_name: str) -> str:
        '''Useful for writing unit names with appropiate plurality.'''

        return f"{str(value)} {value_name}{"s" if value != 1 else ""}"
    
    @staticmethod
    async def sprite_handler(url: str, pokemon: str) -> discord.File:
        '''Returns appropiate sprite based on a given URL and Pokemon.'''
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return discord.File(io.BytesIO(await resp.read()), f'{"shiny-" if "shiny" in url else ""}{pokemon}.png')