'''Matrix representing the weaknesses and resistances of all eighteen types.'''

import src.constants.types.type_map as tm

num_types = 18

normal_dmg = 1.0
super_dmg = 2.0
resist_dmg = 0.5
no_dmg = 0.0

# Each attacking type, then the defending types it doesn't hit for normal damage.
matchups = {
    "normal": {"rock": resist_dmg, "ghost": no_dmg, "steel": resist_dmg},
    "fire": {"fire": resist_dmg, "water": resist_dmg, "grass": super_dmg, "ice": super_dmg, "bug": super_dmg,
             "rock": resist_dmg, "dragon": resist_dmg, "steel": super_dmg},
    "water": {"fire": super_dmg, "water": resist_dmg, "grass": resist_dmg, "ground": super_dmg, "rock": super_dmg,
              "dragon": resist_dmg},
    "grass": {"fire": resist_dmg, "water": super_dmg, "grass": resist_dmg, "poison": resist_dmg, "ground": super_dmg,
              "flying": resist_dmg, "bug": resist_dmg, "rock": super_dmg, "dragon": resist_dmg, "steel": resist_dmg},
    "electric": {"water": super_dmg, "grass": resist_dmg, "electric": resist_dmg, "ground": no_dmg, "flying": super_dmg,
                 "dragon": resist_dmg},
    "ice": {"fire": resist_dmg, "water": resist_dmg, "grass": super_dmg, "ice": resist_dmg, "ground": super_dmg,
            "flying": super_dmg, "dragon": super_dmg, "steel": resist_dmg},
    "fighting": {"normal": super_dmg, "ice": super_dmg, "poison": resist_dmg, "flying": resist_dmg, "psychic": resist_dmg,
                 "bug": resist_dmg, "rock": super_dmg, "ghost": no_dmg, "dark": super_dmg, "steel": super_dmg,
                 "fairy": resist_dmg},
    "poison": {"grass": super_dmg, "poison": resist_dmg, "rock": resist_dmg, "ghost": resist_dmg, "steel": no_dmg,
               "fairy": super_dmg},
    "ground": {"fire": super_dmg, "grass": resist_dmg, "electric": super_dmg, "poison": super_dmg, "flying": no_dmg,
               "bug": resist_dmg, "rock": super_dmg, "steel": super_dmg},
    "flying": {"grass": super_dmg, "electric": resist_dmg, "fighting": super_dmg, "bug": super_dmg, "rock": resist_dmg,
               "steel": resist_dmg},
    "psychic": {"fighting": super_dmg, "poison": super_dmg, "psychic": resist_dmg, "dark": no_dmg, "steel": resist_dmg},
    "bug": {"fire": resist_dmg, "grass": super_dmg, "fighting": resist_dmg, "poison": resist_dmg, "flying": resist_dmg,
            "psychic": super_dmg, "ghost": resist_dmg, "dark": super_dmg, "steel": resist_dmg, "fairy": resist_dmg},
    "rock": {"fire": super_dmg, "ice": super_dmg, "fighting": resist_dmg, "ground": resist_dmg, "flying": super_dmg,
             "bug": super_dmg, "steel": resist_dmg},
    "ghost": {"normal": no_dmg, "psychic": super_dmg, "ghost": super_dmg, "dark": resist_dmg},
    "dragon": {"dragon": super_dmg, "steel": resist_dmg, "fairy": no_dmg},
    "dark": {"fighting": resist_dmg, "psychic": super_dmg, "ghost": super_dmg, "dark": resist_dmg, "fairy": resist_dmg},
    "steel": {"fire": resist_dmg, "water": resist_dmg, "electric": resist_dmg, "ice": super_dmg, "rock": super_dmg,
              "steel": resist_dmg, "fairy": super_dmg},
    "fairy": {"fire": resist_dmg, "fighting": super_dmg, "poison": resist_dmg, "dragon": super_dmg, "dark": super_dmg,
              "steel": resist_dmg},
}

# [attacker][defender]
type_matrix = [[normal_dmg] * num_types for _ in range(num_types)]

for attacker, defenders in matchups.items():
    for defender, damage in defenders.items():
        type_matrix[tm.t_map[attacker]][tm.t_map[defender]] = damage
