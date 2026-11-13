'''Building and judging rounds of !wtp (who's that pokemon).'''

from ..constants.api import urls
from ..constants.output import aliases
from ..constants.structs import objects
from .fetcher import Fetcher
from io import BytesIO
from PIL import Image
from thefuzz import fuzz
import aiohttp, asyncio, random, unicodedata

FUZZY_THRESHOLD = 85
PICK_ATTEMPTS = 5
CANVAS_SIZE = 512
SPRITE_BOX = 400
BACKGROUND = "#ff76aa"

_species_ids = None


def normalize(text: str) -> str:
    '''Lowercases text and strips accents, spaces, dashes, and punctuation,
    so "Mr. Mime", "mr-mime", and "mrmime" all compare equal.'''

    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(character for character in decomposed if character.isalnum())


def species_id_map() -> dict:
    '''Maps every normalized Pokemon name, forms included, to its species (national dex) number.'''

    global _species_ids

    if _species_ids is None:
        dex = objects.pokemon.df
        _species_ids = {normalize(identifier): species_id for identifier, species_id in zip(dex['identifier'], dex['species_id'])}

    return _species_ids


def guess_matches(guess: str, wtp_round: dict) -> bool:
    '''Returns whether a chat message names the round's Pokemon. Forms never matter:
    for Landorus-Therian, "landorus", "landorus-therian", "landorustherian", and any
    other Landorus form are all correct. Small typos are forgiven, unless the guess
    is the name of a different Pokemon.'''

    guess = guess.strip()
    if not guess or len(guess) > 40:
        return False

    sanitized = Fetcher.sanitize(guess)
    candidates = (sanitized, Fetcher.mon_sanitize(sanitized), aliases.alias_map.get(sanitized))
    answers = (wtp_round["species_key"], wtp_round["identifier_key"])
    species_ids = species_id_map()
    names_other_pokemon = False

    for candidate in candidates:
        key = normalize(candidate) if candidate else ""
        if not key:
            continue

        if key in answers:
            return True

        species_id = species_ids.get(key)
        if species_id is not None:
            if species_id == wtp_round["species_id"]:
                return True
            names_other_pokemon = True

    if names_other_pokemon:
        return False

    key = normalize(guess)
    if not key:
        return False

    return any(fuzz.ratio(key, answer) >= FUZZY_THRESHOLD for answer in answers)


def image_url(data: dict) -> str | None:
    '''Picks the picture for a round from a PokeAPI Pokemon response: official artwork, else the sprite.'''

    sprites = data.get("sprites") or {}
    artwork = ((sprites.get("other") or {}).get("official-artwork") or {}).get("front_default")
    return artwork or sprites.get("front_default")


def images(image_bytes: bytes) -> tuple[bytes, bytes]:
    '''Turns a transparent Pokemon picture into two PNGs: the black silhouette and the reveal.
    Raises ValueError if the picture is empty or has no transparent background to cut out.'''

    sprite = Image.open(BytesIO(image_bytes)).convert("RGBA")
    alpha = sprite.getchannel("A")
    bounds = alpha.getbbox()

    if bounds is None or alpha.getextrema()[0] == 255:
        raise ValueError("picture has no usable transparent background")

    sprite = sprite.crop(bounds)
    scale = min(SPRITE_BOX / sprite.width, SPRITE_BOX / sprite.height)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    # Small pixel-art sprites stay crisp with NEAREST; large artwork shrinks smoothly with LANCZOS.
    resample = Image.Resampling.NEAREST if scale >= 2 else Image.Resampling.LANCZOS
    sprite = sprite.resize(size, resample)

    left = (CANVAS_SIZE - sprite.width) // 2
    top = (CANVAS_SIZE - sprite.height) // 2
    canvas_size = (CANVAS_SIZE, CANVAS_SIZE)

    silhouette = Image.new("RGB", canvas_size, BACKGROUND)
    silhouette.paste((0, 0, 0), (left, top, left + sprite.width, top + sprite.height), sprite.getchannel("A"))

    reveal = Image.new("RGB", canvas_size, BACKGROUND)
    reveal.paste(sprite, (left, top), sprite)

    pngs = []
    for image in (silhouette, reveal):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        pngs.append(buffer.getvalue())

    return pngs[0], pngs[1]


def build_round(identifier: str, species: str, image_bytes: bytes) -> dict:
    '''Builds one round: the pictures plus everything needed to judge guesses.
    The answer is the species ("landorus"), whatever form the picture shows.'''

    silhouette, reveal = images(image_bytes)

    return {
        "identifier": identifier,
        "name": species.title(),
        "species_id": objects.pokemon.get_species_id(identifier),
        "species_key": normalize(species),
        "identifier_key": normalize(identifier),
        "silhouette": silhouette,
        "reveal": reveal,
    }


async def fetch_round() -> dict | None:
    '''Picks a random Pokemon (forms included) and builds its round.
    Some forms have no picture, so it tries a few picks. Returns None if every try fails.'''

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for _ in range(PICK_ATTEMPTS):
            identifier = random.choice(objects.pokemon.list)

            try:
                async with session.get(urls.poke_url + identifier) as response:
                    if response.status != 200:
                        continue
                    data = await response.json()

                url = image_url(data)
                if not url:
                    continue

                async with session.get(url) as response:
                    if response.status != 200:
                        continue
                    image_bytes = await response.read()

                return build_round(identifier, data["species"]["name"], image_bytes)
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError, ValueError, KeyError, TypeError):
                continue

    return None
