import requests
import constants

class FetchData:
    '''The Fetch Data class is a wrapper for PokeAPI. It is the primary way our bot finds information on Pokemon.
    Queries should be sent to the dt() function, which parses the query to determine if it is a move, item, ability, or Pokemon.
    After determining what type of object the query is, it invokes the appropiate subroutine to find the appropiate data.
    Several static members are in this class. Names for stats, URLs, a Pokedex, aliases, and so forth.'''

    def __init__(self):
        pass

    def dt_pokemon(self, pokemon: str, response) -> str:
        '''Returns information on a given Pokemon. Information returned consists of the Pokemon's
        name, type, and base stats.'''
        
        answer = ""
        json = response.json()
        stats, types, abilities = json['stats'], json['types'], json['abilities']
  
        answer += f"**{pokemon.title()}** - **Type:** _{types[0]['type']['name'].title()}_"

        if len(types) == 2: answer += f"/_{types[1]['type']['name'].title()}_"

        answer += "\n"
        get_stats = []

        total = 0

        for i in range(len(constants.stat_names)):
            stat_name = constants.stat_names[i]
            stat_num = stats[i]['base_stat']

            get_stats.append(f"**{stat_name}**: {stat_num}")
            total += stat_num

        answer += f"{" | ".join(get_stats)} | **BST**: {total}\n" 

        for i in range(len(abilities)):

            ability_label = f"**Ab. {i+1}**" if not abilities[i]['is_hidden'] else "**HA**"
            answer += f"{ability_label}: {self.format_response(abilities[i]['ability']['name'])}"

            if i != len(abilities) - 1: answer += " | "

        answer += "**Ab. 1**: N/A\n" if not abilities else "\n"
        return self.beautify(answer)
    
    def dt_item(self, item: str, response) -> str:
        '''Returns information on a Pokemon item. Information consists of a simple description of what the item does.'''

        answer = ""
        answer += f"**{self.format_response(item)}\n**"
        answer += f"{response.json()['effect_entries'][1]['effect']}\n"
        return self.beautify(answer)
    
    def dt_move(self, move: str, move_list, response) -> str:
        '''Returns information on a Pokemon move. Information consists of the moves accuracy, PP, generation, and type.'''

        answer = ""
        answer += f"**{self.format_response(move)}** - "

        accuracy = move_list.get_accuracy(move)
        power = move_list.get_power(move)

        json = response.json()

        answer += f"**Accuracy**: {accuracy if accuracy else "-"} | "
        answer += f"**Power**: {power if power else "-"} | "
        answer += f"**Type:** _{json['type']['name'].title()}_ | "
        answer += f"**PP**: {move_list.get_pp(move)} | "
        answer += f"**Generation**: {move_list.get_generation(move)} | "
        answer += f"**Category**: {json['damage_class']['name'].title()}"

        answer += "\n"

        effect = f"{json['effect_entries'][1]['effect']}\n"

        answer += effect if constants.placeholder not in effect else effect.replace(constants.placeholder, str(json['effect_chance']) + "%")
        return self.beautify(answer)

    def dt_ability(self, ability: str, ability_list, response) -> str:
        '''Returns information on a Pokemon ability. Information consists of the ability's generation and effect.'''

        answer = ""
        answer += f"**{self.format_response(ability)}** "
        answer += f"- **Generation**: {ability_list.get_generation(ability)}\n"
        answer += f"{response.json()['effect_entries'][2]['effect']}\n"

        return self.beautify(answer)

    def format_response(self, query:str) -> str:
        '''PokeAPI can return String names weird. This gets rid of pesky dashes while also titling Strings.'''
        
        return query.replace("-", " ").title()

    def sanitize(self, token: str) -> str:
        '''Removes trailing spaces, replaces spaces with dashes.'''

        token = token.strip().lower().replace(" ", "-")
        tokens = token.split("-")
         
        return token if tokens[0] not in constants.modifiers else tokens[1] + "-" + tokens[0]
    
    def beautify(self, output:str) -> str:
        '''Helper method to print bot output easily.'''

        return f"{constants.HR}\n" + output + f"{constants.HR}"
    
    def fuzzy(self, erroneous: str, correct: str) -> str:
        '''Message for an approximate string match.'''

        return f"ummmm... {erroneous}? perhaps you meant {correct}?\n"

    def dt(self, query:str) -> str:
        '''Returns a query on a specified Pokemon item. Invokes the appropiate subroutine depending on if the input query
        is a Pokemon, item, ability, or move.'''

        query = self.sanitize(query)

        if query.isnumeric():
            
            if constants.pokemon.by_number(query):
                query = constants.pokemon.by_number(query)
            else:
                return "you typed a random number..."
            
        if query in constants.alias:
            return self.dt_pokemon(constants.alias[query], requests.get(constants.poke_url+constants.alias[query]))

        if query in constants.pokemon:
            return self.dt_pokemon(query, requests.get(constants.poke_url+query))
        
        if constants.pokemon.flavor_exists(query):
            return self.dt_pokemon(constants.pokemon.flavor(query), requests.get(constants.poke_url+constants.pokemon.flavor(query)))

        if query in constants.items:
            return self.dt_item(query, requests.get(constants.item_url+query))
        
        if query in constants.moves:
            return self.dt_move(query, constants.moves, requests.get(constants.move_url+query))
        
        if query in constants.abilities:
            return self.dt_ability(query, constants.abilities, requests.get(constants.ability_url+query))

        if constants.pokemon.close_match(query):
            closest_match = constants.pokemon.close_match(query)
            return self.fuzzy(query, closest_match) + self.dt_pokemon(closest_match, requests.get(constants.poke_url+closest_match))
        
        if constants.items.close_match(query):
            closest_match = constants.items.close_match(query)
            return self.fuzzy(query, closest_match) + self.dt_item(closest_match, requests.get(constants.item_url+closest_match))
        
        if constants.moves.close_match(query):
            closest_match = constants.moves.close_match(query)
            return self.fuzzy(query, closest_match) + self.dt_move(closest_match, constants.moves, requests.get(constants.move_url+closest_match))
        
        if constants.abilities.close_match(query):
            closest_match = constants.abilities.close_match(query)
            return self.fuzzy(query, closest_match) + self.dt_ability(closest_match, constants.abilities, requests.get(constants.ability_url+closest_match))

        return f"i don't know what {query} is... check your spelling?"