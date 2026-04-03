'''Tuple of Pokemon objects with common prefixes in them.'''

from ...constants.structs import objects
from src.constants.output import prefixes

ob_tuple = (objects.items, objects.moves, objects.abilities)
prefix_list = []

for ob in ob_tuple:
    for i in ob:
        splitted = i.split("-")

        if len(splitted) >= 2 and splitted[0] in prefixes.pre_tuple: 
            prefix_list.append(i)

prefix_tuple = tuple(prefix_list)