from ..constants.files import filenames, folders
from ..constants.structs.objects import api_moves, show_moves, show_pokemon
import json

class LearnSet:
    '''The LearnSet class helps us determine if it is possible for a Pokemon to learn a move.'''

    def __init__(self):

        with open(f"{folders.asset}/{folders.json}/{filenames.learnset_json}", "r") as l:
            self.learn_table = json.load(l)
    
    def reverse_sanitize(query: str):
        '''For printing out moves nicer.'''

        for mon in api_moves:
            if query == mon.replace("-", ""):
                return mon.replace("-", " ").title()
            
        return mon
    
    def sanitize(query: str):
        '''Removes trailing whitespace, removes central whitespace, sets everything to lowercase, removes dashes.'''

        return query.strip().lower().replace("-", "").replace(" ", "")
    
    def move_answer(self, pokemon: str, move: str) -> str:

        learnable = self.learn_table[pokemon]['learnset']

        return f"in gen 9, {pokemon} {"can" if (move in learnable.keys() and "9" in learnable[move][0]) else "cannot"} learn {LearnSet.reverse_sanitize(move)}"

    def learn(self, pokemon: str, move: str):
        '''Returns a string stating if the given Pokemon can learn the given move.'''
        pokemon = LearnSet.sanitize(pokemon)
        move = LearnSet.sanitize(move)

        if (pokemon in show_pokemon) and (move in show_moves):
            return self.move_answer(pokemon, move)
        
        note = ""

        func_map = {
                    show_pokemon: (copy_mon := pokemon), 
                    show_moves:   (copy_move := move)
                    }
        
        for k, v in func_map.items():
            if closest := k.close_match(v):
                note += f"idk what {v} is so imma guess you meant {closest}...\n"
                func_map[k] = closest

        new_mon, new_move = func_map[show_pokemon], func_map[show_moves]

        if ((pokemon != new_mon) and (move in show_moves)):
        # or ((move != copy_move) and (pokemon in show_moves)) or ((move != copy_move) and (pokemon != copy_mon)):
            return note + "\n" + self.move_answer(new_mon, move)

        # if closest := show_pokemon.close_match(pokemon):
        #     note += f"idk what {pokemon} is so imma assume you meant {closest}\n"
        
        # if closest := show_moves.close_match(pokemon):
        #     note += f"idk what {move} is so imma assume you meant {closest}\n"

        # if pokemon not in show_pokemon:
        #     return f"i don't think {pokemon} is a pokemon... check your spelling?"
        
        # if move not in show_moves:
        #     return f"i don't think {move} is a move... check your spelling?"
        



        # return f"in gen 9, {pokemon} {"can" if (move in learnable.keys() and "9" in learnable[move][0]) else "cannot"} learn {LearnSet.reverse_sanitize(move)}"  
    
x = LearnSet()

print(x.learn("pykachu", "flamethrower"))