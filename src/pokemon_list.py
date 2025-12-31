import pandas
import numpy
from thefuzz import fuzz

class PokemonList:

    def __init__(self):
        self.df = pandas.read_csv('assets/pokemon.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, pokemon):
        return pokemon.lower() in self.list
    
    def __contains__(self, pokemon):
        return pokemon.lower() in self.list

    def close_match(self, incorrect):
        closest = [pokemon for pokemon in self.list if fuzz.ratio(incorrect.lower(), pokemon) >= 65]
        return closest
    
    def pokemon_by_number(self, number):
        num = int(number)

        try:
            return self.df[self.df['id'] == num]['identifier'].values[0]
        except IndexError:
            return None