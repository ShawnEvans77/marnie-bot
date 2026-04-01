from ..constants.types import type_chart as tc, type_map as tm
from src.utils import fetcher as static_f
from ..constants.structs import objects
from ..constants.requesting import fetch as f
from typing import List

class Weak:
    '''Utility class for finding a type's weaknesses, resistances, and immunities, in that order.'''

    def __init__(self):
        self.dmg_ordering = [tc.super_dmg, tc.resist_dmg, tc.no_dmg]

    @staticmethod
    def remove_special(type: str):
        return [c for c in type if c.isalpha()]

    def match_dmg_type_two(self, type_1: str, type_2: str, dmg_type: float) -> List:
        weak_list = []  
        double_effect = tc.super_dmg*2 if dmg_type == tc.super_dmg else tc.resist_dmg/2

        for i in range(tc.num_types):
            t_mat = tc.type_matrix[i]
            calc_dmg = t_mat[tm.t_map[type_1]] * t_mat[tm.t_map[type_2]]

            if calc_dmg == double_effect and dmg_type != 0:
                weak_list.append(f"**{tm.rev_t_map[i].capitalize()}**")   
            elif calc_dmg == dmg_type:
                weak_list.append(tm.rev_t_map[i].capitalize())

        return sorted(weak_list, key=Weak.remove_special)
    
    def match_dmg_type(self, type_1: str, dmg_type: float) -> List:
        weak_list = []
         
        for i in range(tc.num_types):
            if tc.type_matrix[i][tm.t_map[type_1]] == dmg_type:
                weak_list.append(tm.rev_t_map[i].capitalize())

        return sorted(weak_list)
    
    def build_matrix(self, *args) -> List[List]:
        weak_matrix = []
        func_name = self.match_dmg_type if len(args) == 1 else self.match_dmg_type_two

        for dmg_type in self.dmg_ordering:
            weak_matrix.append(func_name(*args, dmg_type))

        return weak_matrix

    def format_matrix(self, matrix: List[List]) -> str:
        label_list = ["Weaknesses", "Resistances", "Immunities"]
        answer = ""

        for i in range(len(label_list)):
            answer += f"**{label_list[i]}:** {", ".join(matrix[i]) if matrix[i] else "None"}"

            answer += "\n" if i != len(label_list) - 1 else ""

        return answer
    
    def weak(self, *args) -> str:

        if all(arg in tm.t_map.keys() for arg in args):
            return self.format_matrix(self.build_matrix(*args))
        
        if args[0] in objects.pokemon:
            return self.format_matrix(self.build_matrix(*f.fetcher.get_type(args[0], static_f.Fetcher.request_pokemon(args[0]))))
        
        # (len(args) == 2 and args[0] in type_list and args[1] in type_list) or (len(args) == 1 and args[0] in type_list):
        #     return self.format_matrix(self.find(*args))
        
        


        # elif (pokemonic_answer := (fetcher.Fetcher.pokemonic_get(args[0], f.fetcher.get_type))) and len(args) == 1:
        #     return self.format_matrix(self.find(*pokemonic_answer))
        



        # elif args[0] not in tm.t_map.keys():
        #     return f"{args[0]} is not a type or pokemon that exists"
        # elif len(args) == 2 and args[1] not in tm.t_map.keys():
        #     return f"{args[1]} is not a type or pokemon that exists"
        # else:
        #     weak_matrix = self.find(*args) if len(args) == 1 else self.find_two(*args)

        # label_list = ["Weaknesses", "Resistances", "Immunities"]
        # answer = ""

        # for i in range(len(label_list)):
        #     answer += f"**{label_list[i]}:** {", ".join(weak_matrix[i]) if weak_matrix[i] else "None"}"

        #     answer += "\n" if i != len(label_list) - 1 else ""

        # return answer
    
x = Weak()
print(x.weak("pikachu"))