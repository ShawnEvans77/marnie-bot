from discord.ext import commands
from ...constants.getters import get_objs
from ...constants.structs import objects
import discord, asyncio, io, random, aiohttp


async def lookup(function, *args):
    '''Runs a PokeAPI lookup in a worker thread, so the bot keeps answering everyone else
    while it waits for PokeAPI.'''

    return await asyncio.to_thread(function, *args)


async def sprite_file(url: str, pokemon: str) -> discord.File:
    '''Downloads a sprite or artwork and wraps it as a Discord file.'''

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return discord.File(io.BytesIO(await resp.read()), f'{"shiny-" if "shiny" in url else ""}{pokemon}.png')


class Pokedex(commands.Cog):
    '''Pokemon lookups: !dt, !weak, sprites, and art.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def send_picture(ctx, answer):
        '''Sends a fetched picture, or Marnie's message if there was no picture.'''

        if isinstance(answer, list):
            await ctx.send(file=await sprite_file(*answer))
        else:
            await ctx.send(answer)

    @commands.command()
    async def dt(self, ctx, *, query: str = None):
        if query is not None:
            await ctx.send(await lookup(get_objs.fetcher.dt, query))
        else:
            await ctx.send("how can i do ``!dt`` on **nothing**?\n\nyou have to send a query to ``!dt``, silly!\n\nremember, if you wanna use ``!dt``, you type !dt then a Pokemon, Pokemon move, Pokemon ability, or item. for example: ``!dt morpeko``.")

    @commands.command()
    async def weak(self, ctx, *, query: str = None):
        if query is not None:
            split_char = ',' if ',' in query else '/'
            await ctx.send(await lookup(get_objs.weaker.weak, *query.split(split_char)))
        else:
            await ctx.send("how can i do ``!weak`` on **nothing**?\n\nyou have to send a type or a pokemon to ``!weak``, silly!\n\nremember, if you wanna use the ``!weak`` command, you type ``!weak`` then a type combo or a pokemon. for instance, you could type ``!weak morpeko``, or you could type ``!weak fire/flying``.")

    @commands.command()
    async def randmon(self, ctx):
        await ctx.send(await lookup(get_objs.fetcher.dt, str(objects.pokemon.randmon())))

    @commands.command()
    async def sprite(self, ctx, *, query: str = None):
        if query is not None:
            await self.send_picture(ctx, await lookup(get_objs.fetcher.sprite, query, False))
        else:
            await ctx.send("how can i find a sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!sprite`` command, you type ``!sprite`` then the name of the Pokemon whose sprite you want. for example, ``!sprite pikachu``.")

    @commands.command()
    async def shiny(self, ctx, *, query: str = None):
        if query is not None:
            await self.send_picture(ctx, await lookup(get_objs.fetcher.sprite, query, True))
        else:
            await ctx.send("how can i find a shiny sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!shiny`` command, you type ``!shiny`` then the name of the Pokemon whose shiny sprite you want. for example, ``!shiny goodra``.")

    @commands.command()
    async def randsprite(self, ctx):
        await self.send_picture(ctx, await lookup(get_objs.fetcher.sprite, str(objects.pokemon.randmon()), False))

    @commands.command()
    async def art(self, ctx, *, query: str = None):
        if query is not None:
            await self.send_picture(ctx, await lookup(get_objs.fetcher.art, query))
        else:
            await ctx.send("how can i find art **without knowing** the pokemon to find art for?\n\nremember, if you wanna use the ``!art`` command, you type ``!art`` then the name of the Pokemon whose art you want. for example, ``!art morpeko``.")

    @commands.command()
    async def randart(self, ctx):
        await self.send_picture(ctx, await lookup(get_objs.fetcher.art, str(random.randint(1, objects.pokemon.get_num_pokemon()))))
