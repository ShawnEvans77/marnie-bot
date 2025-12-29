import requests

class FetchData:
    '''The Fetch Data class is a wrapper for PokeAPI.'''

    stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]


    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"

    def dt(self, pokemon: str) -> str:
        '''Returns information on a given Pokemon.'''
        
        answer = ""

        print(pokemon)

        url = f"{self.base_url}/pokemon/{pokemon}"

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()['stats']
            answer += f"{pokemon}'s stats are as follows: \n"

            for i in range(len(data)):
                answer += f"{FetchData.stat_names[i]}: {data[i]['base_stat']}\n"

        else:

            answer += f"{pokemon} does not exist gang, maybe you made a typo?"

        return answer