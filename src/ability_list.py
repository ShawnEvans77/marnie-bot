import pandas
from thefuzz import fuzz

class AbilityList:
    '''The Ability List stores all abilities from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of abilities from all Pokemon games.  
    '''

    THRESHOLD = 70

    def __init__(self):
        self.df = pandas.read_csv('assets/abilities.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, ability:str) -> str:
        '''Returns if the input ability exists in the list of abilities.'''

        return ability.lower() in self.list
    
    def __contains__(self, ability:str) -> str:
        return ability.lower() in self.list

    def close_match(self, incorrect) -> str:

        '''Returns the closest match to the input string. Useful for situations where the user mistykes an item.'''

        closest_val = 0
        closest_item = None

        for ability in self.list:

            comparison = fuzz.ratio(incorrect.lower(), ability)

            if comparison > closest_val and comparison > AbilityList.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), ability)
                closest_item = ability

        return closest_item
    
    def get_generation(self, move):
        return int(self.df[self.df['identifier'] == move]['generation_id'].values[0])