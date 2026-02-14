import pandas, list, thresholds, random

class Pokedex(list.List):
    '''The Pokedex stores abilities from all Pokemon Games.'''

    def __init__(self):
        super().__init__('assets/pokemon.csv', thresholds.poke_threshold)
        self.num_pokemon = self.df['species_id'].max()

    def flavor(self, pokemon: str) -> str:
        '''For Pokemon who do not exist in PokeAPI, convert them into their closest flavor,
        For example, flavor('Landorus') is 'Landorus-Incarnate'.'''

        for listmon in self.list:
            if pokemon == listmon:
                return None
            if "-" in listmon and pokemon == listmon[0:listmon.index("-")]:
                return listmon
            
        return None
    
    def get_num_pokemon(self) -> int:
        '''Returns how many Pokemon there are.'''
        
        return self.num_pokemon

    def by_number(self, num_str: str) -> str:
        '''Returns a Pokemon based on its dex number. Returns none if the input string is out of bounds.'''
    
        num = int(num_str)
        if num < 1 or num > self.num_pokemon: return None
        return self.df[self.df['id'] == num]['identifier'].values[0]
    
    def get_species_id(self, pokemon: str) -> str:
        '''Returns the national dex number of the input Pokemon.'''
        
        return self.df[self.df['identifier'] == pokemon]['species_id'].values[0]
    
    def randmon(self) -> int:
        '''Returns a random Pokemon by dex number.'''
        
        return random.randint(1, self.num_pokemon+1)