import pandas, list as l, thresholds

class AbilityList(l.List):
    '''The Ability List stores abilities from all Pokemon Games. '''

    def __init__(self):
        super().__init__(pandas.read_csv('assets/abilities.csv'), thresholds.ability_threshold)

    def get_generation(self, ability: str) -> int:
        '''Given an ability, return the generation it comes from as a string.'''
        
        return int(self.df[self.df['identifier'] == ability]['generation_id'].values[0])