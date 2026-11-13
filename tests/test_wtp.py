import asyncio
from io import BytesIO
from types import SimpleNamespace

import discord
import pytest
from PIL import Image

from src.utils import wtp_round as wtp


def sprite_png(transparent: bool = True) -> bytes:
    '''A 96x96 picture with a red 20x40 rectangle on a transparent (or solid) background.'''

    image = Image.new("RGBA", (96, 96), (0, 0, 0, 0) if transparent else (255, 255, 255, 255))
    image.paste((255, 0, 0, 255), (30, 20, 50, 60))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_round(identifier: str, species: str) -> dict:
    return wtp.build_round(identifier, species, sprite_png())


@pytest.mark.parametrize('identifier, species, guess', [
    ('landorus-therian', 'landorus', 'landorus'),
    ('landorus-therian', 'landorus', 'Landorus-Therian'),
    ('landorus-therian', 'landorus', 'landorustherian'),
    ('landorus-therian', 'landorus', 'landorus therian'),
    ('landorus-therian', 'landorus', 'landorus-incarnate'),
    ('landorus-therian', 'landorus', 'lando'),
    ('landorus-therian', 'landorus', '  LANDORUS!  '),
    ('landorus-therian', 'landorus', 'landorous'),
    ('alakazam-mega', 'alakazam', 'alakazam'),
    ('alakazam-mega', 'alakazam', 'alakazammega'),
    ('alakazam-mega', 'alakazam', 'alakazam-mega'),
    ('alakazam-mega', 'alakazam', 'mega alakazam'),
    ('alakazam-mega', 'alakazam', 'alakazm'),
    ('alakazam', 'alakazam', 'mega alakazam'),
    ('zapdos-galar', 'zapdos', 'galarian zapdos'),
    ('mr-mime', 'mr-mime', 'Mr. Mime'),
    ('mr-mime', 'mr-mime', 'mrmime'),
    ('mr-mime-galar', 'mr-mime', 'mr mime'),
    ('ho-oh', 'ho-oh', 'hooh'),
    ('farfetchd', 'farfetchd', "Farfetch'd"),
    ('flabebe', 'flabebe', 'Flabébé'),
    ('nidoran-f', 'nidoran-f', 'nidoran'),
    ('charizard-mega-x', 'charizard', 'zard'),
    ('pikachu', 'pikachu', 'pikachu-rock-star'),
])
def test_guess_is_accepted(identifier: str, species: str, guess: str):
    assert wtp.guess_matches(guess, make_round(identifier, species)) is True


@pytest.mark.parametrize('identifier, species, guess', [
    ('landorus-therian', 'landorus', 'tornadus'),
    ('landorus-therian', 'landorus', 'thundurus-therian'),
    ('landorus-therian', 'landorus', ''),
    ('landorus-therian', 'landorus', '   '),
    ('landorus-therian', 'landorus', '!!!'),
    ('landorus-therian', 'landorus', 'i think it is landorus but i am not sure at all honestly'),
    ('kabutops', 'kabutops', 'kabuto'),
    ('nidorino', 'nidorino', 'nidorina'),
    ('pidgeotto', 'pidgeotto', 'pidgeot'),
    ('porygon2', 'porygon2', 'porygonz'),
    ('porygon2', 'porygon2', 'porygon'),
    ('mew', 'mew', 'mewtwo'),
    ('pikachu', 'pikachu', 'pichu'),
    ('alakazam-mega', 'alakazam', 'kadabra'),
    ('alakazam-mega', 'alakazam', 'mega'),
])
def test_guess_is_rejected(identifier: str, species: str, guess: str):
    assert wtp.guess_matches(guess, make_round(identifier, species)) is False


def test_round_answer_is_the_species_not_the_form():
    wtp_round = make_round('landorus-therian', 'landorus')

    assert wtp_round["name"] == "Landorus"
    assert wtp_round["species_id"] == "645"


def test_images_are_a_black_silhouette_and_a_colored_reveal():
    silhouette_png, reveal_png = wtp.images(sprite_png())
    silhouette, reveal = Image.open(BytesIO(silhouette_png)), Image.open(BytesIO(reveal_png))
    size = wtp.CANVAS_SIZE
    background = silhouette.getpixel((0, 0))

    assert silhouette.size == reveal.size == (size, size)
    assert reveal.getpixel((0, 0)) == background != (0, 0, 0)
    assert silhouette.getpixel((size // 2, size // 2)) == (0, 0, 0)
    assert reveal.getpixel((size // 2, size // 2)) == (255, 0, 0)
    # The silhouette shows nothing but the background and black, so it gives no colors away.
    assert {color for _, color in silhouette.getcolors()} == {background, (0, 0, 0)}


@pytest.mark.parametrize('image_bytes', [
    sprite_png(transparent=False),
    b"not a picture",
])
def test_images_reject_unusable_pictures(image_bytes: bytes):
    with pytest.raises((ValueError, OSError)):
        wtp.images(image_bytes)


def test_image_url_prefers_official_artwork():
    data = {"sprites": {"front_default": "sprite.png", "other": {"official-artwork": {"front_default": "art.png"}}}}

    assert wtp.image_url(data) == "art.png"
    assert wtp.image_url({"sprites": {"front_default": "sprite.png", "other": None}}) == "sprite.png"
    assert wtp.image_url({"sprites": {"front_default": None}}) is None
    assert wtp.image_url({}) is None


# ---------------------------------------------------------------- the command

class FakeMessage:
    '''A message Marnie sent. Remembers where it sits in the channel's history.'''

    def __init__(self, log: list, content: str, delete_error: Exception | None = None):
        self.log, self.content, self.delete_error = log, content, delete_error
        self.deleted = False

    async def delete(self):
        self.log.append(("delete", self.content))
        if self.delete_error: raise self.delete_error
        self.deleted = True


class FakeTyping:
    async def __aenter__(self): return None
    async def __aexit__(self, *error): return False


class FakeCtx:
    def __init__(self, delete_error: Exception | None = None, fail_on_send: int | None = None):
        self.channel = SimpleNamespace(id=1)
        self.log, self.messages = [], []
        self.delete_error, self.fail_on_send = delete_error, fail_on_send

    def typing(self):
        return FakeTyping()

    async def send(self, content=None, **kwargs):
        if len(self.messages) + 1 == self.fail_on_send:
            raise RuntimeError("discord hiccup")

        self.log.append(("send", content))
        self.messages.append(FakeMessage(self.log, content, self.delete_error))
        return self.messages[-1]


def play_round(marnie, monkeypatch, ctx: FakeCtx, guess):
    '''Plays one round of !wtp on landorus-therian. guess is what bot.wait_for does: return a
    winning message, or raise.'''

    async def fetch_round():
        return make_round('landorus-therian', 'landorus')

    async def wait_for(event, check, timeout):
        return guess()

    monkeypatch.setattr(wtp, "fetch_round", fetch_round)
    monkeypatch.setattr(marnie.bot, "wait_for", wait_for)

    asyncio.run(marnie.bot.get_command("wtp")(ctx))


def winner():
    return SimpleNamespace(author=SimpleNamespace(mention="<@7>"))


def time_out():
    raise asyncio.TimeoutError


QUESTION = "**who's that pokemon?** type its name! you have 30 seconds."


@pytest.mark.parametrize('guess, answer', [
    (winner, "it's **Landorus**! <@7> got it!"),
    (time_out, "time's up! it's **Landorus**!"),
])
def test_wtp_deletes_the_question_and_keeps_the_answer(marnie, monkeypatch, guess, answer: str):
    ctx = FakeCtx()

    play_round(marnie, monkeypatch, ctx, guess)

    question, reveal = ctx.messages
    assert ctx.log == [("send", QUESTION), ("send", answer), ("delete", QUESTION)]
    assert question.deleted is True
    assert reveal.deleted is False
    assert marnie.bot.get_cog("WhosThatPokemon").active_channels == set()


@pytest.mark.parametrize('error', [
    discord.NotFound(SimpleNamespace(status=404, reason="Not Found"), "unknown message"),
    discord.Forbidden(SimpleNamespace(status=403, reason="Forbidden"), "missing permissions"),
])
def test_wtp_round_still_ends_if_the_question_cant_be_deleted(marnie, monkeypatch, error):
    ctx = FakeCtx(delete_error=error)

    play_round(marnie, monkeypatch, ctx, winner)

    assert ctx.log == [("send", QUESTION), ("send", "it's **Landorus**! <@7> got it!"), ("delete", QUESTION)]
    assert marnie.bot.get_cog("WhosThatPokemon").active_channels == set()


def test_wtp_deletes_the_question_even_if_the_answer_fails_to_send(marnie, monkeypatch):
    ctx = FakeCtx(fail_on_send=2)

    with pytest.raises(RuntimeError):
        play_round(marnie, monkeypatch, ctx, winner)

    assert ctx.log == [("send", QUESTION), ("delete", QUESTION)]
    assert marnie.bot.get_cog("WhosThatPokemon").active_channels == set()


def test_wtp_without_a_pokemon_has_no_question_to_delete(marnie, monkeypatch):
    async def fetch_round():
        return None

    monkeypatch.setattr(wtp, "fetch_round", fetch_round)
    ctx = FakeCtx()

    asyncio.run(marnie.bot.get_command("wtp")(ctx))

    assert ctx.log == [("send", "sorry, i couldn't find a pokemon to show right now... try ``!wtp`` again in a bit?")]
    assert ctx.messages[0].deleted is False
