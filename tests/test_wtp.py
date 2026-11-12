from io import BytesIO

import pytest
from PIL import Image

from src.bot.marnie import Marnie
from src.constants.output import help as h


def sprite_png(transparent: bool = True) -> bytes:
    '''A 96x96 picture with a red 20x40 rectangle on a transparent (or solid) background.'''

    image = Image.new("RGBA", (96, 96), (0, 0, 0, 0) if transparent else (255, 255, 255, 255))
    image.paste((255, 0, 0, 255), (30, 20, 50, 60))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_round(identifier: str, species: str) -> dict:
    return Marnie.build_wtp_round(identifier, species, sprite_png())


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
    assert Marnie.wtp_guess_matches(guess, make_round(identifier, species)) is True


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
    assert Marnie.wtp_guess_matches(guess, make_round(identifier, species)) is False


def test_round_answer_is_the_species_not_the_form():
    wtp_round = make_round('landorus-therian', 'landorus')

    assert wtp_round["name"] == "Landorus"
    assert wtp_round["species_id"] == "645"


def test_images_are_a_black_silhouette_and_a_colored_reveal():
    silhouette_png, reveal_png = Marnie.wtp_images(sprite_png())
    silhouette, reveal = Image.open(BytesIO(silhouette_png)), Image.open(BytesIO(reveal_png))
    size = Marnie.wtp_canvas_size
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
        Marnie.wtp_images(image_bytes)


def test_image_url_prefers_official_artwork():
    data = {"sprites": {"front_default": "sprite.png", "other": {"official-artwork": {"front_default": "art.png"}}}}

    assert Marnie.wtp_image_url(data) == "art.png"
    assert Marnie.wtp_image_url({"sprites": {"front_default": "sprite.png", "other": None}}) == "sprite.png"
    assert Marnie.wtp_image_url({"sprites": {"front_default": None}}) is None
    assert Marnie.wtp_image_url({}) is None


def test_help_documents_new_commands_and_fits_in_one_discord_message():
    assert "!**wtp**" in h.command
    assert "!**top**" in h.command
    assert len(h.command) <= 2000
