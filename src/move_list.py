import pandas
import numpy
from thefuzz import fuzz

class MoveList:
    '''The Item List stores all items from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of items from all Pokemon games.  
    '''

    THRESHOLD = 70

    def __init__(self):
        self.df = pandas.read_csv('assets/moves.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, move:str) -> bool:
        return move.lower() in self.list
    
    def __contains__(self, move:str) -> bool:
        return move.lower() in self.list
    
    def get_accuracy(self, move):

        try: 
            return int(self.df[self.df['identifier'] == move]['accuracy'].values[0])
        except ValueError:
            return None

    def get_generation(self, move:str)->str:
        return int(self.df[self.df['identifier'] == move]['generation_id'].values[0])
    
    def get_power(self, move:str)->str:
        return int(self.df[self.df['identifier'] == move]['power'].values[0])
    
    def get_pp(self, move:str) -> str:
        return int(self.df[self.df['identifier'] == move]['pp'].values[0])

    def close_match(self, incorrect:str) -> str:

        '''Returns the closest match to the input string. Useful for situations where the user mistykes an item.'''

        closest_val = 0
        closest_item = None

        for move in self.list:

            comparison = fuzz.ratio(incorrect.lower(), move)

            if comparison > closest_val and comparison > MoveList.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), move)
                closest_item = move

        return closest_item