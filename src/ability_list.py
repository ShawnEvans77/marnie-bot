import pandas
from thefuzz import fuzz
import list as l

ABILITY_THRESHOLD = 70

class AbilityList(l.List):
    '''The Ability List stores abilities from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determining if an ability exists in the Pokemon games.
        list - A list of abilities from all Pokemon games.  
    '''

    def __init__(self):
        super().__init__(pandas.read_csv('assets/abilities.csv'), ABILITY_THRESHOLD)

    def get_generation(self, ability:str)->int:
        '''Given an ability, return the generation it comes from as a string.'''
        
        return int(self.df[self.df['identifier'] == ability]['generation_id'].values[0])