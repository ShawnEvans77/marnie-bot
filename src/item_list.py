import list, thresholds, constants

class ItemList(list.List):
    '''The Item List stores all items from all Pokemon Games.'''

    def __init__(self):
        super().__init__(f'{constants.asset_folder}/items.csv', thresholds.item_threshold)