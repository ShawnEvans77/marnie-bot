from discord.ext import commands
import logging, requests


def pokeapi_error_message(error: requests.RequestException) -> str:
    '''What Marnie says when a PokeAPI lookup fails.'''

    if isinstance(error, requests.Timeout):
        return "sorry, pokeapi is taking too long to answer right now... try again in a bit?"

    response = getattr(error, "response", None)
    if isinstance(error, requests.HTTPError) and response is not None and response.status_code == 404:
        return "sorry, pokeapi doesn't have any data on that one..."

    return "sorry, i couldn't reach pokeapi right now... try again in a bit?"


class Errors(commands.Cog):
    '''Turns command errors into replies, or logs them.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        original = getattr(error, "original", error)

        if isinstance(original, requests.RequestException):
            await ctx.send(pokeapi_error_message(original))
            return

        # Everything else is logged the same way discord.py does when there is no handler.
        logging.getLogger("discord.ext.commands.bot").error("Ignoring exception in command %s", ctx.command, exc_info=error)
