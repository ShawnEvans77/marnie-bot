from discord.ext import commands
from ..constants.output import help as h, insults
from ..constants.getters import get_objs
from ..constants.structs import objects
from ..servers import web_server
from dotenv import load_dotenv
import discord, logging, os, random, datetime, io, aiohttp

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

        @self.bot.event
        async def on_ready():            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.command()
        async def dt(ctx, *, query: str=None):

            if query is not None:
                await ctx.send(get_objs.fetcher.dt(query))
            else:
                await ctx.send("how can i do ``!dt`` on **nothing**?\n\nyou have to send a query to ``!dt``, silly!\n\nremember, if you wanna use ``!dt``, you type !dt then a Pokemon, Pokemon move, Pokemon ability, or item. for example: ``!dt morpeko``.")

        @self.bot.command()
        async def weak(ctx, *, query: str=None):

            if query is not None:
                split_char = ',' if ',' in query else '/'
                await ctx.send(get_objs.weaker.weak(*query.split(split_char)))
            else:
                await ctx.send("how can i do ``!weak`` on **nothing**?\n\nyou have to send a type or a pokemon to ``!weak``, silly!\n\nremember, if you wanna use the ``!weak`` command, you type ``!weak`` then a type combo or a pokemon. for instance, you could type ``!weak morpeko``, or you could type ``!weak fire/flying``.")

        @self.bot.command()
        async def pick(ctx, *, query: str=None):

            if query is not None:
                await ctx.send(f"i randomly selected: {random.choice(query.split(",")).strip()}")
            else:
                await ctx.send("how can i ``!pick`` from **no options**?\n\nremember, if you wanna use the ``!weak`` command, you type a set of comma separated values after ``!pick``. for example: ``!pick socks, shoes``")

        @self.bot.command()
        async def randmon(ctx):
            await ctx.send(get_objs.fetcher.dt(str(objects.pokemon.randmon())))

        @self.bot.command()
        async def help(ctx):
            await ctx.send(h.command)

        @self.bot.command()
        async def muted(ctx):
            answer = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    answer += f"**{member.global_name.lower()}** is muted for"
                    total = int((member.timed_out_until-datetime.datetime.now(datetime.UTC)).total_seconds())

                    hours, rem_min = total // 3600, total % 3600
                    minutes, rem_sec = rem_min // 60, rem_min % 60

                    answer += f" {Marnie.plural(hours, "hour")}, {Marnie.plural(minutes, "minute")}, and {Marnie.plural(rem_sec, "second")}. what a {random.choice(insults.insult_tup)}.\n"

            await ctx.send(answer if len(answer) != 0 else "nobody is muted right now")

        @self.bot.command()
        async def sprite(ctx, *, query: str=None):

            if query is not None:
                answer = get_objs.fetcher.sprite(query, shiny=False)
                if isinstance(answer, list):
                    await ctx.send(file=(await Marnie.sprite_handler(*answer)))
                else:
                    await ctx.send(answer)
            else:
                await ctx.send("how can i find a sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!sprite`` command, you type ``!sprite`` then the name of the Pokemon whose sprite you want. for example, ``!sprite pikachu``.")

        @self.bot.command()
        async def shiny(ctx, *, query: str=None):

            if query is not None:
                answer = get_objs.fetcher.sprite(query, shiny=True)
                if isinstance(answer, list):
                    await ctx.send(file = (await Marnie.sprite_handler(*answer)))
                else:
                    await ctx.send(answer)
            else:
                await ctx.send("how can i find a shiny sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!shiny`` command, you type ``!shiny`` then the name of the Pokemon whose shiny sprite you want. for example, ``!shiny goodra``.")

        @self.bot.command()
        async def randsprite(ctx):
            rand_sprite = get_objs.fetcher.sprite(str(objects.pokemon.randmon()), shiny=False)
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