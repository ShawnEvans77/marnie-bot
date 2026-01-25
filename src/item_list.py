import pandas, list as l, constants

class ItemList(l.List):
    '''The Item List stores all items from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determining if an item exists in the Pokemon games.
        list - A list of items from all Pokemon games.  
    '''

    def __init__(self):
        super().__init__(pandas.read_csv('assets/items.csv'), constants.item_threshold)