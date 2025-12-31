import pandas
import numpy
from thefuzz import fuzz

class Pokedex:

    THRESHOLD = 65

    def __init__(self):
        self.df = pandas.read_csv('assets/pokemon.csv')
        self.list = self.df['identifier'].values.tolist()
        self.dex_numbers = set(self.df['species_id'].values.tolist())
        self.num_pokemon = len(self.list) + 1

    def exists(self, pokemon):
        return pokemon.lower() in self.list
    
    def __contains__(self, pokemon):
        return pokemon.lower() in self.list

    def close_match(self, incorrect) -> str:
        closest_val = 0
        closest_mon = None

        for pokemon in self.list:

            comparison = fuzz.ratio(incorrect.lower(), pokemon)

            if comparison > closest_val and comparison > Pokedex.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), pokemon)
                closest_mon = pokemon

        return closest_mon
    
    def by_number(self, num_str: str) -> str:
        if not num_str.isnumeric():
            return None
        
        num = int(num_str)

        if num < 1 or num > self.num_pokemon:
            return None
        
        return self.df[self.df['id'] == num]['identifier'].values[0]