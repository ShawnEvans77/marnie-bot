import pandas
import numpy
from thefuzz import fuzz
import list as l

class ItemList(l.List):
    '''The Item List stores all items from all Pokemon Games.
    
    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determing if an item exists in the Pokemon games.
        list - A list of items from all Pokemon games.  
    '''
    THRESHOLD = 70

    def __init__(self):
        super().__init__(pandas.read_csv('assets/items.csv'), ItemList.THRESHOLD)