import pandas
from abc import ABC
from thefuzz import fuzz

class List(ABC):
    '''
    The List Abstract class is the blueprint for creating lists of Pokemon game items. Pokedex, 
    Move List, Ability List, all inherit from it.

    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determing if an object exists in the Pokemon games.
        list - A list created from the name of the objects in the dataframe. Made available to support certain search operations.
        threshold - An int that indicates how close incorrect strings have to be to trigger a "did you mean" prompt.
    '''
    
    def __init__(self, filepath: str, threshold: int):
        self.df = pandas.read_csv(filepath, dtype = str)
        self.list = self.df['identifier'].values.tolist()
        self.threshold = threshold

    def __contains__(self, object: str) -> bool:
        '''Returns if the input object exists in the object list, dunder magic method to implement 'in' functionality.'''

        return not self.df[self.df['identifier']==object].empty
    
    def close_match(self, incorrect: str) -> str:
        '''Returns the closest match to the input string using fuzzy string matching. 
        Useful for situations where the user mistypes an item.
        Returns None if the input string does not have a closest match.'''

        closest_val = 0
        closest_item = None

        for object in self.list:

            incorrect = incorrect.lower()
            comparison = fuzz.ratio(incorrect, object)

            if comparison > closest_val and comparison > self.threshold:
                closest_val = fuzz.ratio(incorrect, object)
                closest_item = object

        return closest_item