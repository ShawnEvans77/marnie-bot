import requests
import pokedex as pd
import item_list as il
import move_list as ml
import ability_list as al

class FetchData:
    '''The Fetch Data class is a wrapper for PokeAPI.'''

    stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]

    base_url = "https://pokeapi.co/api/v2"

    poke_url = f"{base_url}/pokemon/"
    item_url = f"{base_url}/item/"
    move_url = f"{base_url}/move/"
    ability_url = f"{base_url}/ability/"

    modifiers = ("hisui", "mega", "primal", "origin", "galar")

    LINE_LENGTH = 35

    HR = '-' * LINE_LENGTH

    def __init__(self):
        pass

    def dt_pokemon(self, pokemon: str, response) -> str:
        '''Returns information on a given Pokemon.'''
        
        answer = ""
        total = 0

        json = response.json()

        data = json['stats']
        types = json['types']
        abilities = json['abilities']

        answer += f"**{pokemon.title()}** - "

        type_1 = types[0]['type']['name'].title()
        answer += f"_{type_1}_"

        if len(types) == 2: 
            type_2 = types[1]['type']['name'].title()
            answer += f"/_{type_2}_"

        answer += "\n"

        stats = []

        for i in range(len(FetchData.stat_names)):
            stat_name = FetchData.stat_names[i]
            stat_num = data[i]['base_stat']

            stats.append(f"**{stat_name}**: {stat_num}")

            total += data[i]['base_stat']

        answer += " | ".join(stats)
        answer += f" | **BST**: {total}\n"

        for i in range(len(abilities)):

            ability_label = f"**Ab. {i+1}**" if not abilities[i]['is_hidden'] else "**HA**"
            answer += f"{ability_label}: {self.format_response(abilities[i]['ability']['name'])}"

            if i != len(abilities) - 1:
                answer += " | "

        if not abilities:
            answer += "**Ab. 1**: N/A"

        answer += "\n"

        return self.beautify(answer)
    
    def dt_item(self, item: str, response) -> str:
        answer = ""
        answer += f"**{self.format_response(item)}\n**"
        answer += f"{response.json()['effect_entries'][0]['effect']}\n"
        return self.beautify(answer)
    
    def dt_move(self, move: str, move_list, response) -> str:

        answer = ""
        answer += f"**{self.format_response(move)}** - "

        accuracy = move_list.get_accuracy(move)

        answer += f"**Accuracy**: "

        if accuracy:
            answer += f"{move_list.get_accuracy(move)} "
        else:
            answer += "- "

        answer += "| "
        
        answer += f"**PP**: {move_list.get_pp(move)} | "
        answer += f"**Generation**: {move_list.get_generation(move)} | "
        answer += f"**Type**: {response.json()['damage_class']['name'].title()}"

        answer += "\n"

        answer += f"{response.json()['effect_entries'][0]['effect']}\n"

        return self.beautify(answer)

    def dt_ability(self, ability: str, ability_list, response):
        answer = ""
        answer += f"**{self.format_response(ability)}** "
        answer += f"- **Generation**: {ability_list.get_generation(ability)}\n"

        try:
            answer += f"{response.json()['effect_entries'][1]['effect']}\n"
        except IndexError:
            answer += f"{response.json()['effect_entries'][0]['effect']}\n"

        return self.beautify(answer)

    def format_response(self, query:str) -> str:
        '''PokeAPI can return String names weird. This gets rid of pesky dashes while also titling Strings.'''
        return query.replace("-", " ").title()

    def sanitize(self, token: str) -> str:
        '''Removes trailing spaces, replaces spaces with dashes.'''

        token = token.strip().lower().replace(" ", "-")
        tokens = token.split("-")

        if tokens[0] in FetchData.modifiers:
            return tokens[1] + "-" + tokens[0]            
        
        return token
    
    def beautify(self, output):
        '''Helper method to print bot output easily.'''

        return f"{FetchData.HR}\n" + output + f"{FetchData.HR}\n"

    def dt(self, query):

        query = self.sanitize(query)

        dex = pd.Pokedex()
        items = il.ItemList()
        moves = ml.MoveList()
        abilities = al.AbilityList()

        if query.isnumeric():
            
            if dex.by_number(query):
                query = dex.by_number(query)
            else:
                return "you typed a random number 😹"
        
        if query in dex:
            return self.dt_pokemon(query, requests.get(FetchData.poke_url+query))
        
        if dex.flavor_exists(query):
            return self.dt_pokemon(dex.flavor(query), requests.get(FetchData.poke_url+dex.flavor(query)))

        if query in items:
            return self.dt_item(query, requests.get(FetchData.item_url+query))
        
        if query in moves:
            return self.dt_move(query, moves, requests.get(FetchData.move_url+query))
        
        if query in abilities:
            return self.dt_ability(query, abilities, requests.get(FetchData.ability_url+query))

        if dex.close_match(query):
            closest_match = dex.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_pokemon(closest_match, requests.get(FetchData.poke_url+closest_match))
        
        if items.close_match(query):
            closest_match = items.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_item(closest_match, requests.get(FetchData.item_url+closest_match))
        
        if moves.close_match(query):
            closest_match = moves.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_move(closest_match, moves, requests.get(FetchData.move_url+closest_match))
        
        if abilities.close_match(query):
            closest_match = abilities.close_match(query)
            return f"wth is {query} 😹. did u mean {closest_match}?\n" + self.dt_ability(closest_match, abilities, requests.get(FetchData.ability_url+closest_match))

        return "i don't even know what this is gang try again 😹"