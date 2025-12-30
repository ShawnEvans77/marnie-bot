import pandas
import requests

df = pandas.DataFrame(columns=
                      ['name', 'type 1', 'type 2', 'HP', 'ATK', 'DEF', 'SPA', 'SPD', 'SPE', 'BST', 'ability 1', 'ability 2', 'hidden ability'])

# new_row = pandas.DataFrame({'name': 'Pikachu'}, index=[1])
# new_row_2 = pandas.DataFrame({'name': 'Bulbasaur'}, index=[2])

# df = pandas.concat([df, new_row])
# df = pandas.concat([df, new_row_2])

# df.index.name = "dex#"

# df.to_csv('output.csv')

url = 'https://pokeapi.co/api/v2'

poke_url = f"{url}/pokemon"

count_url = f"{poke_url}/count"
request = requests.get(poke_url)

NUMBER_OF_MONS = int(request.json()['count'])

print(NUMBER_OF_MONS)

for i in range(1, NUMBER_OF_MONS+1):

    curr_mon_url = f"{poke_url}/{i}"

    request = requests.get(curr_mon_url)