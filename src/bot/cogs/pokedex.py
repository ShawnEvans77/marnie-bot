from discord.ext import commands
from .. import dex_embed
from ...constants.getters import get_objs
from ...constants.structs import objects
import discord, asyncio, io, aiohttp


async def lookup(function, *args):
    '''Runs a PokeAPI lookup in a worker thread, so the bot keeps answering everyone else
    while it waits for PokeAPI.'''

    return await asyncio.to_thread(function, *args)



class Pokedex(commands.Cog):
    '''Pokemon lookups: !dt, !dex, !weak, sprites, and art.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = None

    async def cog_unload(self):
        if self.session is not None:
            await self.session.close()

    async def send_picture(self, ctx, answer, shiny: bool = False):
        '''Downloads and sends a fetched picture, or sends Marnie's message if there was no picture.
        Every download shares one session, made on the first one.'''

        if isinstance(answer, str):
            await ctx.send(answer)
            return

        url, pokemon = answer

        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                picture = await response.read()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            await ctx.send("sorry, i couldn't download that picture right now... try again in a bit?")
            return

        await ctx.send(file=discord.File(io.BytesIO(picture), f"{'shiny-' if shiny else ''}{pokemon}.png"))

    @commands.command()
    async def dt(self, ctx, *, query: str = None):
        if query is not None:
            await ctx.send(await lookup(get_objs.fetcher.dt, query))
        else:
            await ctx.send("how can i do ``!dt`` on **nothing**?\n\nyou have to send a query to ``!dt``, silly!\n\nremember, if you wanna use ``!dt``, you type !dt then a Pokemon, Pokemon move, Pokemon ability, or item. for example: ``!dt morpeko``.")

    @commands.command()
    async def dex(self, ctx, *, query: str = None):
        if query is None:
            await ctx.send("how can i do ``!dex`` on **nothing**?\n\nyou have to send a query to ``!dex``, silly!\n\nremember, if you wanna use ``!dex``, you type !dex then a Pokemon, Pokemon move, Pokemon ability, or item. for example: ``!dex morpeko``.")
            return

        entry = await lookup(get_objs.fetcher.dex, query)

        if isinstance(entry, str):
            await ctx.send(entry)
        elif not ctx.channel.permissions_for(ctx.me).embed_links:
            await ctx.send(entry.text)
        else:
            await ctx.send(entry.note, embed=dex_embed.build_embed(entry))

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
            await self.send_picture(ctx, await lookup(get_objs.fetcher.sprite, query, True), shiny=True)
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
        await self.send_picture(ctx, await lookup(get_objs.fetcher.art, str(objects.pokemon.randmon())))
