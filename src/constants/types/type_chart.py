'''Matrix representing the weaknesses and resistances of all eighteen types.'''

import src.constants.types.type_map as tm

num_types = 18

normal_dmg = 1.0
super_dmg = 2.0
resist_dmg = 0.5
no_dmg = 0.0

type_matrix = [[normal_dmg] * num_types for _ in range(num_types)]

# [attacker][defender]
# normal

norm_arr = type_matrix[tm.t_map['normal']]

norm_arr[tm.t_map['rock']] = resist_dmg
norm_arr[tm.t_map['ghost']] = no_dmg
norm_arr[tm.t_map['steel']] = resist_dmg

# fire

fir_arr = type_matrix[tm.t_map['fire']]

fir_arr[tm.t_map['fire']] = resist_dmg
fir_arr[tm.t_map['water']] = resist_dmg
fir_arr[tm.t_map['grass']] = super_dmg
fir_arr[tm.t_map['ice']] = super_dmg
fir_arr[tm.t_map['bug']] = super_dmg
fir_arr[tm.t_map['rock']] = resist_dmg
fir_arr[tm.t_map['dragon']] = resist_dmg
fir_arr[tm.t_map['steel']] = super_dmg

# water

wat_arr = type_matrix[tm.t_map['water']]

wat_arr[tm.t_map['fire']] = super_dmg
wat_arr[tm.t_map['water']] = resist_dmg
wat_arr[tm.t_map['grass']] = resist_dmg
wat_arr[tm.t_map['ground']] = super_dmg
wat_arr[tm.t_map['rock']] = super_dmg
wat_arr[tm.t_map['dragon']] = resist_dmg

# grass

grs_arr = type_matrix[tm.t_map['grass']]

grs_arr[tm.t_map['fire']] = resist_dmg
grs_arr[tm.t_map['water']] = super_dmg
grs_arr[tm.t_map['grass']] = resist_dmg
grs_arr[tm.t_map['poison']] = resist_dmg
grs_arr[tm.t_map['ground']] = super_dmg
grs_arr[tm.t_map['flying']] = resist_dmg
grs_arr[tm.t_map['bug']] = resist_dmg
grs_arr[tm.t_map['rock']] = super_dmg
grs_arr[tm.t_map['dragon']] = resist_dmg
grs_arr[tm.t_map['steel']] = resist_dmg

# electric

ele_arr = type_matrix[tm.t_map['electric']]

ele_arr[tm.t_map['water']] = super_dmg
ele_arr[tm.t_map['grass']] = resist_dmg
ele_arr[tm.t_map['electric']] = resist_dmg
ele_arr[tm.t_map['ground']] = no_dmg
ele_arr[tm.t_map['flying']] = super_dmg
ele_arr[tm.t_map['dragon']] = resist_dmg

# ice

ice_arr = type_matrix[tm.t_map['ice']]

ice_arr[tm.t_map['fire']] = resist_dmg
ice_arr[tm.t_map['water']] = resist_dmg
ice_arr[tm.t_map['grass']] = super_dmg
ice_arr[tm.t_map['ice']] = resist_dmg
ice_arr[tm.t_map['ground']] = super_dmg
ice_arr[tm.t_map['flying']] = super_dmg
ice_arr[tm.t_map['dragon']] = super_dmg
ice_arr[tm.t_map['steel']] = resist_dmg

# fighting

fig_arr = type_matrix[tm.t_map['fighting']]

fig_arr[tm.t_map['normal']] = super_dmg
fig_arr[tm.t_map['ice']] = super_dmg
fig_arr[tm.t_map['poison']] = resist_dmg
fig_arr[tm.t_map['flying']] = resist_dmg
fig_arr[tm.t_map['psychic']] = resist_dmg
fig_arr[tm.t_map['bug']] = resist_dmg
fig_arr[tm.t_map['rock']] = super_dmg
fig_arr[tm.t_map['ghost']] = no_dmg
fig_arr[tm.t_map['dark']] = super_dmg
fig_arr[tm.t_map['steel']] = super_dmg
fig_arr[tm.t_map['fairy']] = resist_dmg

# poison

pos_arr = type_matrix[tm.t_map['poison']]

pos_arr[tm.t_map['grass']] = super_dmg
pos_arr[tm.t_map['poison']] = resist_dmg
pos_arr[tm.t_map['rock']] = resist_dmg
pos_arr[tm.t_map['ghost']] = resist_dmg
pos_arr[tm.t_map['steel']] = no_dmg
pos_arr[tm.t_map['fairy']] = super_dmg

# ground

gro_arr = type_matrix[tm.t_map['ground']]

gro_arr[tm.t_map['fire']] = super_dmg
gro_arr[tm.t_map['grass']] = resist_dmg
gro_arr[tm.t_map['electric']] = super_dmg
gro_arr[tm.t_map['poison']] = super_dmg
gro_arr[tm.t_map['flying']] = no_dmg
gro_arr[tm.t_map['bug']] = resist_dmg
gro_arr[tm.t_map['rock']] = super_dmg
gro_arr[tm.t_map['steel']] = super_dmg

# flying

fly_arr = type_matrix[tm.t_map['flying']]

fly_arr[tm.t_map['grass']] = super_dmg
fly_arr[tm.t_map['electric']] = resist_dmg
fly_arr[tm.t_map['fighting']] = super_dmg
fly_arr[tm.t_map['bug']] = super_dmg
fly_arr[tm.t_map['rock']] = resist_dmg
fly_arr[tm.t_map['steel']] = resist_dmg

# psychic

psy_arr = type_matrix[tm.t_map['psychic']]

psy_arr[tm.t_map['fighting']] = super_dmg
psy_arr[tm.t_map['poison']] = super_dmg
psy_arr[tm.t_map['psychic']] = resist_dmg
psy_arr[tm.t_map['dark']] = no_dmg
psy_arr[tm.t_map['steel']] = resist_dmg

# bug 

bug_arr = type_matrix[tm.t_map['bug']]

bug_arr[tm.t_map['fire']] = resist_dmg
bug_arr[tm.t_map['grass']] = super_dmg
bug_arr[tm.t_map['fighting']] = resist_dmg
bug_arr[tm.t_map['poison']] = resist_dmg
bug_arr[tm.t_map['flying']] = resist_dmg
bug_arr[tm.t_map['psychic']] = super_dmg
bug_arr[tm.t_map['ghost']] = resist_dmg
bug_arr[tm.t_map['dark']] = super_dmg
bug_arr[tm.t_map['steel']] = resist_dmg
bug_arr[tm.t_map['fairy']] = resist_dmg

# rock

rck_arr = type_matrix[tm.t_map['rock']]

rck_arr[tm.t_map['fire']] = super_dmg
rck_arr[tm.t_map['ice']] = super_dmg
rck_arr[tm.t_map['fighting']] = resist_dmg
rck_arr[tm.t_map['ground']] = resist_dmg
rck_arr[tm.t_map['flying']] = super_dmg
rck_arr[tm.t_map['bug']] = super_dmg
rck_arr[tm.t_map['steel']] = resist_dmg

# ghost

ghs_arr = type_matrix[tm.t_map['ghost']]

ghs_arr[tm.t_map['normal']] = no_dmg
ghs_arr[tm.t_map['psychic']] = super_dmg
ghs_arr[tm.t_map['ghost']] = super_dmg
ghs_arr[tm.t_map['dark']] = resist_dmg

# dragon

drg_arr = type_matrix[tm.t_map['dragon']]

drg_arr[tm.t_map['dragon']] = super_dmg
drg_arr[tm.t_map['steel']] = resist_dmg
drg_arr[tm.t_map['fairy']] = no_dmg

# dark

drk_arr = type_matrix[tm.t_map['dark']]

drk_arr[tm.t_map['fighting']] = resist_dmg
drk_arr[tm.t_map['psychic']] = super_dmg
drk_arr[tm.t_map['ghost']] = super_dmg
drk_arr[tm.t_map['dark']] = resist_dmg
drk_arr[tm.t_map['fairy']] = resist_dmg

# steel

stl_arr = type_matrix[tm.t_map['steel']]

stl_arr[tm.t_map['fire']] = resist_dmg
stl_arr[tm.t_map['water']] = resist_dmg
stl_arr[tm.t_map['electric']] = resist_dmg
stl_arr[tm.t_map['ice']] = super_dmg
stl_arr[tm.t_map['rock']] = super_dmg
stl_arr[tm.t_map['steel']] = resist_dmg
stl_arr[tm.t_map['fairy']] = super_dmg

# fairy

fry_arr = type_matrix[tm.t_map['fairy']]

fry_arr[tm.t_map['fire']] = resist_dmg
fry_arr[tm.t_map['fighting']] = super_dmg
fry_arr[tm.t_map['poison']] = resist_dmg
fry_arr[tm.t_map['dragon']] = super_dmg
fry_arr[tm.t_map['dark']] = super_dmg
fry_arr[tm.t_map['steel']] = resist_dmg