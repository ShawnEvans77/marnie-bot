from ..constants.types import type_chart as tc, type_map as tm
from typing import List

class Weak:
    '''Utility class for finding a type's weaknesses, resistances, and immunities, in that order.'''

    def __init__(self):
        self.dmg_ordering = [tc.super_dmg, tc.resist_dmg, tc.no_dmg]

    def match_dmg_type(self, type_1: str, dmg_type) -> List:

        weak_list = []
         
        for i in range(tc.num_types):
            if tc.type_matrix[i][tm.t_map[type_1]] == dmg_type:
                weak_list.append(tm.rev_t_map[i].capitalize())

        return sorted(weak_list)

    def find(self, type_1: str) -> List[List]:
        
        weak_matrix = []

        for dmg_type in self.dmg_ordering:
            weak_matrix.append(self.match_dmg_type(type_1, dmg_type))

        return weak_matrix
    
    def weak(self, type_1: str) -> str:

        if type_1 not in tm.t_map.keys():
            return f"{type_1} is not a type that exists"
        
        weak_matrix = self.find(type_1)
        label_list = ["Weaknesses", "Resistances", "Immunities"]
        answer = ""

        for i in range(len(label_list)):
            answer += f"**{label_list[i]}:** {", ".join(weak_matrix[i]) if weak_matrix[i] else "None"}"

            answer += "\n" if i != len(label_list) - 1 else ""

        return answer