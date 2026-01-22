import pokedex as pd, item_list as il, move_list as ml, ability_list as al

stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]

base_url = "https://pokeapi.co/api/v2"
poke_url = f"{base_url}/pokemon/"
item_url = f"{base_url}/item/"
move_url = f"{base_url}/move/"
ability_url = f"{base_url}/ability/"

pokemon = pd.Pokedex()
items = il.ItemList()
moves = ml.MoveList()
abilities = al.AbilityList()

modifiers = ("hisui", "mega", "primal", "origin", "galar", "alola")

alias = {
    "zard": "charizard",
    "fridge": "rotom-frost",
    "lando": "landorus-incarnate",
    "landot": "landorus-therian",
    "lando-t": "landorus-incarnate",
    "mark": "ludicolo",
    "trump": "gumshoos",
    "kamala": "komala",
    "biden": "musharna",
    "perc": "scrafty-mega",
    "itami": "snorlax",
}

LINE_LENGTH = 35
HR = '-' * LINE_LENGTH

placeholder = "$effect_chance%"