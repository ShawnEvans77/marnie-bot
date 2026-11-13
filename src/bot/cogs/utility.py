from discord.ext import commands
from .. import help_menu
from ..helpers import find_member, find_user
from ...constants.output import command
import random


class Utility(commands.Cog):
    '''General commands: !help, !pick, and !id.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_(self, ctx):
        if not ctx.channel.permissions_for(ctx.me).embed_links:
            for text_page in help_menu.build_text_pages(command.prefix):
                await ctx.send(text_page)
            return

        avatar_url = self.bot.user.display_avatar.url if self.bot.user is not None else None
        menu = help_menu.HelpMenu(help_menu.build_embeds(command.prefix, avatar_url))
        menu.message = await ctx.send(embed=menu.embeds[0], view=menu)

    @commands.command()
    async def pick(self, ctx, *, query: str = None):
        if query is not None:
            await ctx.send(f"i randomly selected: {random.choice(query.split(',')).strip()}")
        else:
            await ctx.send("how can i ``!pick`` from **no options**?\n\nremember, if you wanna use the ``!pick`` command, you type a set of comma separated values after ``!pick``. for example: ``!pick socks, shoes``")

    @commands.command(name="id")
    async def id_(self, ctx, *, query: str = None):
        if query is None:
            await ctx.send(f"your discord id is ``{ctx.author.id}``.")
            return

        user = find_member(ctx.guild, query) if ctx.guild is not None else find_user(self.bot.users, query)
        if user is None:
            await ctx.send(f"i couldn't find anybody named \"{query}\"... check their spelling?")
            return

        display_name = getattr(user, "display_name", None) or user.global_name or user.name
        await ctx.send(f"**{display_name}**'s discord id is ``{user.id}``.")
