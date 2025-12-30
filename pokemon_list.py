import pandas
import numpy
from thefuzz import fuzz

class PokemonList:

    def __init__(self):
        self.df = pandas.read_csv('data.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, pokemon):
        return pokemon.lower() in self.list
    
    def __contains__(self, pokemon):
        return pokemon.lower() in self.list

    def close_match(self, incorrect):
        closest = [pokemon for pokemon in self.list if fuzz.ratio(incorrect.lower(), pokemon) >= 65]
        return closest