import pokedex as pd, item_list as il, move_list as ml, ability_list as al

# help command
help = "!dt {query} - Returns information on Pokemon, Pokemon abilities, Pokemon items, or Pokemon moves.\n" \
       "!pick {args...} - Selects a random option given a list of options.\n" \
       "!randmon - Returns a random Pokemon." \
       "!muted - lists all timed out server members and the amount of time they are timed out for."

# stat names
stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]

# urls
base_url = "https://pokeapi.co/api/v2"
poke_url = f"{base_url}/pokemon/"
item_url = f"{base_url}/item/"
move_url = f"{base_url}/move/"
ability_url = f"{base_url}/ability/"

# categories
generation = "Generation"
type = "Type"

# thresholds
poke_threshold = 80
item_threshold = 70
ability_threshold = 70
move_threshold = 70

#collections
pokemon = pd.Pokedex()
items = il.ItemList()
moves = ml.MoveList()
abilities = al.AbilityList()

# modifiers
modifiers = ("hisui", "mega", "primal", "origin", "galar", "alola")

# colors
colors = {
    "galarian": "galar",
    "alolan": "alola",
    "hisuian": "hisui",
}

col_key = colors.keys()

# aliases
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

# the line created in responses
line_length = 35
hr = '-' * line_length

# placeholder for moves with a chance for secondary effect
placeholder = "$effect_chance%"

# system language, english by default
language = "en"