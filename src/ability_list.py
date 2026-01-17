import pandas
from thefuzz import fuzz
import list as l

class AbilityList(l.List):
    '''The Ability List stores abilities from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determing if an ability exists in the Pokemon games.
        list - A list of abilities from all Pokemon games.  
    '''

    THRESHOLD = 70

    def __init__(self):
        super().__init__(pandas.read_csv('assets/abilities.csv'), AbilityList.THRESHOLD)

    def get_generation(self, ability:str)->str:
        '''Given an ability, return the generation it comes from as a string.'''
        
        return int(self.df[self.df['identifier'] == ability]['generation_id'].values[0])