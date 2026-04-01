from ..abstracted import list
from ...constants.files import filenames, folders
from ...constants.output import thresholds

class TypeList(list.List):
    '''The Pokedex stores abilities from all Pokemon Games.'''

    def __init__(self):
        super().__init__(f'{folders.asset}/{folders.csv}/{filenames.type_csv}', thresholds.type_threshold)