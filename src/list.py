from abc import ABC
from thefuzz import fuzz

class List(ABC):
    '''
    The List Abstract class is the blueprint for creating lists of Pokemon game items. Pokedex, 
    Move List, Ability List, all inherit from it.

    All lists will support an exists() method as well as the Python in operator. They also support a 
    method for finding closest matches using fuzzy string matching. The list class is meant to be an abstraction of a 
    pandas dataframe. CSVs are sourced from the assets directory. We do this to support the program recognizing nonexistent
    game objects. without going through the trouble of parsing HTTP status codes.

    Attributes:
        df - A pandas dataframe sourced from a CSV, used for determing if an object exists in the Pokemon games.
        list - A list created from the name of the objects in the dataframe. Made available to support certain search operations.
    '''
    def __init__(self, df, threshold):
        self.df = df
        self.list = self.df['identifier'].values.tolist()
        self.threshold = threshold

    def exists(self, object:str) -> bool:
        '''Returns if the input object exists in the object list.'''
        return not self.df[self.df['identifier']==object].empty

    def __contains__(self, object:str) -> bool:
        '''Returns if the input object exists in the object list, dunder magic method to implement 'in' functionality.'''
        return not self.df[self.df['identifier']==object].empty
    
    def close_match(self, incorrect:str) -> str:
        '''Returns the closest match to the input string. Useful for situations where the user mistypes an item.
        Returns None if the input string does not exist in this list of objects..'''

        closest_val = 0
        closest_item = None

        for object in self.list:

            comparison = fuzz.ratio(incorrect.lower(), object)

            if comparison > closest_val and comparison > self.threshold:
                closest_val = fuzz.ratio(incorrect.lower(), object)
                closest_item = object

        return closest_item