from ..constants.api import urls, language
from ..constants.output import aliases, formatters, nationalities, prefix_objects, prefixes
from ..constants.structs import objects
from typing import List
import requests, collections, pandas

class Fetcher:
    '''The Fetcher class is a wrapper for PokeAPI. Queries should be sent to the dt() function, 
    which parses the query to determine if it is a move, item, ability, or Pokemon.
    After determining what type of object the query is, it invokes the appropiate subroutine to find the appropiate data.
    The class imports a constants module that contains Pokemon aliases and lists of items.
    
    Attributes:
        funcs - A set-like object mapping collections to their associated function names and URLs.
    '''

    def __init__(self):
        self.funcs = self.get_func_map().items()

    def get_func_map(self) -> dict:
        '''Returns a function map and their associated URLs.'''

        return {
            objects.pokemon: [self.dt_pokemon, urls.poke_url],
            objects.items: [self.dt_item, urls.item_url],
            objects.moves: [self.dt_move, urls.move_url],
            objects.abilities: [self.dt_ability, urls.ability_url]
        }
    
    def dt(self, query: str) -> str:
        '''Returns a query on a specified Pokemon item. Invokes the appropiate subroutine depending on if the input query
        is a Pokemon, item, ability, or move.'''

        original = query
        query = Fetcher.sanitize(query)

        if pokemonic_answer := Fetcher.pokemonic_get(query, self.dt_pokemon): return pokemonic_answer

        for k, v in self.funcs:
            if query in k:
                query = query if k != objects.pokemon else Fetcher.mon_sanitization(query)
                return v[0](query, requests.get(v[1]+query))
        
        for k, v in self.funcs:
            if closest := k.close_match(query):
                query = query if k != objects.pokemon else Fetcher.mon_sanitization(query)
                return Fetcher.fuzzy(original, closest) + v[0](closest, requests.get(v[1]+closest))

        return f"i don't know what {original} is... check your spelling?"
    
    def dt_pokemon(self, pokemon: str, response: requests.models.Response) -> str:
        '''Returns information on a given Pokemon. Information returned consists of the Pokemon's
        name, generation, type, abilities, base stats, and base stat total.'''
        
        answer = ""
        json = response.json()
        stats, types, abilities = json['stats'], json['types'], json['abilities']

        type = ""
        type += f"_{types[0]['type']['name'].title()}_"

        if len(types) == 2: type += f"/_{types[1]['type']['name'].title()}_"

        answer += f"**{pokemon.title()}** - **Dex #**: {objects.pokemon.get_species_id(pokemon)} | **{formatters.type}:** {type} | **Weight:** {int(json['weight']) / 10:.2f} kg"

        answer += "\n"
        get_stats = []

        total = 0

        for i in range(len(formatters.stat_names)):
            get_stats.append(f"**{formatters.stat_names[i]}**: {stats[i]['base_stat']}")
            total += stats[i]['base_stat']

        answer += f"{" | ".join(get_stats)} | **BST**: {total}\n" 

        for i in range(len(abilities)):

            ability_label = f"**Ab. {i+1}**" if not abilities[i]['is_hidden'] else "**HA**"
            answer += f"{ability_label}: {Fetcher.reverse_sanitize(abilities[i]['ability']['name'])}"

            if i != len(abilities) - 1: answer += " | "

        answer += "**Ab. 1**: N/A\n" if not abilities else "\n"
        return Fetcher.beautify(answer)
    
    def dt_item(self, item: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon item. Information consists of a simple description of what the item does.'''

        answer = ""
        answer += f"**{Fetcher.reverse_sanitize(item)}\n**"

        json = response.json()
        answer += f"{Fetcher.get_effect(json)}\n"

        return Fetcher.beautify(answer)
    
    def dt_move(self, move: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon move. Information consists of the moves accuracy, PP, generation, and type.'''

        answer = ""
        answer += f"**{Fetcher.reverse_sanitize(move)}** - "

        accuracy = objects.moves.get_accuracy(move)
        power = objects.moves.get_power(move)

        json = response.json()

        answer += f"**{formatters.generation}**: {objects.moves.get_generation(move)} | "
        answer += f"**{formatters.type}:** _{json['type']['name'].title()}_ | "
        answer += f"**Power**: {power if not pandas.isnull(power) else "-"} | "
        answer += f"**Accuracy**: {accuracy if not pandas.isnull(accuracy) else "-"} | "
        answer += f"**PP**: {objects.moves.get_pp(move)} | "
        answer += f"**Category**: {json['damage_class']['name'].title()}"

        answer += "\n"
        effect = f"{Fetcher.get_effect(json)}\n"
        answer += effect if formatters.placeholder not in effect else effect.replace(formatters.placeholder, str(json['effect_chance']) + "%")

        return Fetcher.beautify(answer)

    def dt_ability(self, ability: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon ability. Information consists of the ability's generation and effect.'''

        answer = ""
        answer += f"**{Fetcher.reverse_sanitize(ability)}** "
        answer += f"- **{formatters.generation}**: {objects.abilities.get_generation(ability)}\n"

        json = response.json()
        answer += f"{Fetcher.get_effect(json)}\n"

        return Fetcher.beautify(answer)
    
    def sprite(self, query: str, shiny: bool) -> List | str:
        '''Parses the query then returns the appropiate sprite.'''

        query = Fetcher.sanitize(query)

        function_name = self.get_shiny_sprite if shiny else self.get_sprite

        if pokemonic_answer := Fetcher.pokemonic_get(query, function_name): return pokemonic_answer

        if query in objects.pokemon:
            return function_name(query, requests.get(urls.poke_url+query))
  
        if closest := objects.pokemon.close_match(query):
            return function_name(closest, requests.get(urls.poke_url+closest))

        return f"i don't think {query} is a pokemon... check your spelling?"
    
    def get_sprite(self, pokemon: str, response: requests.models.Response) -> List | str:
        '''Returns a URL to the sprite.'''

        url = response.json()['sprites']['front_default']     
        return [url, pokemon] if url else f"sorry, {pokemon} has no sprite right now"
    
    def get_shiny_sprite(self, pokemon: str, response: requests.models.Response) -> List | str:
        '''Returns a URL to the shiny sprite.'''

        shiny_url = response.json()['sprites']['front_shiny']     
        return [shiny_url, pokemon] if shiny_url else f"sorry, {pokemon} has no shiny sprite right now"
    
    def get_type(self, pokemon: str, response: requests.models.Response) -> List:
        '''Fetches the types from a Pokemon HTTP Response. Returns a list containing the Pokemon's name and types.'''
        
        json = response.json()
        types = json['types']
        answer = []

        answer.append(types[0]['type']['name'])
        if len(types) == 2: answer.append(types[1]['type']['name'])

        return [pokemon, answer]
    
    @staticmethod
    def pokemonic_get(query: str, function: collections.abc.Callable):
        '''Calls and returns the value of the appropiate function if the input parameter is a Pokemon, Pokemon alias, dex number, or flavor.'''

        if query in aliases.alias_map:
            associated = aliases.alias_map[query]
            return function(associated, requests.get(urls.poke_url+associated))
        
        if query.isnumeric():
            mon = objects.pokemon.by_number(query)
            return function(mon, requests.get(urls.poke_url+mon)) if mon else None
                    
        if flavor := objects.pokemon.flavor(query): 
            return function(flavor, requests.get(urls.poke_url+flavor))
        
        return None
    
    @staticmethod
    def request_pokemon(pokemon: str) -> requests.models.Response:
        '''Used for making Pokemon request calls outside of the class.'''

        return requests.get(urls.poke_url+pokemon)

    @staticmethod
    def reverse_sanitize(query: str) -> str:
        '''Gets rid of dashes in a String and titles it.'''
        
        return query.replace("-", " ").title()
    
    @staticmethod
    def sanitize(token: str) -> str:
        '''Removes trailing spaces, replaces spaces with dashes.'''

        return token.strip().lower().replace(" ", "-")
      
    @staticmethod
    def mon_sanitization(token: str) -> str:
        '''Rearranges Pokemon with a modifier where the modifier is typed first. For example, token "Mega Alakazam" becomes "alakazam-mega."'''

        tokens = token.split("-")

        if (token not in prefix_objects.prefix_tuple) and (tokens[0] in prefixes.pre_tuple) and (len(tokens) >= 2):
            answer = tokens[1] + "-" + tokens[0]

            if len(tokens) >= 3:
                rest_tup = (word for word in tokens[2:])
                answer += ("-"+"-".join(rest_tup))

            return answer
        else:
            return token

    @staticmethod
    def beautify(output: str) -> str:
        '''Helper method to print bot output easily.'''

        return f"{formatters.hr}\n" + output + f"{formatters.hr}"
    
    @staticmethod
    def fuzzy(erroneous: str, correct: str) -> str:
        '''Message for an approximate string match.'''

        return f"ummmm... {erroneous}? perhaps you meant {correct}?\n"
    
    @staticmethod
    def get_effect(json) -> str:
        '''Returns the effect of a move, item, or ability in the system assigned language.
        Function exists for error checking purposes, sometimes PokeAPI puts the English Desc. in different places.'''

        effect = ""

        for entry in json['effect_entries']:
            if entry['language']['name'] == language.curr_lang:
                effect = f"{entry['effect']}"

        if not json['effect_entries']:
            for entry in json['flavor_text_entries']:
                if entry['language']['name'] == language.curr_lang:                        
                    effect = f"{entry['text']}" if 'text' in entry else f"{entry['flavor_text']}"

        return effect
    
    @staticmethod
    def error_number(num_str: str) -> str:
        return f"there are only {objects.pokemon.get_num_pokemon()} pokemon, {num_str} is way too big..."