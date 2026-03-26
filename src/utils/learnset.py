from ..constants.files import filenames, folders
from ..constants.output import generations
from ..constants.structs.objects import api_moves, api_pokemon, show_moves, show_pokemon
import json

class LearnSet:
    '''The LearnSet class helps us determine if it is possible for a Pokemon to learn a move.'''

    def __init__(self):

        with open(f"{folders.asset}/{folders.json}/{filenames.learnset_json}", "r") as l:
            self.learn_table = json.load(l)

    @staticmethod
    def reverse_sanitize(query: str, struct) -> str:
        '''For printing out moves nicer.'''

        for item in struct:
            if query == item.replace("-", ""):
                return item.replace("-", " ").title()
            
        return query.title()
    
    @staticmethod
    def sanitize(query: str) -> str:
        '''Removes trailing whitespace, removes central whitespace, sets everything to lowercase, removes dashes.'''

        return query.strip().lower().replace("-", "").replace(" ", "")
     
    def move_answer(self, pokemon: str, move: str, gen: str) -> str:

        gen_num = gen[3]

        learnable = self.learn_table[pokemon]['learnset']

        return f"in gen {gen_num}, {LearnSet.reverse_sanitize(pokemon, api_pokemon)} {"**can**" if (move in learnable.keys() and any(gen_num in move_data for move_data in learnable[move])) else "**cannot**"} learn {LearnSet.reverse_sanitize(move, api_moves)}."
    
    def learn(self, pokemon: str, move: str, gen: str = "gen9") -> str:
        '''Returns a string stating if the given Pokemon can learn the given move.'''

        if gen not in generations.gen_tuple:
            return "generation must be in the form gen# where # is the generation number you want. ex: gen9"

        pokemon = LearnSet.sanitize(pokemon)
        move = LearnSet.sanitize(move)

        if pokemon in show_pokemon and move in show_moves:
            return self.move_answer(pokemon, move, gen)
        
        note = ""

        func_map = {show_pokemon: [pokemon, api_pokemon], show_moves: [move, api_moves]}
        
        for k, v in func_map.items():
            if closest := k.close_match(v[0]):
                note += f"idk what {v[0]} is so imma guess you meant {LearnSet.reverse_sanitize(closest, v[1])}...\n"
                func_map[k][0] = closest

        pokemon, move = func_map[show_pokemon][0], func_map[show_moves][0]

        if pokemon in show_pokemon and move in show_moves:
            return note + "\n" + self.move_answer(pokemon, move, gen)
        
        error = ""

        if pokemon not in show_pokemon:
            error += f"i don't think {pokemon} is a pokemon... check your spelling?"

        error += "\n" if len(error) != 0 else ""

        if move not in show_moves:
            error += f"i don't think {move} is a move... check your spelling?"

        return error