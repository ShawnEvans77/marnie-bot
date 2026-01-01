# marnie bot 👢

Marnie Bot is a Discord bot that allows you to fetch data on Pokemon and Pokemon items. No vibe coding was used in this project. This isn't a ChatGPT wrapper, all code is originally written by me. It is called Marnie Bot because who wouldn't want to be a part of Team Yell?

Feel free to clone the source code to set up your own version of the bot.

The bot scrapes PokeAPI data to provide updated information on Pokemon Base Stat Totals. Useful if you have a Discord Server
based around Pokemon Showdown, and you want your own lightweight port of the website's commands.

The bot is mostly hosted on my own machine, but I am looking for proper hosting.

## Installation

Feel free to install her at this [link](https://discord.com/oauth2/authorize?client_id=1455036822014001168&permissions=68608&integration_type=0&scope=bot).

Or, alternatively, if you desire to host an instance of herself to customize her to your liking, do:

```
docker build -t marnie .
```

```
docker run marnie
```

Don't be silly and commit your .env publicly! 

## Usage

See below. The bot implements [fuzzy string matching](https://en.wikipedia.org/wiki/Approximate_string_matching), so if you make
a typo it will still try to parse what you said. As of now, the bot supports Pokemon, Pokemon item, and Pokemon ability queries. I have plans to implement a dexsearch algorithim to find Pokemon matching a specific property.

<img src="https://github.com/ShawnEvans77/marnie-bot/blob/main/image.png?raw=true"></img>

## Motivation

There are so many abhorrent vibe-coded ChatGPT wrapper SaaS B2B products which contain security lapses. I wanted to go back to basics and develop something from scratch on my own. It's nothing crazy, but I'm proud of it. I learned a lot making this.