import asyncio
from types import SimpleNamespace

import discord
import pytest
import requests

import src.constants.getters.get_objs as get_objs
from src.bot import dex_embed
from src.constants.output import dex as d
from src.utils import dex
from src.utils.fetcher import Fetcher

f = get_objs.fetcher

ART_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"
SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"


class FakeCtx:
    def __init__(self, embed_links: bool = True):
        self.me = SimpleNamespace()
        self.channel = SimpleNamespace(permissions_for=lambda member: SimpleNamespace(embed_links=embed_links))
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append((content, kwargs))


def link(name: str, *evolves_to: dict) -> dict:
    '''One link of a PokeAPI evolution chain.'''

    return {"species": {"name": name}, "evolves_to": list(evolves_to)}


def fields(embed: discord.Embed) -> dict:
    return {field.name: field.value for field in embed.fields}


def fits_discord_limits(embed: discord.Embed) -> bool:
    return (len(embed.title) <= 256
            and len(embed.description or "") <= 4096
            and len(embed.fields) <= 25
            and all(len(field.name) <= 256 and 1 <= len(field.value) <= 1024 for field in embed.fields)
            and len(embed) <= 6000)


# ---------------------------------------------------------------- stat bars

@pytest.mark.parametrize('value, filled', [
    (0, 0),
    (1, 1),
    (10, 1),
    (58, 3),
    (100, 6),
    (255, 15),
    (999, 15),
])
def test_stat_bar(value: int, filled: int):
    bar = dex.stat_bar(value)

    assert bar == d.bar_full * filled + d.bar_empty * (d.bar_width - filled)
    assert len(bar) == d.bar_width


def test_stat_block_lines_up():
    stats = [{"base_stat": value, "stat": {"name": name}} for name, value in zip(d.stat_keys, (90, 85, 85, 125, 100, 95))]

    assert dex.stat_block({"stats": stats}) == "\n".join((
        "HP       90 █████░░░░░░░░░░",
        "ATK      85 █████░░░░░░░░░░",
        "DEF      85 █████░░░░░░░░░░",
        "SP. ATK 125 ███████░░░░░░░░",
        "SP. DEF 100 ██████░░░░░░░░░",
        "SPEED    95 ██████░░░░░░░░░",
        "BST     580",
    ))


@pytest.mark.parametrize('data', [
    {},
    {"stats": None},
    {"stats": []},
    {"stats": [{"base_stat": 50, "stat": {"name": "hp"}}]},
    {"stats": [{"base_stat": None, "stat": {"name": name}} for name in d.stat_keys]},
    {"stats": [{"base_stat": "50", "stat": {"name": name}} for name in d.stat_keys]},
])
def test_stat_block_is_left_out_without_all_six_stats(data: dict):
    assert dex.stat_block(data) is None


# ---------------------------------------------------------------- evolution

@pytest.mark.parametrize('chain, current, expected', [
    (link("snom", link("frosmoth")), "snom", "**Snom** → Frosmoth"),
    (link("abra", link("kadabra", link("alakazam"))), "alakazam", "Abra → Kadabra → **Alakazam**"),
    (link("eevee", link("vaporeon"), link("jolteon")), "jolteon", "Eevee → Vaporeon / **Jolteon**"),
    (link("wurmple", link("silcoon", link("beautifly")), link("cascoon", link("dustox"))), "wurmple", "**Wurmple** → Silcoon / Cascoon → Beautifly / Dustox"),
    (link("snom", link("frosmoth")), None, "Snom → Frosmoth"),
])
def test_evolution_line(chain: dict, current: str, expected: str):
    assert dex.evolution_line({"chain": chain}, current) == expected


@pytest.mark.parametrize('evolution', [
    None,
    {},
    {"chain": None},
    {"chain": {}},
    {"chain": "morpeko"},
    {"chain": link("morpeko")},
    {"chain": {"species": {"name": "morpeko"}}},
    {"chain": {"species": {"name": "morpeko"}, "evolves_to": None}},
    {"chain": {"species": None, "evolves_to": [link("frosmoth")]}},
    {"chain": {"species": {"name": "snom"}, "evolves_to": [None, "frosmoth", {}]}},
])
def test_evolution_line_is_left_out_without_evolution_data(evolution):
    assert dex.evolution_line(evolution, "morpeko") is None


# ---------------------------------------------------------------- species details

@pytest.mark.parametrize('rate, expected', [
    (-1, "genderless"),
    (0, "100% ♂"),
    (1, "87.5% ♂ / 12.5% ♀"),
    (4, "50% ♂ / 50% ♀"),
    (6, "25% ♂ / 75% ♀"),
    (8, "100% ♀"),
    (9, None),
    (-2, None),
    (None, None),
    ("4", None),
])
def test_gender(rate, expected):
    assert dex.gender({"gender_rate": rate}) == expected


def test_species_details_are_left_out_without_a_species():
    for species in (None, {}):
        assert dex.genus(species) is None
        assert dex.flavor_text(species) is None
        assert dex.tags(species) == []
        assert dex.gender(species) is None
        assert dex.egg_groups(species) is None
        assert dex.catch_rate(species) is None


def test_egg_groups_use_the_games_names():
    species = {"egg_groups": [{"name": "ground"}, {"name": "humanshape"}, {"name": "no-eggs"}, {"name": "brand-new"}]}

    assert dex.egg_groups(species) == "Field, Human-Like, Undiscovered, Brand New"


def test_flavor_text_is_the_newest_one_in_marnies_language_and_tidied():
    def entry(text: str, language: str) -> dict:
        return {"flavor_text": text, "language": {"name": language}}

    species = {"flavor_text_entries": [
        entry("Its brain can out\xad\nperform a super\xad\ncomputer.\x0cIts intelligence\nquotient is said\nto be 5,000.", "en"),
        entry("Son cerveau est puissant.", "fr"),
    ]}

    assert dex.flavor_text(species) == "Its brain can outperform a supercomputer. Its intelligence quotient is said to be 5,000."
    assert dex.flavor_text({"flavor_text_entries": [entry("Son cerveau est puissant.", "fr")]}) is None


def test_size_is_left_out_when_the_games_give_none():
    assert (dex.height({"height": 17}), dex.weight({"weight": 509})) == ("1.7 m", "50.9 kg")
    assert (dex.height({"height": 0}), dex.weight({"weight": 0})) == (None, None)
    assert (dex.height({}), dex.weight({"weight": None})) == (None, None)


def test_effect_text_is_tidied():
    raw = "Used in battle\n:   Attempts to catch a wild Pokémon.\n\n    If used in a trainer battle,  nothing happens."

    assert dex.tidy(raw) == "Used in battle: Attempts to catch a wild Pokémon.\n\nIf used in a trainer battle, nothing happens."


def test_clip_fits_discord_limits():
    assert dex.clip("short", 10) == "short"
    assert dex.clip("a" * 5000, d.description_limit) == "a" * 4095 + "…"


# ---------------------------------------------------------------- embeds from made-up data

def test_pokemon_embed_with_no_data_at_all_still_builds():
    '''The worst case: PokeAPI answers with nothing useful, and has no species or evolution chain.'''

    embed = dex_embed.build_embed(dex.DexEntry(kind="pokemon", name="snom", data={}, text=""))

    assert embed.title == "Snom • #872"
    assert embed.description is None
    assert embed.fields == []
    assert embed.image.url is None
    assert embed.thumbnail.url is None
    assert embed.color.value == d.default_color
    assert embed.footer.text == d.footer


def test_pokemon_embed_leaves_out_only_what_is_missing():
    data = {
        "types": [{"type": {"name": "ice"}}, {"type": {"name": "bug"}}],
        "abilities": [{"ability": {"name": "shield-dust"}, "is_hidden": False}, {"ability": {"name": "ice-scales"}, "is_hidden": True}],
        "species": {"name": "snom"},
        "sprites": {"front_default": None, "other": None},
    }
    entry = dex.DexEntry(kind="pokemon", name="snom", data=data, text="", species={"is_baby": True}, evolution={"chain": link("snom")})

    embed = dex_embed.build_embed(entry)

    assert embed.description == "baby"
    assert fields(embed) == {
        "type": "Ice / Bug",
        "abilities": "Shield Dust\nIce Scales *(hidden)*",
        "weaknesses": "**Fire**, Flying, **Rock**, Steel",
        "resistances": "Grass, Ground, Ice",
        "immunities": "none",
    }
    assert embed.color.value == d.type_colors["ice"]
    assert embed.image.url is None
    assert embed.thumbnail.url is None


def test_pokemon_embed_skips_matchups_for_a_type_outside_the_chart():
    data = {"types": [{"type": {"name": "stellar"}}]}

    embed = dex_embed.build_embed(dex.DexEntry(kind="pokemon", name="snom", data=data, text=""))

    assert fields(embed) == {"type": "Stellar"}
    assert embed.color.value == d.default_color


@pytest.mark.parametrize('sprites, expected', [
    ({"front_default": "sprite.png", "other": {"official-artwork": {"front_default": "art.png"}}}, "art.png"),
    ({"front_default": "sprite.png", "other": {"official-artwork": {"front_default": None}}}, "sprite.png"),
    ({"front_default": "sprite.png"}, "sprite.png"),
    ({"front_default": None, "other": None}, None),
])
def test_pokemon_embed_never_uses_a_big_image(sprites: dict, expected: str | None):
    '''A big image makes Discord shrink the whole embed to the image's width, which squeezes
    the fields. The art goes in the thumbnail instead, or the sprite if there is no art.'''

    embed = dex_embed.build_embed(dex.DexEntry(kind="pokemon", name="snom", data={"sprites": sprites}, text=""))

    assert embed.image.url is None
    assert embed.thumbnail.url == expected


@pytest.mark.parametrize('kind', ["move", "ability", "item"])
def test_other_embeds_with_no_data_say_so(kind: str):
    data = {"effect_entries": [], "flavor_text_entries": []}

    embed = dex_embed.build_embed(dex.DexEntry(kind=kind, name="booster-energy", data=data, text=""))

    assert embed.title == "Booster Energy"
    assert embed.description == d.no_description
    assert all(field.value == "-" for field in embed.fields)
    assert fits_discord_limits(embed)


def test_long_text_is_cut_to_fit_discord():
    data = {
        "effect_entries": [{"effect": "word " * 2000, "language": {"name": "en"}}],
        "flavor_text_entries": [],
        "pokemon": [{"pokemon": {"name": f"pokemon-with-a-very-long-name-{number}"}} for number in range(500)],
    }

    embed = dex_embed.build_embed(dex.DexEntry(kind="ability", name="blaze", data=data, text=""))

    assert 4000 < len(embed.description) <= 4096
    assert embed.description.endswith("…")
    assert fields(embed)["pokemon with it (500)"].endswith(", and 488 more")
    assert fits_discord_limits(embed)


# ---------------------------------------------------------------- real lookups

def test_dex_pokemon():
    entry = f.dex("galarian articuno")
    embed = dex_embed.build_embed(entry)

    assert (entry.kind, entry.name, entry.note) == ("pokemon", "articuno-galar", None)
    assert embed.title == "Articuno-Galar • #144"
    assert embed.description.startswith("*Freeze Pokémon* • legendary\n\n")
    assert embed.color.value == d.type_colors["psychic"]
    assert embed.image.url is None
    assert embed.thumbnail.url == ART_URL + "10169.png"
    assert embed.footer.text == d.footer
    assert list(fields(embed)) == ["type", "height & weight", "abilities", "base stats", "weaknesses", "resistances", "immunities", "egg groups", "gender", "catch rate"]
    assert fields(embed) | {"base stats": None} == {
        "type": "Psychic / Flying",
        "height & weight": "1.7 m / 50.9 kg",
        "abilities": "Competitive",
        "base stats": None,
        "weaknesses": "Dark, Electric, Ghost, Ice, Rock",
        "resistances": "**Fighting**, Grass, Psychic",
        "immunities": "Ground",
        "egg groups": "Undiscovered",
        "gender": "genderless",
        "catch rate": "3",
    }
    assert fields(embed)["base stats"] == "```\n" + "\n".join((
        "HP       90 █████░░░░░░░░░░",
        "ATK      85 █████░░░░░░░░░░",
        "DEF      85 █████░░░░░░░░░░",
        "SP. ATK 125 ███████░░░░░░░░",
        "SP. DEF 100 ██████░░░░░░░░░",
        "SPEED    95 ██████░░░░░░░░░",
        "BST     580",
    )) + "\n```"
    assert fits_discord_limits(embed)


@pytest.mark.parametrize('query, title, evolution', [
    ('garchomp', "Garchomp • #445", "Gible → Gabite → **Garchomp**"),
    ('445', "Garchomp • #445", "Gible → Gabite → **Garchomp**"),
    ('chomp', "Garchomp • #445", "Gible → Gabite → **Garchomp**"),
    ('mega alakazam', "Alakazam-Mega • #65", "Abra → Kadabra → **Alakazam**"),
    ('landorus', "Landorus-Incarnate • #645", None),
    ('morpeko', "Morpeko-Full-Belly • #877", None),
])
def test_dex_finds_pokemon_the_same_way_dt_does(query: str, title: str, evolution: str | None):
    entry = f.dex(query)
    embed = dex_embed.build_embed(entry)

    assert embed.title == title
    assert fields(embed).get("evolution line") == evolution
    assert entry.note is None
    assert entry.text == f.dt(query)
    assert fits_discord_limits(embed)


def test_dex_fuzzy_match_keeps_the_note_out_of_the_embed():
    entry = f.dex("diance")

    assert entry.note == "ummmm... \"diance\"? perhaps you meant diancie?"
    assert entry.text.startswith(entry.note + "\n")
    assert dex_embed.build_embed(entry).title == "Diancie • #719"


def test_dex_unknown_query():
    assert f.dex("qwertyuiopasdf") == "i don't know what \"qwertyuiopasdf\" is... check your spelling?"
    assert f.dex("1026") == "i don't know what \"1026\" is... check your spelling?"


def test_dex_move():
    embed = dex_embed.build_embed(f.dex("quick attack"))

    assert embed.title == "Quick Attack"
    assert embed.color.value == d.type_colors["normal"]
    assert embed.description
    assert fields(embed) == {
        "type": "Normal",
        "category": "Physical",
        "power": "40",
        "accuracy": "100%",
        "pp": "30",
        "priority": "+1",
        "generation": "1",
        "target": "Selected Pokemon",
    }
    assert fits_discord_limits(embed)


def test_dex_status_move_has_dashes_for_power_and_accuracy():
    embed = dex_embed.build_embed(f.dex("swords dance"))

    assert (fields(embed)["power"], fields(embed)["accuracy"], fields(embed)["priority"]) == ("-", "-", "0")


def test_dex_ability():
    embed = dex_embed.build_embed(f.dex("blaze"))
    holders = next(value for name, value in fields(embed).items() if name.startswith("pokemon with it ("))

    assert embed.title == "Blaze"
    assert "Fire" in embed.description
    assert fields(embed)["generation"] == "3"
    assert holders.startswith("Charmander, Charmeleon, Charizard, ")
    assert fits_discord_limits(embed)


def test_dex_item():
    embed = dex_embed.build_embed(f.dex("leftovers"))

    assert embed.title == "Leftovers"
    assert "1/16" in embed.description
    assert fields(embed) == {"category": "Held Items", "fling power": "10"}
    assert embed.thumbnail.url.endswith("/items/leftovers.png")
    assert embed.image.url is None
    assert fits_discord_limits(embed)


def test_dex_long_ability_fits_discord_limits():
    assert fits_discord_limits(dex_embed.build_embed(f.dex("mold breaker")))


def test_dex_survives_losing_the_species_and_evolution_requests(monkeypatch):
    '''Only the Pokemon itself is needed. If the extra requests fail, their parts are left out.'''

    real_get = Fetcher.get

    def flaky_get(url: str):
        if "pokemon-species" in url or "evolution-chain" in url:
            raise requests.ConnectionError("pokeapi hiccup")
        return real_get(url)

    monkeypatch.setattr(Fetcher, "get", staticmethod(flaky_get))

    entry = f.dex("garchomp")
    embed = dex_embed.build_embed(entry)

    assert (entry.species, entry.evolution) == (None, None)
    assert embed.title == "Garchomp • #445"
    assert embed.description is None
    assert list(fields(embed)) == ["type", "height & weight", "abilities", "base stats", "weaknesses", "resistances", "immunities"]
    assert embed.thumbnail.url == ART_URL + "445.png"


def test_dex_survives_losing_only_the_evolution_request(monkeypatch):
    real_get = Fetcher.get

    def flaky_get(url: str):
        if "evolution-chain" in url:
            raise requests.Timeout("pokeapi is slow")
        return real_get(url)

    monkeypatch.setattr(Fetcher, "get", staticmethod(flaky_get))

    entry = f.dex("garchomp")
    names = fields(dex_embed.build_embed(entry))

    assert entry.species is not None and entry.evolution is None
    assert "evolution line" not in names
    assert names["egg groups"] == "Monster, Dragon"


def test_dex_still_fails_when_the_pokemon_itself_cant_be_fetched(monkeypatch):
    def broken_get(url, **kwargs):
        raise requests.ConnectionError("pokeapi is down")

    monkeypatch.setattr(Fetcher.session, "get", broken_get)

    with pytest.raises(requests.ConnectionError):
        f.dex("snom")


# ---------------------------------------------------------------- the command

def test_dex_command_sends_an_embed(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("dex")(ctx, query="snom"))

    assert len(ctx.sent) == 1
    content, kwargs = ctx.sent[0]
    assert content is None
    assert list(kwargs) == ["embed"]
    assert kwargs["embed"].title == "Snom • #872"
    assert fields(kwargs["embed"])["evolution line"] == "**Snom** → Frosmoth"


def test_dex_command_says_what_it_guessed_above_the_embed(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("dex")(ctx, query="mega alakasham"))

    content, kwargs = ctx.sent[0]
    assert content == "ummmm... \"mega alakasham\"? perhaps you meant alakazam-mega?"
    assert kwargs["embed"].title == "Alakazam-Mega • #65"


def test_dex_command_falls_back_to_dt_text_without_embed_permission(marnie):
    ctx = FakeCtx(embed_links=False)

    asyncio.run(marnie.bot.get_command("dex")(ctx, query="snom"))

    assert ctx.sent == [(f.dt("snom"), {})]


def test_dex_command_with_an_unknown_query(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("dex")(ctx, query="qwertyuiopasdf"))

    assert ctx.sent == [("i don't know what \"qwertyuiopasdf\" is... check your spelling?", {})]


def test_dex_command_with_no_query(marnie):
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("dex")(ctx, query=None))

    assert len(ctx.sent) == 1
    assert ctx.sent[0][0].startswith("how can i do ``!dex`` on **nothing**?")
    assert ctx.sent[0][1] == {}
