import fetch_data as f

x = f.FetchData()

tests = ["445", "321", "112", "001", "fishious-rend", "blaze", "fire punch", "heavy duty boots", "poke-ball", "arceus", "tera shell", "dragon dance", "swords dance", "pikachu", "diance", "diance-mega", "leftovers", "choice band", "choice scarf",
         "bulbasaur", "vensaur", "mega rayquaza", "cinccino"]

for test in tests:
    print(x.dt(test))
    print()