# marnie bot 👢

Marnie Bot is a Discord bot that allows you to fetch data on Pokemon, Pokemon items, Pokemon moves, and Pokemon abilities. No vibe coding was used in this project and this isn't a ChatGPT wrapper. It is called Marnie Bot because who wouldn't want to be a part of Team Yell?

Feel free to clone the source code to set up your own version of the bot.

The bot scrapes PokeAPI data to provide updated information on Pokemon game data. Useful if you have a Discord Server
based around Pokemon Showdown, and you want your own lightweight port of the website's commands. The primary information returned for queries on a Pokemon species are their stats, abilities, and type.

The bot is currently hosted 24/7 using the Render Cloud Hosting Platform. Please contact me if it is not online. 

## Installation

Feel free to install her [at this link](https://discord.com/oauth2/authorize?client_id=1455036822014001168&permissions=68608&integration_type=0&scope=bot). The bot can run in servers or direct messages.

Or, alternatively, if you desire to host an instance of herself to customize her to your liking, do:

```
docker build -t marnie .
```

```
docker run marnie
```

.env is obviously .gitignore'd by default. 

## Usage

See below. The bot implements [fuzzy string matching](https://en.wikipedia.org/wiki/Approximate_string_matching), so if you make
a typo it will still try to parse what you said. You can invoke Pokemon by their name or dex number. I have plans to implement a dexsearch algorithim to find Pokemon matching a specific property. Commands are invoked by typing !dt. You can also type !wiki to search up Bulbapedia articles.

<img src="https://raw.githubusercontent.com/ShawnEvans77/marnie-bot/refs/heads/main/marnie.png"></img>

## Motivation

There are so many abhorrent vibe-coded ChatGPT wrapper SaaS B2B products which contain security lapses. I wanted to go back to basics and develop something from scratch on my own. It's nothing crazy, but I'm proud of it. I learned a lot making this.