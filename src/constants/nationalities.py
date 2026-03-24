'''Helps convert nationality queries like Galarian into a form PokeAPI can parse.'''

nat_map = {
    "galarian": "galar",
    "alolan": "alola",
    "hisuian": "hisui",
}

nat_key = nat_map.keys()