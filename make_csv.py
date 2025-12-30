import pandas

df = pandas.DataFrame(columns=
                      ['name', 'type 1', 'type 2', 'HP', 'ATK', 'DEF', 'SPA', 'SPD', 'SPE', 'BST', 'ability 1', 'ability 2', 'hidden ability'])

mons_names = pandas.read_csv('data.csv')

print(mons_names.loc[mons_names['species_id'] == 150]['identifier'])