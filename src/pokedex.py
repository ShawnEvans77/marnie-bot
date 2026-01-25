import pandas
import list as l

POKEDEX_THRESHOLD = 80

class Pokedex(l.List):
    '''The Pokedex stores abilities from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determing if a Pokemon exists in the Pokemon games.
        list - A list of all Pokemon.
        num_pokemon - The number of Pokemon that exist in all the games.
    '''

    def __init__(self):
        super().__init__(pandas.read_csv('assets/pokemon.csv'), POKEDEX_THRESHOLD)
        self.num_pokemon = len(self.list) + 1

    def flavor_exists(self, pokemon: str) -> bool:
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
    
        if not num_str.isnumeric(): return None
        num = int(num_str)
        if num < 1 or num > self.num_pokemon: return None
        return self.df[self.df['id'] == num]['identifier'].values[0]
    
    def get_species_id(self, pokemon: str) -> str:
        '''Returns the national dex number of the input Pokemon.'''
        
        return self.df[self.df['identifier'] == pokemon]['species_id'].values[0]