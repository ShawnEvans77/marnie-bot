import asyncio
import subprocess
import sys

import pytest



class FakeCtx:
    def __init__(self, guild=None):
        self.guild = guild
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


def test_muted_in_dms_replies_instead_of_crashing(marnie):
    ctx = FakeCtx(guild=None)

    asyncio.run(marnie.bot.get_command("muted")(ctx))

    assert ctx.sent == ["i can only check who's muted inside a server, silly!"]


def test_pick_with_no_options_names_pick(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("pick")(ctx, query=None))

    assert "``!weak``" not in ctx.sent[0]
    assert "``!pick`` command" in ctx.sent[0]


def test_weak_finder_can_be_imported_first():
    result = subprocess.run(
        [sys.executable, "-c", "import src.utils.weak_finder as w; w.Weak()"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_lando_t_is_the_therian_forme():
    from src.constants.output import aliases

    assert aliases.alias_map["lando-t"] == "landorus-therian"


def test_close_match_ignores_capital_letters():
    from src.constants.structs import objects

    assert objects.pokemon.close_match("PIKACHUU") == objects.pokemon.close_match("pikachuu") == "pikachu"
    assert objects.pokemon.close_match("PIKACHU") is None


def test_display_name_prefers_server_nickname():
    from types import SimpleNamespace
    from src.bot.helpers import display_name

    member = SimpleNamespace(display_name="snommy", global_name="Snom Fan", name="snomfan")
    user = SimpleNamespace(global_name="Snom Fan", name="snomfan")

    assert display_name(member) == "snommy"
    assert display_name(user) == "Snom Fan"
