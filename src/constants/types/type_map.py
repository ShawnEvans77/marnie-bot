'''Mapping of type names to indices in the type matrix.'''
from ..structs.objects import types

t_map = {type_name: index for index, type_name in enumerate(types)}
rev_t_map = {index: type_name for type_name, index in t_map.items()}
all_types = t_map.keys()
