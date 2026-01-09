import pokedex as pd

class Bulbapedia:
    '''A class representing Bulbapedia. You can query Pokemon information and recieve Bulbapedia pages.'''

    dex = pd.Pokedex()

    def __init__(self):
        pass

    def get_mon(self, pokemon: str) -> str:

        if pokemon in Bulbapedia.dex or Bulbapedia.dex.flavor_exists(pokemon):
            return f"https://bulbapedia.bulbagarden.net/wiki/{pokemon}_(Pok%C3%A9mon)"
        else:
            return "that pokemon does not exist"