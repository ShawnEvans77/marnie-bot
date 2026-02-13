import pandas, list, thresholds

class ItemList(list.List):
    '''The Item List stores all items from all Pokemon Games.'''

    def __init__(self):
        super().__init__(pandas.read_csv('assets/items.csv'), thresholds.item_threshold)