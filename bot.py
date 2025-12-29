import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import fetch_data as f

load_dotenv()
token = os.getenv('DISCORD_ENV')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"we are ready to go in, {bot.user.name}")

#!dt

@bot.command()
async def dt(ctx, *, pokemon):

    if " " in pokemon.strip():
        await ctx.send("there are no pokemon with first and last names")
    else:
        await ctx.send(f.FetchData().dt(pokemon))

bot.run(token, log_handler=handler, log_level=logging.DEBUG)