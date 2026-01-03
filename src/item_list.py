import pandas
import numpy
from thefuzz import fuzz

class ItemList:
    '''The Item List stores all items from all Pokemon Games.
    
    Attributes:
        THRESHOLD (int) - How close a user has to be for the "did you mean?" suggestion to work.
        df (pandas dataframe) - The result of reading the item CSV.
        list (list) - A list of items from all Pokemon games.  
    '''

    THRESHOLD = 70

    def __init__(self):
        self.df = pandas.read_csv('assets/items.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, item:str) -> str:
        return item.lower() in self.list
    
    def __contains__(self, item:str) -> str:
        return item.lower() in self.list

    def close_match(self, incorrect:str) -> str:

        '''Returns the closest match to the input string. Useful for situations where the user mistykes an item.'''

        closest_val = 0
        closest_item = None

        for item in self.list:

            comparison = fuzz.ratio(incorrect.lower(), item)

            if comparison > closest_val and comparison > ItemList.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), item)
                closest_item = item

        return closest_item