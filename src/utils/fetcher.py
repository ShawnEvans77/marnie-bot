from ..constants.api import urls, language
from ..constants.output import aliases, formatters, nationalities, prefixes
from ..constants.structs import objects
from .dex import DexEntry, art_url, title
from collections.abc import Callable
from typing import NamedTuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests, pandas

def build_session() -> requests.Session:
    '''Builds the one session every PokeAPI request goes through. A session keeps its connection
    open between requests, so only the first lookup pays to set the connection up.
    A request that fails because the connection dropped, or because PokeAPI had a brief
    server error, is tried one more time.'''

    session = requests.Session()
    retries = Retry(total=1, backoff_factor=0.2, status_forcelist=(502, 503, 504), allowed_methods=("GET",))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

class Found(NamedTuple):
    '''What a query turned out to mean: the list it belongs to (Pokemon, items, moves, or
    abilities), its name, PokeAPI's answer, and whether it was only a fuzzy match.'''

    collection: object
    name: str
    response: requests.models.Response
    fuzzy: bool

class Fetcher:
    '''The Fetcher class is a wrapper for PokeAPI. Queries should be sent to the dt() function, 
    which parses the query to determine if it is a move, item, ability, or Pokemon.
    After determining what type of object the query is, it invokes the appropiate subroutine to find the appropiate data.
    The class imports a constants module that contains Pokemon aliases and lists of items.
    
    Attributes:
        func_map - Maps each collection to its !dt function and its URL.
        kinds - Maps each collection to the name of the kind of thing it holds.
        session - The shared connection to PokeAPI.
        timeout - How many seconds one request may take before it is given up on.
    '''

    session = build_session()
    timeout = 10

    @staticmethod
    def get(url: str) -> requests.models.Response:
        '''Makes a PokeAPI request on the shared session. Nothing is remembered between calls,
        so the data is always fresh. Raises a requests.RequestException if PokeAPI can't be
        reached, takes too long, or answers with an error.'''

        response = Fetcher.session.get(url, timeout=Fetcher.timeout)
        response.raise_for_status()
        return response

    def __init__(self):
        self.func_map = self.get_func_map()
        self.kinds = {objects.pokemon: "pokemon", objects.items: "item", objects.moves: "move", objects.abilities: "ability"}

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

        found = self.find(query)

        return self.describe(query, found) if found else Fetcher.unknown(query)

    def dex(self, query: str) -> DexEntry | str:
        '''Looks a query up the same way dt() does, but returns everything the !dex embed needs
        instead of text. Returns Marnie's "i don't know" message if the query matches nothing.

        For a Pokemon it also asks PokeAPI for the species (dex entry, egg groups, and so on) and
        its evolution chain. Those two are extras: if either can't be fetched, it is left as None
        and the embed simply leaves that part out.'''

        found = self.find(query)

        if not found: return Fetcher.unknown(query)

        data = found.response.json()

        entry = DexEntry(
            kind=self.kinds[found.collection],
            name=found.name,
            data=data,
            text=self.describe(query, found),
            note=Fetcher.fuzzy(query, found.name).strip() if found.fuzzy else None,
        )

        if found.collection is objects.pokemon:
            entry.species = Fetcher.get_extra((data.get('species') or {}).get('url'))
            entry.evolution = Fetcher.get_extra(((entry.species or {}).get('evolution_chain') or {}).get('url'))

        return entry

    def find(self, query: str) -> Found | None:
        '''Works out what a query means and requests it from PokeAPI. Tries, in order: a Pokemon
        alias, dex number, or flavor, then an exact name, then the closest fuzzy match.
        Returns None if nothing matches.'''

        sanitized_query = Fetcher.sanitize(query)

        if pokemonic_answer := Fetcher.pokemonic_get(sanitized_query, lambda name, response: Found(objects.pokemon, name, response, False)):
            return pokemonic_answer

        mon_sanitized_query = Fetcher.mon_sanitize(sanitized_query)

        for k, v in self.func_map.items():
            if sanitized_query in k:
                return Found(k, sanitized_query, Fetcher.get(v[1]+sanitized_query), False)
            elif k == objects.pokemon and mon_sanitized_query in k:
                return Found(k, mon_sanitized_query, Fetcher.get(v[1]+mon_sanitized_query), False)

        for k, v in self.func_map.items():
            if  (k == objects.pokemon and (closest := k.close_match(mon_sanitized_query))) or (closest := k.close_match(sanitized_query)):
                return Found(k, closest, Fetcher.get(v[1]+closest), True)

        return None

    def describe(self, query: str, found: Found) -> str:
        '''Writes the !dt text for something find() found, with the "perhaps you meant" line
        on top if it was a fuzzy match.'''

        text = self.func_map[found.collection][0](found.name, found.response)

        return (Fetcher.fuzzy(query, found.name) if found.fuzzy else "") + text

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
            answer += f"{ability_label}: {title(abilities[i]['ability']['name'])}"

            if i != len(abilities) - 1: answer += " | "

        answer += "**Ab. 1**: N/A\n" if not abilities else "\n"
        return Fetcher.beautify(answer)
    
    def dt_item(self, item: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon item. Information consists of a simple description of what the item does.'''

        answer = ""
        answer += f"**{title(item)}\n**"

        json = response.json()
        answer += f"{Fetcher.get_effect(json)}\n"

        return Fetcher.beautify(answer)
    
    def dt_move(self, move: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon move. Information consists of the moves accuracy, PP, generation, and type.'''

        answer = ""
        answer += f"**{title(move)}** - "

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
        answer += f"{Fetcher.get_move_effect(json)}\n"

        return Fetcher.beautify(answer)

    def dt_ability(self, ability: str, response: requests.models.Response) -> str:
        '''Returns information on a Pokemon ability. Information consists of the ability's generation and effect.'''

        answer = ""
        answer += f"**{title(ability)}** "
        answer += f"- **{formatters.generation}**: {objects.abilities.get_generation(ability)}\n"

        json = response.json()
        answer += f"{Fetcher.get_effect(json)}\n"

        return Fetcher.beautify(answer)
    
    def sprite(self, query: str, shiny: bool) -> list | str:
        '''Parses the query then returns the appropiate sprite.'''

        return self.picture(query, self.get_shiny_sprite if shiny else self.get_sprite)

    def art(self, query: str) -> list | str:
        '''Parses the query then returns the Pokemon's official artwork.'''

        return self.picture(query, self.get_art)

    def picture(self, query: str, function_name: Callable) -> list | str:
        '''Finds the Pokemon a query means, then returns its picture using the given getter.'''

        original_query, mon_sanitized_query = query, Fetcher.mon_sanitize(Fetcher.sanitize(query))

        if pokemonic_answer := Fetcher.pokemonic_get(mon_sanitized_query, function_name): return pokemonic_answer

        if mon_sanitized_query in objects.pokemon:
            return function_name(mon_sanitized_query, Fetcher.get(urls.poke_url+mon_sanitized_query))
  
        if closest := objects.pokemon.close_match(mon_sanitized_query):
            return function_name(closest, Fetcher.get(urls.poke_url+closest))

        return f"i don't think {original_query} is a pokemon... check your spelling?"
    
    def get_sprite(self, pokemon: str, response: requests.models.Response) -> list | str:
        '''Returns a URL to the sprite.'''

        url = response.json()['sprites']['front_default']     
        return [url, pokemon] if url else f"sorry, {pokemon} has no sprite right now"
    
    def get_shiny_sprite(self, pokemon: str, response: requests.models.Response) -> list | str:
        '''Returns a URL to the shiny sprite.'''

        shiny_url = response.json()['sprites']['front_shiny']     
        return [shiny_url, pokemon] if shiny_url else f"sorry, {pokemon} has no shiny sprite right now"

    def get_art(self, pokemon: str, response: requests.models.Response) -> list | str:
        '''Returns a URL to the official artwork, a large picture with a transparent background.'''

        url = art_url(response.json())
        return [url, pokemon] if url else f"sorry, {pokemon} has no art right now"
    
    def get_type(self, pokemon: str, response: requests.models.Response) -> list:
        '''Fetches the types from a Pokemon HTTP Response. Returns a list containing the Pokemon's name and types.'''
        
        json = response.json()
        types = json['types']
        answer = []

        answer.append(types[0]['type']['name'])
        if len(types) == 2: answer.append(types[1]['type']['name'])

        return [pokemon, answer]
    
    @staticmethod
    def pokemonic_get(query: str, function: Callable):
        '''Calls and returns the value of the appropiate function if the input parameter is a Pokemon, Pokemon alias, dex number, or flavor.'''

        if query in aliases.alias_map:
            associated = aliases.alias_map[query]
            return function(associated, Fetcher.get(urls.poke_url+associated))
        
        if query.isnumeric():
            mon = objects.pokemon.by_number(query)
            return function(mon, Fetcher.get(urls.poke_url+mon)) if mon else None
                    
        if flavor := objects.pokemon.flavor(query): 
            return function(flavor, Fetcher.get(urls.poke_url+flavor))
        
        return None
    
    @staticmethod
    def request_pokemon(pokemon: str) -> requests.models.Response:
        '''Used for making Pokemon request calls outside of the class.'''

        return Fetcher.get(urls.poke_url+pokemon)

    @staticmethod
    def sanitize(token: str) -> str:
        '''Removes trailing spaces, replaces spaces with dashes.'''

        return token.strip().lower().replace(" ", "-")
    
    @staticmethod
    def mon_sanitize(token: str) -> str:
        '''Rearranges Pokemon with a modifier where the modifier is typed first. For example, token "Mega Alakazam" becomes Alakazam-Mega. Parses queries like "Galarian Zapdos" into "Zapdos-Galar" so the API can recognize it.'''

        tokens = token.split("-")
        
        tokens[0] = nationalities.nat_map.get(tokens[0], tokens[0])

        if (tokens[0] in prefixes.pre_tuple) and (len(tokens) >= 2):
            return "-".join([tokens[1], tokens[0], *tokens[2:]])

        return token
             
    @staticmethod
    def beautify(output: str) -> str:
        '''Helper method to print bot output easily.'''

        return f"{formatters.hr}\n" + output + f"{formatters.hr}"
    
    @staticmethod
    def fuzzy(erroneous: str, correct: str) -> str:
        '''Message for an approximate string match.'''

        return f"ummmm... \"{erroneous}\"? perhaps you meant {correct}?\n"
    
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
    def get_move_effect(json) -> str:
        '''Returns the effect of a move, with the move's real effect chance written in.'''

        effect = Fetcher.get_effect(json)

        return effect if formatters.placeholder not in effect else effect.replace(formatters.placeholder, str(json['effect_chance']) + "%")

    @staticmethod
    def get_extra(url: str | None) -> dict | None:
        '''Requests extra data that an answer can do without. Returns None, instead of raising,
        if there is no URL, PokeAPI can't be reached, or the answer isn't a JSON object.'''

        if not url: return None

        try:
            extra = Fetcher.get(url).json()
        except (requests.RequestException, ValueError):
            return None

        return extra if isinstance(extra, dict) else None

    @staticmethod
    def unknown(query: str) -> str:
        '''Message for a query that matches nothing.'''

        return f"i don't know what \"{query}\" is... check your spelling?"
