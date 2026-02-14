import list, thresholds, constants

class AbilityList(list.List):
    '''The Ability List stores abilities from all Pokemon Games. '''

    def __init__(self):
        super().__init__(f'{constants.asset_folder}/abilities.csv', thresholds.ability_threshold)

    def get_generation(self, ability: str) -> str:
        '''Given an ability, return the generation it comes from as a string.'''
        
        return self.df[self.df['identifier'] == ability]['generation_id'].values[0]