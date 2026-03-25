'''The four objects Marnie uses to determine the validity of user queries.'''
from ...lists.implemented.api import api_pokedex as a_pd, api_item_list as a_il, api_move_list as a_ml, api_ability_list as a_al
from ...lists.implemented.showdown import showdown_dex as s_pd, showdown_move_list as s_ml

api_pokemon = a_pd.Pokedex()
api_items = a_il.ItemList()
api_moves = a_ml.MoveList()
api_abilities = a_al.AbilityList()

show_pokemon = s_pd.ShowdownPokeDex()
show_moves = s_ml.ShowdownMoveList()