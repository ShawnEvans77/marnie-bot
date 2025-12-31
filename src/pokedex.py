import pandas
import numpy
from thefuzz import fuzz

class Pokedex:
    '''
    The PokeDex class is an abstraction of a Pandas Table containing information on all of the Pokemon.

    Attributes:
        THRESHOLD (int) - A crucial variable that assists our fuzzy matching algorithim. The higher it is, the more precise
        queries have to be for the 'did you mean this Pokemon' suggestion to work. 
    '''

    THRESHOLD = 80

    def __init__(self):
        self.df = pandas.read_csv('assets/pokemon.csv')
        self.list = self.df['identifier'].values.tolist()
        self.dex_numbers = set(self.df['species_id'].values.tolist())
        self.num_pokemon = len(self.list) + 1

    def exists(self, pokemon):
        '''Returns if the input Pokemon exists, done without magic method dunder.'''
        return pokemon.lower() in self.list
    
    def __contains__(self, pokemon):
        '''Returns if the input Pokemon exists, magic method that allows for interaction with Python in operator.'''
        return pokemon.lower() in self.list
    
    def flavor_exists(self, pokemon):
        '''Returns if the list contains a flavor of the input Pokemon. Meaning, if user queries for 'Aegislash', 
        I still want the bot to return 'Aegislas'''

        for listmon in self.list:
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return True
            
        return False
    
    def flavor(self, pokemon):
        '''I return the closest flavor of a "bare" Pokemon with forms.'''

        for listmon in self.list:
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return listmon
            
        return None

    def close_match(self, incorrect) -> str:
        '''Returns the closest match to the input string. Useful for situations where the user mistypes a Pokemon.'''

        closest_val = 0
        closest_mon = None

        for pokemon in self.list:

            comparison = fuzz.ratio(incorrect.lower(), pokemon)

            if comparison > closest_val and comparison > Pokedex.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), pokemon)
                closest_mon = pokemon

        return closest_mon
    
    def by_number(self, num_str: str) -> str:
        '''Returns a Pokemon based on its dex number. Returns none if input string is not numeric or out of bounds.'''
    
        if not num_str.isnumeric():
            return None
        
        num = int(num_str)

        if num < 1 or num > self.num_pokemon:
            return None
        
        return self.df[self.df['id'] == num]['identifier'].values[0]