import fetch_data

x = fetch_data.FetchData()

print("******************************************")
print("Welcome to the Marnie Repl, used for testing !dt without deploying the bot to production.")

print(">>> Enter your command. Type exit() to quit.")
query = input(">>> ").lower().strip()

while query != "exit()":
    print(x.dt(query))
    print(">>> Enter your command. Type exit() to quit.")
    query = input(">>> ").lower().strip()  

print("Thanks for using the Marnie repl.")
print("******************************************")