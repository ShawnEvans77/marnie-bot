from discord.ext import commands
from ..constants.output import help as h
from ..constants.getters import get_objs
from ..constants.structs import objects
from ..servers import web_server
from dotenv import load_dotenv
from collections import Counter, deque
from io import BytesIO
from PIL import Image
from wordcloud import STOPWORDS, WordCloud
import discord, logging, os, random, datetime, io, aiohttp, re


class Marnie:
    '''The Marnie Class represents your Discord Bot.'''

    wc_stopwords = STOPWORDS.union({
        "im", "ive", "ill", "id", "dont", "didnt", "doesnt", "cant", "couldnt",
        "thats", "theres", "youre", "youve", "youll", "theyre", "weve", "whats",
        "would", "could", "also", "like", "just", "yeah", "yes", "nah", "lol",
        "ok", "okay", "got", "get", "one", "two", "really", "much", "thing",
        "know", "new", "even", "people",
    })
    wc_message_limit = 5000
    wc_cache = {}

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents, help_command=None)

        @self.bot.event
        async def on_ready():
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")

        @self.bot.event
        async def on_message(message):
            Marnie.update_wc_cache_with_message(message)
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_message_delete(message):
            Marnie.invalidate_wc_cache(message.channel.id, message.id)

        @self.bot.event
        async def on_message_edit(before, after):
            Marnie.invalidate_wc_cache(after.channel.id, after.id)

        @self.bot.command()
        async def dt(ctx, *, query: str = None):

            if query is not None:
                await ctx.send(get_objs.fetcher.dt(query))
            else:
                await ctx.send("how can i do ``!dt`` on **nothing**?\n\nyou have to send a query to ``!dt``, silly!\n\nremember, if you wanna use ``!dt``, you type !dt then a Pokemon, Pokemon move, Pokemon ability, or item. for example: ``!dt morpeko``.")

        @self.bot.command()
        async def weak(ctx, *, query: str = None):

            if query is not None:
                split_char = ',' if ',' in query else '/'
                await ctx.send(get_objs.weaker.weak(*query.split(split_char)))
            else:
                await ctx.send("how can i do ``!weak`` on **nothing**?\n\nyou have to send a type or a pokemon to ``!weak``, silly!\n\nremember, if you wanna use the ``!weak`` command, you type ``!weak`` then a type combo or a pokemon. for instance, you could type ``!weak morpeko``, or you could type ``!weak fire/flying``.")

        @self.bot.command()
        async def pick(ctx, *, query: str = None):

            if query is not None:
                await ctx.send(f"i randomly selected: {random.choice(query.split(',')).strip()}")
            else:
                await ctx.send("how can i ``!pick`` from **no options**?\n\nremember, if you wanna use the ``!weak`` command, you type a set of comma separated values after ``!pick``. for example: ``!pick socks, shoes``")

        @self.bot.command()
        async def randmon(ctx):
            await ctx.send(get_objs.fetcher.dt(str(objects.pokemon.randmon())))

        @self.bot.command()
        async def wc(ctx, *, query: str = None):
            async with ctx.typing():
                target_member = None

                if query is not None:
                    if ctx.guild is None:
                        await ctx.send(file=Marnie.wordcloud_status_image())
                        return

                    target_member = Marnie.find_member(ctx.guild, query)
                    if target_member is None:
                        await ctx.send(file=Marnie.wordcloud_status_image())
                        return

                try:
                    frequencies = await Marnie.collect_word_counts(ctx.channel, target_member)
                except discord.Forbidden:
                    await ctx.send(file=Marnie.wordcloud_status_image())
                    return

                if not frequencies:
                    await ctx.send(file=Marnie.wordcloud_status_image())
                    return

                await ctx.send(file=Marnie.wordcloud_image(frequencies))

        @self.bot.command()
        async def help(ctx):
            await ctx.send(h.command)

        @self.bot.command()
        async def muted(ctx):
            answer = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    display_name = member.global_name or member.display_name or member.name
                    answer += f"**{display_name.lower()}** is muted for"
                    total = int((member.timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds())

                    hours, rem_min = total // 3600, total % 3600
                    minutes, rem_sec = rem_min // 60, rem_min % 60

                    answer += f" {Marnie.plural(hours, 'hour')}, {Marnie.plural(minutes, 'minute')}, and {Marnie.plural(rem_sec, 'second')}\n"

            await ctx.send(answer if len(answer) != 0 else "nobody is muted right now")

        @self.bot.command()
        async def sprite(ctx, *, query: str = None):

            if query is not None:
                answer = get_objs.fetcher.sprite(query, shiny=False)
                if isinstance(answer, list):
                    await ctx.send(file=(await Marnie.sprite_handler(*answer)))
                else:
                    await ctx.send(answer)
            else:
                await ctx.send("how can i find a sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!sprite`` command, you type ``!sprite`` then the name of the Pokemon whose sprite you want. for example, ``!sprite pikachu``.")

        @self.bot.command()
        async def shiny(ctx, *, query: str = None):

            if query is not None:
                answer = get_objs.fetcher.sprite(query, shiny=True)
                if isinstance(answer, list):
                    await ctx.send(file=(await Marnie.sprite_handler(*answer)))
                else:
                    await ctx.send(answer)
            else:
                await ctx.send("how can i find a shiny sprite **without knowing** the pokemon to find a sprite for?\n\nremember, if you wanna use the ``!shiny`` command, you type ``!shiny`` then the name of the Pokemon whose shiny sprite you want. for example, ``!shiny goodra``.")

        @self.bot.command()
        async def randsprite(ctx):
            rand_sprite = get_objs.fetcher.sprite(str(objects.pokemon.randmon()), shiny=False)
            await ctx.send(file=(await Marnie.sprite_handler(*rand_sprite)))

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        web_server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)

    @staticmethod
    def plural(value: int, value_name: str) -> str:
        '''Useful for writing unit names with appropiate plurality.'''

        return f"{value} {value_name}{'s' if value != 1 else ''}"

    @staticmethod
    def sanitize_wc_text(text: str) -> str:
        '''Drops URLs and normalizes message text before tokenization.'''

        without_urls = re.sub(r"https?://\S+|www\.\S+", " ", text)
        return without_urls.replace("\n", " ").strip()

    @staticmethod
    def tokenize_wc_text(text: str) -> list[str]:
        '''Returns lowercase word tokens for the word cloud.'''

        normalized_text = text.lower().replace("’", "'")
        tokens = re.findall(r"[a-zA-Z][a-zA-Z'\-]*", normalized_text)
        normalized_tokens = [token.replace("'", "") for token in tokens]
        return [token for token in normalized_tokens if token not in Marnie.wc_stopwords and len(token) > 1]

    @staticmethod
    def tokenize_wc_text_unfiltered(text: str) -> list[str]:
        '''Returns lowercase word tokens without stopword filtering for fallback clouds.'''

        normalized_text = text.lower().replace("’", "'")
        tokens = re.findall(r"[a-zA-Z][a-zA-Z'\-]*", normalized_text)
        normalized_tokens = [token.replace("'", "") for token in tokens]
        return [token for token in normalized_tokens if len(token) > 1]

    @staticmethod
    def find_member(guild: discord.Guild, query: str) -> discord.Member | None:
        '''Finds a guild member by username, display name, or nickname.'''

        cleaned = query.strip().lstrip("@").casefold()

        def names_for(member: discord.Member) -> list[str]:
            return [
                value.casefold()
                for value in [member.name, member.display_name, member.global_name]
                if value
            ]

        exact_matches = [member for member in guild.members if cleaned in names_for(member)]
        if exact_matches:
            return exact_matches[0]

        partial_matches = [
            member for member in guild.members
            if any(cleaned in value for value in names_for(member))
        ]
        if partial_matches:
            return partial_matches[0]

        return None

    @staticmethod
    async def collect_word_counts(channel, target_member: discord.Member | None) -> Counter:
        '''Scans recent accessible history and returns word frequencies.'''

        frequencies = Counter()
        fallback_frequencies = Counter()

        channel_cache = await Marnie.refresh_wc_cache(channel)

        if target_member is None:
            return channel_cache["message_counts"].copy() if channel_cache["message_counts"] else channel_cache["fallback_message_counts"].copy()

        author_counts = channel_cache["author_counts"].get(target_member.id, Counter()).copy()
        fallback_author_counts = channel_cache["fallback_author_counts"].get(target_member.id, Counter()).copy()
        return author_counts if author_counts else fallback_author_counts

    @staticmethod
    def add_message_to_word_counts(message, frequencies: Counter, fallback_frequencies: Counter) -> bool:
        '''Adds one message into the running wc counters.'''

        if message.author.bot or not message.content:
            return False

        cleaned_text = Marnie.sanitize_wc_text(message.content)
        fallback_tokens = Marnie.tokenize_wc_text_unfiltered(cleaned_text)

        if not fallback_tokens:
            return False

        fallback_frequencies.update(fallback_tokens)

        tokens = Marnie.tokenize_wc_text(cleaned_text)
        if tokens:
            frequencies.update(tokens)

        return True

    @staticmethod
    def empty_wc_cache() -> dict:
        '''Creates an empty rolling wc cache entry.'''

        return {
            "messages": deque(),
            "message_counts": Counter(),
            "fallback_message_counts": Counter(),
            "author_counts": {},
            "fallback_author_counts": {},
        }

    @staticmethod
    def build_wc_entry(message) -> dict:
        '''Builds the cached representation for one message in the wc window.'''

        counts = Counter()
        fallback_counts = Counter()
        author_id = None

        if not message.author.bot and message.content:
            cleaned_text = Marnie.sanitize_wc_text(message.content)
            fallback_tokens = Marnie.tokenize_wc_text_unfiltered(cleaned_text)

            if fallback_tokens:
                fallback_counts = Counter(fallback_tokens)
                author_id = message.author.id
                tokens = Marnie.tokenize_wc_text(cleaned_text)
                counts = Counter(tokens)

        return {
            "id": message.id,
            "author_id": author_id,
            "counts": counts,
            "fallback_counts": fallback_counts,
        }

    @staticmethod
    def apply_wc_entry(cache: dict, entry: dict, direction: int):
        '''Applies or removes one cached message entry from aggregate counters.'''

        if entry["author_id"] is None:
            return

        if entry["counts"]:
            counts = entry["counts"]
            cache["message_counts"].update(counts) if direction == 1 else cache["message_counts"].subtract(counts)
            author_counter = cache["author_counts"].setdefault(entry["author_id"], Counter())
            author_counter.update(counts) if direction == 1 else author_counter.subtract(counts)
            if direction == -1:
                cache["message_counts"] += Counter()
                author_counter += Counter()
                if not author_counter:
                    del cache["author_counts"][entry["author_id"]]
        elif entry["fallback_counts"]:
            counts = entry["fallback_counts"]
            cache["fallback_message_counts"].update(counts) if direction == 1 else cache["fallback_message_counts"].subtract(counts)
            author_counter = cache["fallback_author_counts"].setdefault(entry["author_id"], Counter())
            author_counter.update(counts) if direction == 1 else author_counter.subtract(counts)
            if direction == -1:
                cache["fallback_message_counts"] += Counter()
                author_counter += Counter()
                if not author_counter:
                    del cache["fallback_author_counts"][entry["author_id"]]

    @staticmethod
    def add_wc_entry(cache: dict, entry: dict):
        '''Adds one message entry and trims the rolling window back to the limit.'''

        cache["messages"].append(entry)
        Marnie.apply_wc_entry(cache, entry, direction=1)

        while len(cache["messages"]) > Marnie.wc_message_limit:
            removed_entry = cache["messages"].popleft()
            Marnie.apply_wc_entry(cache, removed_entry, direction=-1)

    @staticmethod
    async def rebuild_wc_cache(channel) -> dict:
        '''Rebuilds the cache so it exactly matches the latest wc window.'''

        cache = Marnie.empty_wc_cache()
        recent_messages = [message async for message in channel.history(limit=Marnie.wc_message_limit)]

        for message in reversed(recent_messages):
            Marnie.add_wc_entry(cache, Marnie.build_wc_entry(message))

        Marnie.wc_cache[channel.id] = cache
        return cache

    @staticmethod
    async def refresh_wc_cache(channel) -> dict:
        '''Refreshes the rolling channel cache.'''

        cache = Marnie.wc_cache.get(channel.id)
        if cache is None:
            return await Marnie.rebuild_wc_cache(channel)

        newest_cached_id = cache["messages"][-1]["id"] if cache["messages"] else None
        new_messages = [
            message async for message in channel.history(
                limit=Marnie.wc_message_limit,
                after=discord.Object(id=newest_cached_id) if newest_cached_id else None,
            )
        ]

        if len(new_messages) >= Marnie.wc_message_limit:
            return await Marnie.rebuild_wc_cache(channel)

        for message in reversed(new_messages):
            Marnie.add_wc_entry(cache, Marnie.build_wc_entry(message))

        return cache

    @staticmethod
    def update_wc_cache_with_message(message):
        '''Incrementally updates an existing channel wc cache with a new message.'''

        cache = Marnie.wc_cache.get(message.channel.id)
        if cache is None:
            return

        if any(entry["id"] == message.id for entry in cache["messages"]):
            return

        Marnie.add_wc_entry(cache, Marnie.build_wc_entry(message))

    @staticmethod
    def invalidate_wc_cache(channel_id: int, message_id: int):
        '''Drops a channel cache if a cached message was edited or deleted.'''

        cache = Marnie.wc_cache.get(channel_id)
        if cache is None:
            return

        for entry in cache["messages"]:
            if entry["id"] == message_id:
                del Marnie.wc_cache[channel_id]
                break

    @staticmethod
    def wc_color_func(*args, **kwargs) -> str:
        '''Color palette for the word cloud.'''

        palette = [
            "#ff76aa",
            "#ff9bc4",
            "#ffc2dd",
            "#f7f7fb",
            "#d7d9e4",
            "#c3a6ff",
        ]
        return random.choice(palette)

    @staticmethod
    def wordcloud_status_image() -> discord.File:
        '''Builds a blank fallback image for wc failures or empty scans.'''

        canvas = Image.new("RGB", (1200, 700), "#1f1f28")
        buffer = BytesIO()
        canvas.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="wc.png")

    @staticmethod
    def wordcloud_image(frequencies: Counter) -> discord.File:
        '''Builds the final word cloud image.'''

        cloud = WordCloud(
            width=1800,
            height=1100,
            background_color="#1f1f28",
            collocations=False,
            max_words=180,
            margin=24,
            prefer_horizontal=0.9,
            min_font_size=14,
        ).generate_from_frequencies(frequencies)

        cloud = cloud.recolor(color_func=Marnie.wc_color_func, random_state=17)
        cloud_image = cloud.to_image().convert("RGB")

        buffer = BytesIO()
        cloud_image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="wc.png")

    @staticmethod
    async def sprite_handler(url: str, pokemon: str) -> discord.File:
        '''Returns appropiate sprite based on a given URL and Pokemon.'''

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return discord.File(io.BytesIO(await resp.read()), f'{"shiny-" if "shiny" in url else ""}{pokemon}.png')
