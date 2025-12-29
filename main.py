import requests

base_url = "https://pokeapi.co/api/v2"

print("--------------------------------------------------------")
print("Welcome to snom bot! Type /dt [pokemon name] to get data on that Pokemon.")
print("Type exit() to terminate snom bot.")
print("--------------------------------------------------------")

running = True

stat_names = ["HP", "ATK", "DEF", "SP. ATK", "SP. DEF", "SPEED"]

while running:
    print(">>> ", end="")

    command = input()

    if command == "exit()":
        running = False
    elif command[:3] == "/dt" or command[:3] == "!dt":
        name = command.split(" ")[1]
        url = f"{base_url}/pokemon/{name}"

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()['stats']

            print(f"{name}'s stats are as follows: ")

            for i in range(len(data)):
                print( f"{stat_names[i]}: {data[i]['base_stat']}")

        else:
            print(f"Error! The Pokemon {name} was not found.")

    else:
        print("ERROR: Invalid command. Please try again!")