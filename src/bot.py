import discord, logging, os, fetch_data, server, random, constants, datetime, io, aiohttp
from discord.ext import commands
from dotenv import load_dotenv
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

class Bot:
    '''The Bot Class represents your Discord Bot.'''

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents, help_command=None)
        self.fetcher = fetch_data.FetchData()
        self.last_seen_channel = {}

        @self.bot.event
        async def on_ready():            
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.event
        async def on_message(message):
            if not message.author.bot:
                self.last_seen_channel[message.author.id] = message.channel
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_member_update(before, after):
            timed_out_now = after.timed_out_until is not None
            was_timed_out = before.timed_out_until is not None and before.timed_out_until > datetime.datetime.now(datetime.UTC)

            if timed_out_now and not was_timed_out:
                total = int((after.timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds())
                hours, rem_min = total // 3600, total % 3600
                minutes, rem_sec = rem_min // 60, rem_min % 60
                duration_str = f"{Bot.plural(hours, 'hour')}, {Bot.plural(minutes, 'minute')}, and {Bot.plural(rem_sec, 'second')}"

                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        moderator_name = entry.user.global_name or entry.user.name
                        break

                victim_name = after.global_name or after.name
                msg = f"{victim_name} was muted by {moderator_name} for {duration_str}"

                channel = (
                    self.last_seen_channel.get(after.id)
                    or after.guild.system_channel
                    or next((c for c in after.guild.text_channels if c.name == "general"), None)
                    or next((c for c in after.guild.text_channels), None)
                )

                if channel:
                    await channel.send(msg)

        @self.bot.command()
        async def dt(ctx, *, query: str):
            await ctx.send(self.fetcher.dt(query))

        @self.bot.command()
        async def pick(ctx, *, query: str):
            await ctx.send(f"i randomly selected: {random.choice(query.split(",")).strip()}")

        @self.bot.command()
        async def randmon(ctx):
            await ctx.send(self.fetcher.dt(str(constants.pokemon.randmon())))

        @self.bot.command()
        async def help(ctx):
            await ctx.send(constants.help)

        @self.bot.command()
        async def muted(ctx):
            answer = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    answer += f"{member.global_name.lower()} is muted for"
                    total = int((member.timed_out_until-datetime.datetime.now(datetime.UTC)).total_seconds())

                    hours, rem_min = total // 3600, total % 3600
                    minutes, rem_sec = rem_min // 60, rem_min % 60

                    answer += f" {Bot.plural(hours, "hour")}, {Bot.plural(minutes, "minute")}, and {Bot.plural(rem_sec, "second")}\n"

            await ctx.send(answer if len(answer) != 0 else "nobody is muted right now")

        @self.bot.command()
        async def define(ctx, *, query: str):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{query.strip()}") as resp:
                    if resp.status != 200:
                        await ctx.send(f"couldn't find a definition for **{query}**")
                        return

                    data = await resp.json()
                    meanings = data[0]["meanings"]

                    answer = f"**{query.lower()}**\n"
                    for meaning in meanings:
                        part = meaning["partOfSpeech"]
                        definition = meaning["definitions"][0]["definition"]
                        answer += f"*{part}* — {definition}\n"

                    await ctx.send(answer)

        @self.bot.command()
        async def wc(ctx):
            async with ctx.typing():
                text = ""
                async for message in ctx.channel.history(limit=1000):
                    if not message.author.bot and not message.content.startswith("!"):
                        text += f" {message.content}"

                if not text.strip():
                    await ctx.send("not enough messages to generate a word cloud")
                    return

                cloud = WordCloud(
                    width=1000,
                    height=500,
                    background_color="black",
                    stopwords=STOPWORDS,
                    colormap="plasma",
                    max_words=150
                ).generate(text)

                buf = io.BytesIO()
                plt.figure(figsize=(10, 5))
                plt.imshow(cloud, interpolation="bilinear")
                plt.axis("off")
                plt.tight_layout(pad=0)
                plt.savefig(buf, format="png", bbox_inches="tight")
                plt.close()
                buf.seek(0)

                await ctx.send(file=discord.File(buf, "wordcloud.png"))

        @self.bot.command()
        async def sprite(ctx, *, query):
            answer = self.fetcher.sprite(query, shiny=False)

            if isinstance(answer, list):
                await ctx.send(file=(await Bot.sprite_handler(answer[0], answer[1])))
            else:
                await ctx.send(answer)

        @self.bot.command()
        async def shiny(ctx, *, query):
            answer = self.fetcher.sprite(query, shiny=True)

            if isinstance(answer, list):
                await ctx.send(file = (await Bot.sprite_handler(answer[0], answer[1])))
            else:
                await ctx.send(answer)

        @self.bot.command()
        async def randsprite(ctx):
            rand_sprite = self.fetcher.sprite(str(constants.pokemon.randmon()), shiny=False)
            await ctx.send(file = (await Bot.sprite_handler(rand_sprite[0], rand_sprite[1])))

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)

    @staticmethod
    def plural(value: int, value_name: str) -> str:
        '''Useful for writing unit names with appropiate plurality.'''

        return f"{str(value)} {value_name}{"s" if value != 1 else ""}"
    
    @staticmethod
    async def sprite_handler(url: str, pokemon: str) -> discord.File:
        '''Returns appropiate sprite based on a given URL and Pokemon.'''
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return discord.File(io.BytesIO(await resp.read()), f'{"shiny-" if "shiny" in url else ""}{pokemon}.png')