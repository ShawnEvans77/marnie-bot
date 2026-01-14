import pandas
import numpy
from thefuzz import fuzz
import list as l

class MoveList(l.List):
    '''The move List stores all moves from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of moves from all Pokemon games.  
    '''

    THRESHOLD = 70

    def __init__(self):
        super().__init__(pandas.read_csv('assets/moves.csv'), MoveList.THRESHOLD)

    def get_accuracy(self, move:str) -> int:
        '''Returns the accuracy of the input move it has one. If the move has no accuracy, like Swords Dance, this function returns
        None.'''

        try: 
            return int(self.df[self.df['identifier'] == move]['accuracy'].values[0])
        except ValueError:
            return None

    def get_generation(self, move:str)->str:
        '''Returns the generation the input move originated from.'''
        return int(self.df[self.df['identifier'] == move]['generation_id'].values[0])
    
    def get_power(self, move:str)->str:
        '''Returns the power of the input move.'''

        try:
            return int(self.df[self.df['identifier'] == move]['power'].values[0])
        except ValueError:
            return None
    
    def get_pp(self, move:str) -> str:
        '''Returns the amount of PP the input move has.'''

        return int(self.df[self.df['identifier'] == move]['pp'].values[0])