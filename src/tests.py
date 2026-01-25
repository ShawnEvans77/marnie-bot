import fetch_data as f

x = f.FetchData()

tests = ["blaze", "fire punch", "heavy duty boots", "poke-ball", "arceus", "tera shell", "dragon dance", "swords dance", "pikachu"]

for test in tests:
    print(x.dt(test))
    print()