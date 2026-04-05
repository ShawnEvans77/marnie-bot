'''Mapping of type names to indices in the type matrix.'''
from ..structs.objects import types

t_map = {}
i = 0

for type in types:
    t_map[type] = i
    i += 1

rev_t_map = {v: k for k, v in t_map.items()}
all_types = t_map.keys()