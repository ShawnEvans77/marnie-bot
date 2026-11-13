'''The embed Marnie sends for !dex. The text inside it is worked out in src/utils/dex.py.

Anything PokeAPI has no data for is left out of the embed.'''

from ..constants.getters import get_objs
from ..constants.output import dex as d
from ..constants.structs import objects
from ..constants.types import type_map as tm
from ..utils import dex
from ..utils.fetcher import Fetcher
import discord


def build_embed(entry: dex.DexEntry) -> discord.Embed:
    '''Builds the embed for whatever !dex found.'''

    builders = {"pokemon": pokemon_embed, "move": move_embed, "ability": ability_embed, "item": item_embed}

    embed = builders[entry.kind](entry)
    embed.set_footer(text=d.footer)

    return embed


def add_field(embed: discord.Embed, name: str, value: str | None, inline: bool = True):
    '''Adds a field, unless there is nothing to put in it.'''

    if value:
        embed.add_field(name=name, value=dex.clip(value, d.field_limit), inline=inline)


def describe(*parts: str | None) -> str | None:
    '''Joins the parts of a description that exist. Returns None if none of them do.'''

    return dex.clip("\n\n".join(part for part in parts if part), d.description_limit) or None


def effect_description(flavor: str | None, effect: str | None) -> str:
    '''Builds the description of a move, ability, or item: the games' own description in italics,
    then PokeAPI's longer effect text if it says anything different.'''

    effect = dex.tidy(effect) if isinstance(effect, str) else None

    return describe(f"*{flavor}*" if flavor else None, None if dex.same_text(flavor, effect) else effect) or d.no_description


def type_color(type_name: str | None) -> int:
    '''Returns the colour of a type, or Marnie's pink for a type without one.'''

    return d.type_colors.get(type_name, d.default_color)


def dex_number(entry: dex.DexEntry) -> str | None:
    '''Returns a Pokemon's national dex number.'''

    if entry.name in objects.pokemon:
        return str(objects.pokemon.get_species_id(entry.name))

    number = dex.number(dex.dig(entry.species, 'id'))

    return str(number) if number is not None else None


def matchups(types: list[str]) -> list[list[str]] | None:
    '''Returns the weaknesses, resistances, and immunities of a Pokemon's types, the same way
    !weak lists them. Returns None for a type combination the type chart doesn't cover.'''

    if len(types) not in (1, 2) or any(type_name not in tm.all_types for type_name in types):
        return None

    return get_objs.weaker.build_matrix("", *types)[1]


def pokemon_embed(entry: dex.DexEntry) -> discord.Embed:
    '''A Pokemon: dex entry, types, size, abilities, stat bars, type matchups, breeding,
    evolution line, and official art.'''

    data, species = entry.data, entry.species
    types = dex.type_names(data)
    number = dex_number(entry)
    genus = dex.genus(species)

    kind = " • ".join(([f"*{genus}*"] if genus else []) + dex.tags(species))

    embed = discord.Embed(
        title=entry.name.title() + (f" • #{number}" if number else ""),
        description=describe(kind, dex.flavor_text(species)),
        color=type_color(types[0] if types else None),
    )

    add_field(embed, "type", " / ".join(type_name.title() for type_name in types))
    sizes = [(label, size) for label, size in (("height", dex.height(data)), ("weight", dex.weight(data))) if size]
    add_field(embed, " & ".join(label for label, _ in sizes), " / ".join(size for _, size in sizes))
    add_field(embed, "abilities", "\n".join(dex.title(name) + (" *(hidden)*" if hidden else "") for name, hidden in dex.abilities(data)))

    if stats := dex.stat_block(data):
        add_field(embed, "base stats", f"```\n{stats}\n```", inline=False)

    if matrix := matchups(types):
        for label, names in zip(("weaknesses", "resistances", "immunities"), matrix):
            add_field(embed, label, ", ".join(names) or "none")

    add_field(embed, "egg groups", dex.egg_groups(species))
    add_field(embed, "gender", dex.gender(species))
    add_field(embed, "catch rate", dex.catch_rate(species))
    add_field(embed, "evolution line", dex.evolution_line(entry.evolution, dex.dig(data, 'species', 'name')), inline=False)

    art, sprite = dex.art_url(data), dex.sprite_url(data)

    if art: embed.set_image(url=art)
    if sprite: embed.set_thumbnail(url=sprite)

    return embed


def move_embed(entry: dex.DexEntry) -> discord.Embed:
    '''A move: what it does and its numbers.'''

    data = entry.data
    type_name = dex.dig(data, 'type', 'name')

    embed = discord.Embed(
        title=dex.title(entry.name),
        description=effect_description(dex.flavor_text(data), Fetcher.get_move_effect(data)),
        color=type_color(type_name),
    )

    def stat(key: str, suffix: str = "") -> str:
        value = dex.number(dex.dig(data, key))
        return f"{value}{suffix}" if value is not None else "-"

    priority = dex.number(dex.dig(data, 'priority'))
    category, target = dex.dig(data, 'damage_class', 'name'), dex.dig(data, 'target', 'name')

    add_field(embed, "type", type_name.title() if isinstance(type_name, str) else None)
    add_field(embed, "category", category.title() if isinstance(category, str) else None)
    add_field(embed, "power", stat('power'))
    add_field(embed, "accuracy", stat('accuracy', "%"))
    add_field(embed, "pp", stat('pp'))
    add_field(embed, "priority", f"{priority:+g}" if priority else "0" if priority == 0 else None)
    add_field(embed, "generation", dex.generation(data))
    add_field(embed, "target", dex.title(target) if isinstance(target, str) else None)

    return embed


def ability_embed(entry: dex.DexEntry) -> discord.Embed:
    '''An ability: what it does and which Pokemon have it.'''

    data = entry.data

    embed = discord.Embed(
        title=dex.title(entry.name),
        description=effect_description(dex.flavor_text(data), Fetcher.get_effect(data)),
        color=d.default_color,
    )

    add_field(embed, "generation", dex.generation(data))

    names = [name.title() for holder in dex.items(data, 'pokemon') if isinstance(name := dex.dig(holder, 'pokemon', 'name'), str)]

    if names:
        shown = ", ".join(names[:d.max_ability_pokemon])
        hidden = len(names) - d.max_ability_pokemon
        add_field(embed, f"pokemon with it ({len(names)})", shown + (f", and {hidden} more" if hidden > 0 else ""), inline=False)

    return embed


def item_embed(entry: dex.DexEntry) -> discord.Embed:
    '''An item: what it does, with its picture.'''

    data = entry.data
    category, fling_power = dex.dig(data, 'category', 'name'), dex.number(dex.dig(data, 'fling_power'))

    embed = discord.Embed(
        title=dex.title(entry.name),
        description=effect_description(dex.flavor_text(data), Fetcher.get_effect(data)),
        color=d.default_color,
    )

    add_field(embed, "category", dex.title(category) if isinstance(category, str) else None)
    add_field(embed, "fling power", str(fling_power) if fling_power is not None else None)

    if sprite := dex.sprite_url(data):
        embed.set_thumbnail(url=sprite)

    return embed
