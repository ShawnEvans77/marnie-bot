import pandas
from thefuzz import fuzz
import list as l

class AbilityList(l.List):
    '''The Ability List stores all abilities from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of abilities from all Pokemon games.  
    '''
    
    THRESHOLD = 70

    def __init__(self):
        super().__init__(pandas.read_csv('assets/abilities.csv'), AbilityList.THRESHOLD)

    def get_generation(self, ability:str)->str:
        '''Given an ability, return the generation it comes from.'''
        return int(self.df[self.df['identifier'] == ability]['generation_id'].values[0])