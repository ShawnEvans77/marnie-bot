'''Marnie's commands, grouped into discord.py cogs.'''

from .chat_stats import ChatStats
from .errors import Errors
from .moderation import Moderation
from .pokedex import Pokedex
from .utility import Utility
from .wtp import WhosThatPokemon

ALL_COGS = (Pokedex, Utility, WhosThatPokemon, ChatStats, Moderation, Errors)
