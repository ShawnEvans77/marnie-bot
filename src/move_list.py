import pandas, list, thresholds

class MoveList(list.List):
    '''The move list stores moves from all Pokemon Games.'''
    
    def __init__(self):
        super().__init__('assets/moves.csv', thresholds.move_threshold)

    def get_accuracy(self, move: str) -> str:
        '''Returns the accuracy of the input move it has one. If the move has no accuracy, like Swords Dance, this function returns
        None.'''

        return self.df[self.df['identifier'] == move]['accuracy'].values[0]

    def get_generation(self, move: str) -> str:
        '''Returns the generation the input move originated from.'''
        
        return self.df[self.df['identifier'] == move]['generation_id'].values[0]
    
    def get_power(self, move: str) -> str:
        '''Returns the power of the input move.'''

        return self.df[self.df['identifier'] == move]['power'].values[0]
    
    def get_pp(self, move: str) -> str:
        '''Returns the amount of PP the input move has.'''

        return int(self.df[self.df['identifier'] == move]['pp'].values[0])