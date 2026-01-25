import fetch_data as f

x = f.FetchData()

tests = ["blaze", "fire punch", "heavy duty boots", "poke-ball", "arceus", "tera shell", "dragon dance", "swords dance", "pikachu", "diance", "diance-mega", "leftovers", "choice band", "choice scarf"]

for test in tests:
    print(x.dt(test))
    print()