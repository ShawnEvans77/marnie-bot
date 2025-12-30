import requests
import pokemon_list as pl

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

        answer += "----------------------------------\n"
        answer += f"**{pokemon.title()}** \n\n"
        
        stats = []

        for i in range(len(FetchData.stat_names)):
            stats.append(f"**{FetchData.stat_names[i]}**: {data[i]['base_stat']}")
            total += data[i]['base_stat']

        answer += " | ".join(stats)
        answer += f"\n\n**BST**: {total}\n"

        answer += "----------------------------------"
        return answer
    
    def dt_item(self, item: str, response):
        return response.json()['effect_entries'][0]['effect']
    
    def dt_ability(self, ability: str, response):
        pass

    def dt(self, token):
        
        url = f"{self.base_url}/pokemon/"

        response = requests.get(url)

        mons = pl.PokemonList()

        if token in mons:

            response = requests.get(url)
            return self.dt_pokemon(token, requests.get(url+token))
        
        elif len(mons.close_match(token)) >= 1:

            closest_match = mons.close_match(token)[0]
            answer = ""
            answer += f"wth is {token} 😹. did u mean {closest_match}?\n"
            answer += self.dt_pokemon(closest_match, requests.get(url+closest_match))
            return answer
                
        url = f"{self.base_url}/item/{token}"
        response = requests.get(url)

        if response.status_code == 200:
            return self.dt_item(token, response)
                
        return "i don't even know what this is gang try again 😹"