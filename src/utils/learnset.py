from ..constants import filenames, folders
import json

class LearnSet:
    '''The LearnSet class helps us determine if it is possible for a Pokemon to learn a move.'''

    def __init__(self):

        with open(f"{folders.asset}/{folders.json}/{filenames.learnset_json}", "r") as l:
            self.learn_table = json.load(l)
            
        self.all_pokemon = self.learn_table.keys()

        with open(f"{folders.asset}/{folders.txt}/{filenames.move_txt}", "r") as m:
            self.all_moves = m.read()

    def sanitize(query: str):
        '''Removes trailing whitespace, removes central whitespace, sets everything to lowercase, removes dashes.'''

        return query.strip().lower().replace("-", "").replace(" ", "")

    def learn(self, pokemon: str, move: str):
        '''Returns a string stating if the given Pokemon can learn the given move.'''
        pokemon = LearnSet.sanitize(pokemon)
        move = LearnSet.sanitize(move)

        if pokemon not in self.all_pokemon:
            return f"i don't think {pokemon} is a pokemon... check your spelling?"
        
        if move not in self.all_moves:
            return f"i don't think {move} is a move... check your spelling?"
        
        learnable = self.learn_table[pokemon]['learnset']

        return f"in gen 9, {pokemon} {"can" if (move in learnable.keys() and "9" in learnable[move][0]) else "cannot"} learn {move}"  