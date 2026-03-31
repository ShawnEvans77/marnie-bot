'''The four objects Marnie uses to determine the validity of user queries.'''

from ...lists.implemented import ability_list as al, move_list as ml, pokedex as pd, item_list as il

pokemon = pd.Pokedex()
items = il.ItemList()
moves = ml.MoveList()
abilities = al.AbilityList()