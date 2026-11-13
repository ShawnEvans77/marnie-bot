import asyncio
import logging
import subprocess
import sys

import pytest

from src.bot.marnie import Marnie


class FakeCtx:
    def __init__(self, guild=None):
        self.guild = guild
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


@pytest.fixture
def marnie(monkeypatch):
    '''A Marnie that does not open (and wipe) the real discord.log.'''

    monkeypatch.setattr(logging, "FileHandler", lambda **kwargs: logging.NullHandler())
    return Marnie()


def test_muted_in_dms_replies_instead_of_crashing(marnie):
    ctx = FakeCtx(guild=None)

    asyncio.run(marnie.bot.get_command("muted").callback(ctx))

    assert ctx.sent == ["i can only check who's muted inside a server, silly!"]


def test_pick_with_no_options_names_pick(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("pick").callback(ctx, query=None))

    assert "``!weak``" not in ctx.sent[0]
    assert "``!pick`` command" in ctx.sent[0]


def test_weak_finder_can_be_imported_first():
    result = subprocess.run(
        [sys.executable, "-c", "import src.utils.weak_finder as w; w.Weak()"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
