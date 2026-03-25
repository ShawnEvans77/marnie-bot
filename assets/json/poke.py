import json

with open("learnsets.json", "r") as f:

    x = json.load(f)
    y = x.keys()


    with open("pokemon.txt", "a") as v:

        for k in y:
            v.write(f"{k}\n")
