# marnie 

Marnie is a Discord bot for people who love Pokemon. 

She's called Marnie because who wouldn't want to be a part of Team Yell?

The bot scrapes PokeAPI data to provide updated information on Pokemon game data. Useful if you have a Discord Server
based around Pokemon Showdown and you want your own lightweight port of the website's commands. The primary information returned for queries on a Pokemon species are their stats, abilities, weight, generation, and type. Simple descriptions are returned for items and abilities. Generation, Power, PP, Accuracy, Type, and Damage Type are returned for moves. 

The bot is typically online, but due to me being limited to free hosting services sometimes she is offline. There is a "flaskless" branch of this repository that does not implement a Flask Server if you want this application to be more lightweight.

## Installation

Feel free to install her [at this link if you want her in one of your servers.](https://discord.com/oauth2/authorize?client_id=1455036822014001168&permissions=68608&integration_type=0&scope=bot). If you want her in direct messages, send a message to her. This is her profile and tag.

<img src="https://raw.githubusercontent.com/ShawnEvans77/marnie-bot/refs/heads/main/marnie_prof.png"></img>

If you desire to host an instance of her yourself to self-host and customize her to your liking, do these Docker commands:

```
docker build -t marnie .
```

```
docker run marnie
```

If you would prefer not to use Docker, you may do:

```
git clone https://github.com/ShawnEvans77/marnie-bot
```
```
pip install -r requirements.txt
```
```
py src/main.py
```

.env is obviously .gitignore'd by default. Make sure to create it and put in your DISCORD_ENV if you want to host the bot yourself. 

## Usage
See below. The bot implements [fuzzy string matching](https://en.wikipedia.org/wiki/Approximate_string_matching), so if you make a typo it will still try to parse what you said. You can invoke Pokemon by their name or dex number. I have plans to implement a dexsearch algorithim to find Pokemon matching a specific property. Commands are invoked by typing !dt. 

If you're cloning this project, feel free to change the language by altering the language constants variable. "es" for Spanish. "fr" for French. View all supported languages [here](https://pokeapi.co/api/v2/language). The bot is the Queen's English by default.

You can view a list of all currently muted server members with !muted. You can view a Pokemon's non-shiny and shiny sprite with !sprite and !shiny, respectively.

Type !help to get a list of commands. The bot also supports !randmon for selecting a random Pokemon and !pick for picking a random option from a list of options. !randsprite returns an image of a random Pokemon.

<img src="https://raw.githubusercontent.com/ShawnEvans77/marnie-bot/refs/heads/main/marnie.png"></img>
<img src="https://raw.githubusercontent.com/ShawnEvans77/marnie-bot/refs/heads/main/marnie_2.png"></img>
<img src="https://raw.githubusercontent.com/ShawnEvans77/marnie-bot/refs/heads/main/marnie-3.png"></img>

## Motivation

There are so many abhorrent vibe-coded ChatGPT wrapper SaaS B2B products which contain security lapses, so I wanted to go back to basics and develop something from scratch on my own. It's nothing crazy, but I'm proud of it. I learned a lot making this.