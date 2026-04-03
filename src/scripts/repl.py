from ..constants.getters import get_objs

print("************************************************************************")
print("Welcome to the Marnie REPL!")
print("Use this to test !dt and !weak without deploying the bot to production.")
print()
print("Enter your prompt after the >>>. Type exit() to quit.")
prompt = input(">>> ").lower().strip()

while prompt != "exit()":

    tokens = prompt.split(" ", maxsplit=2)

    dt = "!dt"
    weak = "!weak"
    commands = [dt, weak]
    command = tokens[0]
    
    if command not in commands:
        print("error: please start your message with !dt or !weak.")
    elif len(tokens) == 1:
        print("error: please enter a query after your command.")
    elif command == dt:
        print(get_objs.fetcher.dt(prompt[prompt.index(" ")+1:]))
    elif command == weak:
        query = prompt[prompt.index(" ")+1:]
        split_char = ',' if ',' in prompt[prompt.index(" ")+1:] else '/'
        type_tokens = prompt[prompt.index(" ")+1:].split(split_char)
        print(get_objs.weaker.weak(*type_tokens))

    print()
    prompt = input(">>> ").lower().strip()  

print()
print("Thanks for using the Marnie repl.")
print("******************************************")