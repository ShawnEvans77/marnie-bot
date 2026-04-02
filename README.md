# marnie 

Marnie is a Discord bot for people who love Pokemon! I called her Marnie because who wouldn't want to be a part of Team Yell?

If you have a Discord Server based around Pokemon Showdown and you want a bot emulating that site's command, Marnie is the bot for you!

I try to keep her online as much as I can!

## Installation

Feel free to install her [at this link if you want her in one of your servers!](https://discord.com/oauth2/authorize?client_id=1455036822014001168&permissions=68608&integration_type=0&scope=bot). If you want her in direct messages, send a message to her. This is her profile and tag.

<img src="https://i.imgur.com/iTYDXwZ.png"></img>

If you desire to self-host and customize her to your liking, do these Docker commands:

```
docker build -t marnie .
```

```
docker run marnie
```

If you would prefer not to use Docker, you may do:

```
pip install -r requirements.txt
```

```
py -m src.scripts.main
```

If you would like to run the program's tests, do:

```
py -m tests.tests
```

.env is obviously .gitignore'd by default. Do not commit your API tokens to GitHub! If you want to use her locally, you would need to create .env and put your API Token in there. 

You can change her language by editing language.py. View all supported languages [here](https://pokeapi.co/api/v2/language). Marnie's default language is the Queen's English.
## Usage
Commands are typed in this form:

```
!command query
```

Where command is the name of the command and query is your query. For example, if I wanted her to tell me the weaknesses of the fire type, I would do:

```
!weak fire
```

Note that not all commands will use a query. Some commands, like muted, can be invoked by simply typing !muted.

Marnie implements [fuzzy string matching](https://en.wikipedia.org/wiki/Approximate_string_matching), so she'll still try and parse your typos. 

Here are some examples of what she can output:

<img src="https://i.imgur.com/jT8NyIg.png"></img>
<img src="https://i.imgur.com/om3QHvX.png"></img>
<img src="https://i.imgur.com/gLRHjVb.png">
<img src="https://i.imgur.com/Zgz91u3.png">

## Commands
All of her commands are as follows:

* !**dt** {query} - Returns information on a Pokemon, Pokemon ability, Pokemon item, or Pokemon move.
* !**weak** {type} - Lists weaknesses, resistances, and immunities of a given type. You can query a dual type by sending two types seperated by slashes or commas to the command. For example, !dt fire/water or !dt fire,water.
* !**weak** {pokemon} - Lists weaknesses, resistances, and immunities of a given Pokemon.
* !**pick** {args...} - Selects a random option given a list of options.
* !**randmon** - Returns the information of a random Pokemon.
* !**muted** - Lists all timed out server members and the amount of time they are timed out for.
* !**sprite** {pokemon} - Returns a Pokemon's sprite.
* !**shiny** {pokemon} ** - Returns a Pokemon's shiny sprite.\n" \
* !**randsprite** - Returns a random Pokemon's sprite."

## Motivation

I'm in a Discord Server and we needed a bot that supported these features. I made this bot myself to help out that Discord Server.