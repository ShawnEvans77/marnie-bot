from discord.ext import commands
from ...utils import wtp_round as wtp
from io import BytesIO
import discord, asyncio

TIMEOUT_SECONDS = 30


class WhosThatPokemon(commands.Cog):
    '''!wtp: guess the Pokemon from its silhouette.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_channels = set()

    @commands.command()
    async def wtp(self, ctx):
        if ctx.channel.id in self.active_channels:
            await ctx.send("a round of who's that pokemon is already going on here! type your guess.")
            return

        self.active_channels.add(ctx.channel.id)

        try:
            async with ctx.typing():
                wtp_round = await wtp.fetch_round()

            if wtp_round is None:
                await ctx.send("sorry, i couldn't find a pokemon to show right now... try ``!wtp`` again in a bit?")
                return

            await ctx.send(
                f"**who's that pokemon?** type its name! you have {TIMEOUT_SECONDS} seconds.",
                file=discord.File(BytesIO(wtp_round["silhouette"]), filename="wtp.png"),
            )

            def is_correct(message) -> bool:
                return (
                    message.channel.id == ctx.channel.id
                    and not message.author.bot
                    and wtp.guess_matches(message.content, wtp_round)
                )

            reveal = discord.File(BytesIO(wtp_round["reveal"]), filename="wtp-answer.png")

            try:
                winner = await self.bot.wait_for("message", check=is_correct, timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                await ctx.send(f"time's up! it's **{wtp_round['name']}**!", file=reveal)
            else:
                await ctx.send(f"it's **{wtp_round['name']}**! {winner.author.mention} got it!", file=reveal)
        finally:
            self.active_channels.discard(ctx.channel.id)
