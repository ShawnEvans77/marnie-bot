'''Constants used when building !dex embeds.'''

default_color = 0xff76aa

type_colors = {
    "normal": 0xA8A77A,
    "fire": 0xEE8130,
    "water": 0x6390F0,
    "electric": 0xF7D02C,
    "grass": 0x7AC74C,
    "ice": 0x96D9D6,
    "fighting": 0xC22E28,
    "poison": 0xA33EA1,
    "ground": 0xE2BF65,
    "flying": 0xA98FF3,
    "psychic": 0xF95587,
    "bug": 0xA6B91A,
    "rock": 0xB6A136,
    "ghost": 0x735797,
    "dragon": 0x6F35FC,
    "dark": 0x705746,
    "steel": 0xB7B7CE,
    "fairy": 0xD685AD,
}

# PokeAPI's stat names, in the same order as formatters.stat_names.
stat_keys = ("hp", "attack", "defense", "special-attack", "special-defense", "speed")

# A full bar is the highest base stat in the games (Blissey's HP).
max_stat = 255
bar_width = 15
bar_full = "█"
bar_empty = "░"

# PokeAPI's egg group names next to the names the games use.
egg_groups = {
    "monster": "Monster",
    "water1": "Water 1",
    "water2": "Water 2",
    "water3": "Water 3",
    "bug": "Bug",
    "flying": "Flying",
    "ground": "Field",
    "fairy": "Fairy",
    "plant": "Grass",
    "humanshape": "Human-Like",
    "mineral": "Mineral",
    "indeterminate": "Amorphous",
    "ditto": "Ditto",
    "dragon": "Dragon",
    "no-eggs": "Undiscovered",
}

# PokeAPI writes generations as "generation-viii".
generations = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10}

# How many Pokemon an ability's embed names before it says "and N more".
max_ability_pokemon = 12

# Discord's limits on embed text.
description_limit = 4096
field_limit = 1024

footer = "marnie's pokedex • data from pokeapi"
no_description = "i don't have a description for this one yet, sorry..."
