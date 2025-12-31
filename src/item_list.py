import pandas
import numpy
from thefuzz import fuzz

class ItemList:

    THRESHOLD = 65

    def __init__(self):
        self.df = pandas.read_csv('assets/items.csv')
        self.list = self.df['identifier'].values.tolist()

    def exists(self, item):
        return item.lower() in self.list
    
    def __contains__(self, item):
        return item.lower() in self.list

    def close_match(self, incorrect) -> str:
        closest_val = 0
        closest_item = None

        for item in self.list:

            comparison = fuzz.ratio(incorrect.lower(), pokemon)

            if comparison > closest_val and comparison > ItemList.THRESHOLD:
                closest_val = fuzz.ratio(incorrect.lower(), pokemon)
                closest_item = item

        return closest_item