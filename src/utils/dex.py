'''The pure logic behind !dex: turning PokeAPI's JSON into the pieces of text the embed shows.

PokeAPI data is sometimes incomplete, especially for new Pokemon and forms. Every function here
returns None (or an empty list) when the data it needs is missing or malformed, so the embed can
leave that part out instead of crashing or showing something wrong.'''

from ..constants.api import language
from ..constants.output import dex as d, formatters
from dataclasses import dataclass


@dataclass
class DexEntry:
    '''Everything !dex found for one query.

    Attributes:
        kind - "pokemon", "item", "move", or "ability".
        name - The PokeAPI name of what was found, like "alakazam-mega".
        data - PokeAPI's JSON for it.
        text - The same answer as !dt would give, for channels where Marnie can't send embeds.
        note - The "perhaps you meant" line if the query was a fuzzy match, otherwise None.
        species - A Pokemon's species JSON, or None if there isn't any.
        evolution - A Pokemon's evolution chain JSON, or None if there isn't any.
    '''

    kind: str
    name: str
    data: dict
    text: str
    note: str | None = None
    species: dict | None = None
    evolution: dict | None = None


def dig(data, *keys):
    '''Follows keys down through nested dicts. Returns None as soon as one is missing.'''

    for key in keys:
        if not isinstance(data, dict): return None
        data = data.get(key)

    return data


def items(data, key: str) -> list[dict]:
    '''Returns the dicts in the list stored under a key, or an empty list if there is no such list.'''

    value = dig(data, key)

    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def number(value) -> int | float | None:
    '''Returns the value if it is a real number, otherwise None.'''

    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def clean(text: str) -> str:
    '''Tidies game text: the games break lines (and hyphenate words) to fit their text boxes.'''

    return " ".join(text.replace("\xad\n", "").replace("\xad", "").split())


def tidy(text: str) -> str:
    '''Tidies PokeAPI's effect text for an embed. Paragraphs are kept, but PokeAPI's
    "heading, then an indented line starting with a colon" layout becomes "heading: text".'''

    lines = [" ".join(line.split()) for line in text.replace("\n:", ":").split("\n")]

    return "\n".join(lines).strip()


def same_text(first: str | None, second: str | None) -> bool:
    '''Returns if two texts say the same thing, ignoring spacing and which apostrophe is used.'''

    def plain(text: str | None) -> str:
        return clean(text or "").replace("\u2019", "'").lower()

    return plain(first) == plain(second)


def clip(text: str, limit: int) -> str:
    '''Shortens text to fit one of Discord's limits.'''

    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def title(name: str) -> str:
    '''Writes a PokeAPI name like "mold-breaker" as "Mold Breaker".'''

    return name.replace("-", " ").title()


def in_language(entries: list[dict], key: str) -> str | None:
    '''Returns the newest text stored under a key among entries written in Marnie's language.'''

    texts = [entry[key] for entry in entries
             if dig(entry, 'language', 'name') == language.curr_lang and isinstance(entry.get(key), str) and entry[key].strip()]

    return clean(texts[-1]) if texts else None


def type_names(data: dict) -> list[str]:
    '''Returns a Pokemon's types, in order.'''

    names = [dig(slot, 'type', 'name') for slot in items(data, 'types')]

    return [name for name in names if isinstance(name, str)]


def abilities(data: dict) -> list[tuple[str, bool]]:
    '''Returns a Pokemon's abilities as (name, is hidden).'''

    return [(name, bool(slot.get('is_hidden'))) for slot in items(data, 'abilities')
            if isinstance(name := dig(slot, 'ability', 'name'), str)]


def stat_bar(value: int | float) -> str:
    '''Draws one stat as a bar. Any stat above zero shows at least one block.'''

    filled = round(max(0, min(value, d.max_stat)) / d.max_stat * d.bar_width)
    if value > 0: filled = max(filled, 1)

    return d.bar_full * filled + d.bar_empty * (d.bar_width - filled)


def stat_block(data: dict) -> str | None:
    '''Returns a Pokemon's base stats as lines of "name, number, bar" with the total underneath.
    Returns None unless all six stats are there, since a partial total would be wrong.'''

    found = {dig(stat, 'stat', 'name'): number(stat.get('base_stat')) for stat in items(data, 'stats')}

    if any(found.get(key) is None for key in d.stat_keys): return None

    width = max(len(name) for name in formatters.stat_names)
    lines = [f"{name:<{width}} {found[key]:>3} {stat_bar(found[key])}" for name, key in zip(formatters.stat_names, d.stat_keys)]
    lines.append(f"{'BST':<{width}} {sum(found[key] for key in d.stat_keys):>3}")

    return "\n".join(lines)


def art_url(data: dict) -> str | None:
    '''Returns the URL of a Pokemon's official artwork.'''

    url = dig(data, 'sprites', 'other', 'official-artwork', 'front_default')

    return url if isinstance(url, str) and url else None


def sprite_url(data: dict) -> str | None:
    '''Returns the URL of a Pokemon's sprite, or of an item's picture.'''

    url = dig(data, 'sprites', 'front_default') or dig(data, 'sprites', 'default')

    return url if isinstance(url, str) and url else None


def height(data: dict) -> str | None:
    '''Returns a Pokemon's height in metres. PokeAPI stores it in tenths of a metre.'''

    value = number(dig(data, 'height'))

    return f"{value / 10:.1f} m" if value is not None and value > 0 else None


def weight(data: dict) -> str | None:
    '''Returns a Pokemon's weight in kilograms. PokeAPI stores it in tenths of a kilogram,
    and stores 0 when the games don't give one.'''

    value = number(dig(data, 'weight'))

    return f"{value / 10:.1f} kg" if value is not None and value > 0 else None


def genus(species: dict | None) -> str | None:
    '''Returns what kind of Pokemon a species is, like "Two-Sided Pokémon".'''

    return in_language(items(species, 'genera'), 'genus')


def flavor_text(json: dict | None) -> str | None:
    '''Returns the newest description the games give for a species, move, ability, or item.'''

    entries = items(json, 'flavor_text_entries')

    return in_language(entries, 'flavor_text') or in_language(entries, 'text')


def tags(species: dict | None) -> list[str]:
    '''Returns the special groups a species belongs to.'''

    labels = (('is_legendary', "legendary"), ('is_mythical', "mythical"), ('is_baby', "baby"))

    return [label for key, label in labels if dig(species, key) is True]


def gender(species: dict | None) -> str | None:
    '''Returns how often a species is male or female. PokeAPI counts females in eighths, and
    uses -1 for a species with no gender.'''

    rate = number(dig(species, 'gender_rate'))

    if rate == -1: return "genderless"
    if rate is None or not 0 <= rate <= 8: return None
    if rate == 0: return "100% ♂"
    if rate == 8: return "100% ♀"

    female = rate * 12.5

    return f"{100 - female:g}% ♂ / {female:g}% ♀"


def egg_groups(species: dict | None) -> str | None:
    '''Returns a species' egg groups, by the names the games use.'''

    names = [group.get('name') for group in items(species, 'egg_groups')]
    names = [d.egg_groups.get(name, title(name)) for name in names if isinstance(name, str)]

    return ", ".join(names) if names else None


def catch_rate(species: dict | None) -> str | None:
    '''Returns a species' catch rate, which runs from 1 to 255.'''

    rate = number(dig(species, 'capture_rate'))

    return str(rate) if rate is not None else None


def evolution_line(evolution: dict | None, current: str | None) -> str | None:
    '''Returns an evolution chain as one line, like "Snom → **Frosmoth**", with the current
    species in bold. Species at the same stage are split with slashes.
    Returns None if there is no chain, or if the species doesn't evolve at all.'''

    stages = []
    links = [link for link in [dig(evolution, 'chain')] if isinstance(link, dict)]

    # No real chain is deeper than three stages. The cap is only here so bad data can't loop forever.
    while links and len(stages) < 10:
        names = [name for link in links if isinstance(name := dig(link, 'species', 'name'), str)]
        if not names: break

        stages.append(names)
        links = [child for link in links for child in items(link, 'evolves_to')]

    if sum(len(names) for names in stages) < 2: return None

    return " → ".join(" / ".join(f"**{name.title()}**" if name == current else name.title() for name in names) for names in stages)


def generation(json: dict | None) -> str | None:
    '''Returns the number of the generation a move or ability is from.'''

    name = dig(json, 'generation', 'name')
    if not isinstance(name, str): return None

    found = d.generations.get(name.rpartition("-")[2])

    return str(found) if found is not None else None
