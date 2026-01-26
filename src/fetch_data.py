import requests, constants

class FetchData:
    '''The Fetch Data class is a wrapper for PokeAPI. It is the primary way our bot finds information on Pokemon.
    Queries should be sent to the dt() function, which parses the query to determine if it is a move, item, ability, or Pokemon.
    After determining what type of object the query is, it invokes the appropiate subroutine to find the appropiate data.
    The class imports a constants module to store Pokemon aliases and lists of items.
    
    Attributes:
        funcs - A set-like object mapping collections to their associated function names and URLs.
    '''

    def __init__(self):
        self.funcs = self.get_func_map().items()

    def dt_pokemon(self, pokemon: str, response) -> str:
        '''Returns information on a given Pokemon. Information returned consists of the Pokemon's
        name, generation, type, abilities, base stats, and base stat total.'''
        
        answer = ""
        json = response.json()
        stats, types, abilities = json['stats'], json['types'], json['abilities']

        answer += f"**{pokemon.title()}** - **Dex #**: {constants.pokemon.get_species_id(pokemon)} | **{constants.type}:** _{types[0]['type']['name'].title()}_"

        if len(types) == 2: answer += f"/_{types[1]['type']['name'].title()}_"

        answer += "\n"
        get_stats = []

        total = 0

        for i in range(len(constants.stat_names)):
            get_stats.append(f"**{constants.stat_names[i]}**: {stats[i]['base_stat']}")
            total += stats[i]['base_stat']

        answer += f"{" | ".join(get_stats)} | **BST**: {total}\n" 

        for i in range(len(abilities)):

            ability_label = f"**Ab. {i+1}**" if not abilities[i]['is_hidden'] else "**HA**"
            answer += f"{ability_label}: {FetchData.reverse_sanitize(abilities[i]['ability']['name'])}"

            if i != len(abilities) - 1: answer += " | "

        answer += "**Ab. 1**: N/A\n" if not abilities else "\n"
        return FetchData.beautify(answer)
    
    def dt_item(self, item: str, response) -> str:
        '''Returns information on a Pokemon item. Information consists of a simple description of what the item does.'''

        answer = ""
        answer += f"**{FetchData.reverse_sanitize(item)}\n**"

        json = response.json()
        answer += f"{FetchData.get_effect(json)}\n"

        return FetchData.beautify(answer)
    
    def dt_move(self, move: str, response) -> str:
        '''Returns information on a Pokemon move. Information consists of the moves accuracy, PP, generation, and type.'''

        answer = ""
        answer += f"**{FetchData.reverse_sanitize(move)}** - "

        accuracy = constants.moves.get_accuracy(move)
        power = constants.moves.get_power(move)

        json = response.json()

        answer += f"**{constants.generation}**: {constants.moves.get_generation(move)} | "
        answer += f"**{constants.type}:** _{json['type']['name'].title()}_ | "
        answer += f"**Power**: {power if power else "-"} | "
        answer += f"**Accuracy**: {accuracy if accuracy else "-"} | "
        answer += f"**PP**: {constants.moves.get_pp(move)} | "
        answer += f"**Category**: {json['damage_class']['name'].title()}"

        answer += "\n"
        effect = f"{FetchData.get_effect(json)}\n"
        answer += effect if constants.placeholder not in effect else effect.replace(constants.placeholder, str(json['effect_chance']) + "%")

        return FetchData.beautify(answer)

    def dt_ability(self, ability: str, response) -> str:
        '''Returns information on a Pokemon ability. Information consists of the ability's generation and effect.'''

        answer = ""
        answer += f"**{FetchData.reverse_sanitize(ability)}** "
        answer += f"- **{constants.generation}**: {constants.abilities.get_generation(ability)}\n"

        json = response.json()
        answer += f"{FetchData.get_effect(json)}\n"

        return FetchData.beautify(answer)
    
    @staticmethod
    def reverse_sanitize(query: str) -> str:
        '''Gets rid of dashes in a String and titles it.'''
        
        return query.replace("-", " ").title()
    
    @staticmethod
    def sanitize(token: str) -> str:
        '''Removes trailing spaces, replaces spaces with dashes, rearranges Pokemon with a modifier where the modifier
        is typed first. For example, token "Mega Alakazam" becomes "alakazam-mega."'''

        token = token.strip().lower().replace(" ", "-")
        tokens = token.split("-")
         
        return token if tokens[0] not in constants.modifiers else tokens[1] + "-" + tokens[0]
    
    @staticmethod
    def beautify(output: str) -> str:
        '''Helper method to print bot output easily.'''

        return f"{constants.hr}\n" + output + f"{constants.hr}"
    
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
            if entry['language']['name'] == constants.language:
                effect = f"{entry['effect']}"

        if not json['effect_entries']:
            for entry in json['flavor_text_entries']:
                if entry['language']['name'] == constants.language:                        
                    effect = f"{entry['text']}" if 'text' in entry else f"{entry['flavor_text']}"

        return effect

    def get_func_map(self) -> dict:
        '''Returns a function map and their associated URLs.'''

        return  {
            constants.pokemon: [self.dt_pokemon, constants.poke_url],
            constants.items: [self.dt_item, constants.item_url],
            constants.moves: [self.dt_move, constants.move_url],
            constants.abilities: [self.dt_ability, constants.ability_url]
        }

    def dt(self, query: str) -> str:
        '''Returns a query on a specified Pokemon item. Invokes the appropiate subroutine depending on if the input query
        is a Pokemon, item, ability, or move.'''

        query = FetchData.sanitize(query)

        if query in constants.alias:
            associated = constants.alias[query]
            return self.dt_pokemon(associated, requests.get(constants.poke_url+associated))
        
        if query.isnumeric():
            mon = constants.pokemon.by_number(query)
            return self.dt_pokemon(mon, requests.get(constants.poke_url+mon)) if mon else "you typed a random number..."
        
        if flavor := constants.pokemon.flavor(query): 
            return self.dt_pokemon(flavor, requests.get(constants.poke_url+flavor))

        for k, v in self.funcs:
            if query in k:
                return v[0](query, requests.get(v[1]+query))
        
        for k, v in self.funcs:
            if closest := k.close_match(query):
                return FetchData.fuzzy(query, closest) + v[0](closest, requests.get(v[1]+closest))

        return f"i don't know what {query} is... check your spelling?"