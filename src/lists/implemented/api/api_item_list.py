from ...abstracted import list
from ....constants.files import filenames, folders
from ....constants.output import thresholds

class ItemList(list.List):
    '''The Item List stores all items from all Pokemon Games.'''

    def __init__(self):
        super().__init__(f'{folders.asset}/{folders.csv}/{filenames.item_csv}', thresholds.item_threshold)