import asyncio
import logging

import pytest

from src.bot.marnie import Marnie


@pytest.fixture
def marnie(monkeypatch):
    '''A Marnie with all of its cogs loaded, that does not open (and wipe) the real discord.log.'''

    monkeypatch.setattr(logging, "FileHandler", lambda **kwargs: logging.NullHandler())
    bot = Marnie()
    asyncio.run(bot.load_cogs())
    return bot
