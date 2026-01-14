import pandas
import numpy
from thefuzz import fuzz
import list as l

class Pokedex(l.List):
    '''
    The PokeDex class is an abstraction of a Pandas Table containing information on all of the Pokemon.

    Attributes:
        THRESHOLD (int) - A crucial variable that assists our fuzzy matching algorithim. The higher it is, the more precise
        queries have to be for the 'did you mean this Pokemon' suggestion to work. 
    '''
    THRESHOLD = 80

    def __init__(self):
        super().__init__(pandas.read_csv('assets/pokemon.csv'), Pokedex.THRESHOLD)
        self.num_pokemon = len(self.list) + 1

    def flavor_exists(self, pokemon: str) -> str:
        '''Returns if the list contains a flavor of the input Pokemon. Meaning, if user queries for 'Aegislash', 
        I still want the bot to return 'Aegislash-Sword'. Landorus queries still return 'Landorus-Incarnate.'''

        for listmon in self.list:
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return True
            
        return False
    
    def flavor(self, pokemon: str) -> str:
        '''I return the closest flavor of a "bare" Pokemon with forms.'''

        for listmon in self.list:
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return listmon
            
        return None

    def by_number(self, num_str: str) -> str:
        '''Returns a Pokemon based on its dex number. Returns none if input string is not numeric or out of bounds.'''
    
        if not num_str.isnumeric():
            return None
        
        num = int(num_str)

        if num < 1 or num > self.num_pokemon:
            return None
        
        return self.df[self.df['id'] == num]['identifier'].values[0]