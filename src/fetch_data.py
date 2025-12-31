import requests
import pokemon_list as pl
import item_list as il

class FetchData:
    '''The Fetch Data class is a wrapper for PokeAPI.'''

    stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]

    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"

    def dt_pokemon(self, pokemon: str, response) -> str:
        '''Returns information on a given Pokemon.'''
        
        answer = ""
        total = 0

        data = response.json()['stats']

        types = response.json()['types']

        answer += "----------------------------------\n"
        answer += f"**{pokemon.title()}** - "

        type_1 = types[0]['type']['name'].title()

        if len(types) == 2: 
            type_2 = types[1]['type']['name'].title()
            answer += f" _{type_1}_/_{type_2}_\n"
        else:
            answer += f"_{type_1}_\n"

        stats = []

        for i in range(len(FetchData.stat_names)):
            stats.append(f"**{FetchData.stat_names[i]}**: {data[i]['base_stat']}")
            total += data[i]['base_stat']

        answer += " | ".join(stats)
        answer += f" | **BST**: {total}\n"

        answer += "----------------------------------"
        return answer
    
    def dt_item(self, item: str, response):
        answer = ""
        answer += "----------------------------------\n"
        answer += f"{response.json()['effect_entries'][0]['effect']}\n"
        answer += "----------------------------------\n"

        return answer
    
    def dt_ability(self, ability: str, response):
        pass

    def dt(self, token):
        
        url = f"{self.base_url}/pokemon/"

        response = requests.get(url)

        mons = pl.PokemonList()

        if token.isnumeric() and mons.pokemon_by_number(token) is not None:

            return self.dt_pokemon(mons.pokemon_by_number(token), requests.get(url+mons.pokemon_by_number(token)))
        
        elif mons.pokemon_by_number(token) is None:

            return "you typed a random number 😹"

        if token in mons:

            return self.dt_pokemon(token, requests.get(url+token))
        
        elif len(mons.close_match(token)) >= 1:

            closest_match = mons.close_match(token)[0]
            answer = ""
            answer += f"wth is {token} 😹. did u mean {closest_match}?\n"
            answer += self.dt_pokemon(closest_match, requests.get(url+closest_match))
            return answer
                
        url = f"{self.base_url}/item/"

        items = il.ItemList()

        if token in items:

            return self.dt_item(token, requests.get(url+token))
        
        elif len(items.close_match(token)) >= 1:

            closest_match = items.close_match(token)[0]
            answer = ""
            answer += f"wth is {token} 😹. did u mean {closest_match}?\n"
            answer += self.dt_item(closest_match, requests.get(url+closest_match))
            return answer
   
        return "i don't even know what this is gang try again 😹"