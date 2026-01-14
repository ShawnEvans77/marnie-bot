import pandas
import numpy
from thefuzz import fuzz
import list as l

class ItemList(l.List):
    '''
    The Item List stores all items from all Pokemon Games. It inherits from the List class. 
    
    Attributes:
        df - A Pandas Dataframe with a list of items.    
    '''
    THRESHOLD = 70

    def __init__(self):
        super().__init__(pandas.read_csv('assets/items.csv'), ItemList.THRESHOLD)