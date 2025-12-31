import requests
import pokedex as pd
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

        json = response.json()

        data = json['stats']
        types = json['types']

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

        return self.beautify(answer)
    
    def dt_item(self, item: str, response):
        answer = ""
        answer += "----------------------------------\n"
        answer += f"{response.json()['effect_entries'][0]['effect']}\n"
        answer += "----------------------------------\n"

        return answer
    
    def dt_ability(self, ability: str, response):
        pass

    def sanitize(self, token) -> str:
        token = token.strip().replace(" ", "-")
        tokens = token.split("-")

        if tokens[0] == "mega":
            return tokens[1] + "-" + tokens[0]
        
        return token
    
    def beautify(self, output):
        return "----------------------------------\n" + output + "----------------------------------\n"

    def dt(self, query):

        query = self.sanitize(query)
        poke_url = f"{self.base_url}/pokemon/"
        dex = pd.Pokedex()

        if query.isnumeric():
            
            if dex.by_number(query) is not None:
                query = dex.by_number(query)
            else:
                return "you typed a random number 😹"
        
        if query in dex:
            return self.dt_pokemon(query, requests.get(poke_url+query))
        elif dex.close_match(query) is not None:
            closest_match = dex.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_pokemon(closest_match, requests.get(poke_url+closest_match))
        
        items = il.ItemList()
        item_url = f"{self.base_url}/item/"

        if query in items:
            return self.dt_item(query, requests.get(item_url+query))
        elif il.close_match(query) is not None:
            closest_match = il.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_pokemon(closest_match, requests.get(poke_url+closest_match))
        
        return "i don't even know what this is gang try again 😹"
    
x = FetchData()

print(x.dt("flame orb"))