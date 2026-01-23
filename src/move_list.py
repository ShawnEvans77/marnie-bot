import pandas
import list as l

MOVE_THRESHOLD = 70

class MoveList(l.List):
    '''The move list stores moves from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determining if a Pokemon exists in the Pokemon games.
        list - A list of all Pokemon.
        num_pokemon - The number of Pokemon that exist in all the games.
    '''
    
    def __init__(self):
        super().__init__(pandas.read_csv('assets/moves.csv'), MOVE_THRESHOLD)

    def get_accuracy(self, move:str) -> int:
        '''Returns the accuracy of the input move it has one. If the move has no accuracy, like Swords Dance, this function returns
        None.'''

        try: 
            return int(self.df[self.df['identifier'] == move]['accuracy'].values[0])
        except ValueError:
            return None

    def get_generation(self, move:str)->int:
        '''Returns the generation the input move originated from.'''
        return int(self.df[self.df['identifier'] == move]['generation_id'].values[0])
    
    def get_power(self, move:str)->int:
        '''Returns the power of the input move.'''

        try:
            return int(self.df[self.df['identifier'] == move]['power'].values[0])
        except ValueError:
            return None
    
    def get_pp(self, move:str) -> int:
        '''Returns the amount of PP the input move has.'''

        return int(self.df[self.df['identifier'] == move]['pp'].values[0])