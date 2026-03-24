from ..abstracted import list
from ...constants import folders, thresholds

class ItemList(list.List):
    '''The Item List stores all items from all Pokemon Games.'''

    def __init__(self):
        super().__init__(f'{folders.asset_folder}/items.csv', thresholds.item_threshold)