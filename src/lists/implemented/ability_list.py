from ..abstracted import list
from ...constants import filenames, folders, thresholds

class AbilityList(list.List):
    '''The Ability List stores abilities from all Pokemon Games. '''

    def __init__(self):
        super().__init__(f'{folders.asset}/{folders.csv}/{filenames.abil_csv}', thresholds.ability_threshold)

    def get_generation(self, ability: str) -> str:
        '''Given an ability, return the generation it comes from as a string.'''
        
        return self.df[self.df['identifier'] == ability]['generation_id'].values[0]