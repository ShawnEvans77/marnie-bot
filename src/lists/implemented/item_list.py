from ..abstracted import list
from ...constants import filenames, folders, thresholds

class ItemList(list.List):
    '''The Item List stores all items from all Pokemon Games.'''

    def __init__(self):
        super().__init__(f'{folders.asset}/{folders.csv}/{filenames.item_csv}', thresholds.item_threshold)