import pandas
import numpy
from thefuzz import fuzz
import list as l

class Pokedex(l.List):
    '''The Pokedex stores all moves from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of all Pokemon from all Pokemon games.  
    '''
    THRESHOLD = 80

    def __init__(self):
        super().__init__(pandas.read_csv('assets/pokemon.csv'), Pokedex.THRESHOLD)
        self.num_pokemon = len(self.list) + 1

    def flavor_exists(self, pokemon: str) -> str:
        '''Returns if the list contains a flavor of the input Pokemon. Meaning, if user queries for 'Aegislash', 
        'Aegislash-Sword' is returned. Landorus queries still return 'Landorus-Incarnate.'''

        for listmon in self.list:
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return True
            
        return False
    
    def flavor(self, pokemon: str) -> str:
        '''Return the closest flavor of a "bare" Pokemon with forms.'''

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