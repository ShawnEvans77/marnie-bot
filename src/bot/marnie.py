from discord.ext import commands
from ..constants.api import urls
from ..constants.output import aliases, wordcloud as wc
from . import help_menu
from ..constants.getters import get_objs
from ..constants.structs import objects
from ..servers import web_server
from ..utils.fetcher import Fetcher
from dotenv import load_dotenv
from collections import Counter, deque
from io import BytesIO
from PIL import Image
from thefuzz import fuzz
from wordcloud import WordCloud
import discord, logging, os, random, datetime, io, aiohttp, re, asyncio, unicodedata

class Marnie:
    '''The Marnie Class represents your Discord Bot.'''

    command_prefix = '!'
    wc_stopwords = wc.stopwords
    wc_message_limit = 10000
    wc_token_pattern = re.compile(r"[^\W\d_][^\W_]*(?:['\-][^\W_]+)*")
    wc_cache = {}
    wc_locks = {}
    wc_warm_queue = None
    wc_warm_task = None
    wc_warm_pending = set()
    wc_warm_skipped = set()
    top_chatter_count = 3
    wtp_timeout = 30
    wtp_fuzzy_threshold = 85
    wtp_pick_attempts = 5
    wtp_canvas_size = 512
    wtp_sprite_box = 400
    wtp_background = "#ff76aa"
    wtp_active_channels = set()
    wtp_species_ids = None
    last_spoken_channels = {}
    mute_cease_tasks = {}

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_ENV')
        self.handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        self.bot = commands.Bot(command_prefix=Marnie.command_prefix, intents=self.intents, help_command=None)

        @self.bot.event
        async def on_ready():
            print(f"-------------------------------")
            print(f"marnie bot fully operational! <3")
            print(f"-------------------------------")
            Marnie.schedule_existing_mute_ceases(self.bot)

        @self.bot.event
        async def on_message(message):
            Marnie.remember_last_spoken_channel(message)
            Marnie.update_wc_cache_with_message(message)
            Marnie.schedule_wc_warmup(message.channel)
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_raw_message_edit(payload):
            Marnie.edit_wc_cache_message(payload.channel_id, payload.message)

        @self.bot.event
        async def on_raw_message_delete(payload):
            Marnie.delete_wc_cache_messages(payload.channel_id, [payload.message_id])

        @self.bot.event
        async def on_raw_bulk_message_delete(payload):
            Marnie.delete_wc_cache_messages(payload.channel_id, payload.message_ids)

        @self.bot.event
        async def on_member_update(before, after):
            was_timed_out = Marnie.is_timed_out(before)
            is_timed_out = Marnie.is_timed_out(after)

            if was_timed_out and not is_timed_out:
                Marnie.cancel_mute_cease(after)
                await Marnie.announce_mute_cease(after)
                return

            if was_timed_out and is_timed_out:
                if before.timed_out_until != after.timed_out_until:
                    Marnie.schedule_mute_cease(after)
                return

            if not is_timed_out:
                return

            await Marnie.announce_mute_start(after)
            Marnie.schedule_mute_cease(after)

        @self.bot.event
        async def on_member_remove(member):
            Marnie.cancel_mute_cease(member)
            Marnie.last_spoken_channels.pop((member.guild.id, member.id), None)

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
        async def id(ctx, *, query: str = None):
            if query is None:
                await ctx.send(f"your discord id is ``{ctx.author.id}``.")
                return

            user = Marnie.find_member(ctx.guild, query) if ctx.guild is not None else Marnie.find_user(self.bot.users, query)
            if user is None:
                await ctx.send(f"i couldn't find anybody named \"{query}\"... check their spelling?")
                return

            display_name = getattr(user, "display_name", None) or user.global_name or user.name
            await ctx.send(f"**{display_name}**'s discord id is ``{user.id}``.")

        @self.bot.command()
        async def wc(ctx, *, query: str = None):
            async with ctx.typing():
                target_member = None

                if query is not None:
                    if ctx.guild is None:
                        await ctx.send("error: i can only look up a user's messages inside a server.")
                        return

                    target_member = Marnie.find_member(ctx.guild, query)
                    if target_member is None:
                        await ctx.send(f"error: user \"{query}\" not recognized.")
                        return

                try:
                    frequencies = await Marnie.collect_word_counts(ctx.channel, target_member)
                except discord.Forbidden:
                    await ctx.send(file=Marnie.wordcloud_status_image())
                    return

                if not frequencies:
                    if target_member is not None:
                        display_name = target_member.display_name or target_member.global_name or target_member.name
                        await ctx.send(f"error: {display_name}'s messages do not exist in the last {Marnie.wc_message_limit} messages.")
                    else:
                        await ctx.send(file=Marnie.wordcloud_status_image())
                    return

                await ctx.send(file=await asyncio.to_thread(Marnie.wordcloud_image, frequencies))

        @self.bot.command()
        async def help(ctx):
            if not ctx.channel.permissions_for(ctx.me).embed_links:
                for text_page in help_menu.build_text_pages(Marnie.command_prefix):
                    await ctx.send(text_page)
                return

            avatar_url = self.bot.user.display_avatar.url if self.bot.user is not None else None
            menu = help_menu.HelpMenu(help_menu.build_embeds(Marnie.command_prefix, avatar_url))
            menu.message = await ctx.send(embed=menu.embeds[0], view=menu)

        @self.bot.command()
        async def muted(ctx):
            answer = ""

            for member in ctx.guild.members:
                if member.is_timed_out():
                    present_member = await Marnie.fetch_fresh_member(ctx.guild, member.id)
                    if present_member is None or not Marnie.is_timed_out(present_member):
                        continue

                    display_name = Marnie.display_name(present_member)
                    answer += f"**{display_name.lower()}** is muted for"
                    answer += f" {Marnie.mute_duration(present_member.timed_out_until)}\n"

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

        @self.bot.command()
        async def art(ctx, *, query: str = None):

            if query is not None:
                answer = get_objs.fetcher.art(query)
                if isinstance(answer, list):
                    await ctx.send(file=(await Marnie.sprite_handler(*answer)))
                else:
                    await ctx.send(answer)
            else:
                await ctx.send("how can i find art **without knowing** the pokemon to find art for?\n\nremember, if you wanna use the ``!art`` command, you type ``!art`` then the name of the Pokemon whose art you want. for example, ``!art morpeko``.")

        @self.bot.command()
        async def randart(ctx):
            answer = get_objs.fetcher.art(str(random.randint(1, objects.pokemon.get_num_pokemon())))
            if isinstance(answer, list):
                await ctx.send(file=(await Marnie.sprite_handler(*answer)))
            else:
                await ctx.send(answer)

        @self.bot.command()
        async def wtp(ctx):
            if ctx.channel.id in Marnie.wtp_active_channels:
                await ctx.send("a round of who's that pokemon is already going on here! type your guess.")
                return

            Marnie.wtp_active_channels.add(ctx.channel.id)

            try:
                async with ctx.typing():
                    wtp_round = await Marnie.fetch_wtp_round()

                if wtp_round is None:
                    await ctx.send("sorry, i couldn't find a pokemon to show right now... try ``!wtp`` again in a bit?")
                    return

                await ctx.send(
                    f"**who's that pokemon?** type its name! you have {Marnie.wtp_timeout} seconds.",
                    file=discord.File(BytesIO(wtp_round["silhouette"]), filename="wtp.png"),
                )

                def is_correct(message) -> bool:
                    return (
                        message.channel.id == ctx.channel.id
                        and not message.author.bot
                        and Marnie.wtp_guess_matches(message.content, wtp_round)
                    )

                reveal = discord.File(BytesIO(wtp_round["reveal"]), filename="wtp-answer.png")

                try:
                    winner = await self.bot.wait_for("message", check=is_correct, timeout=Marnie.wtp_timeout)
                except asyncio.TimeoutError:
                    await ctx.send(f"time's up! it's **{wtp_round['name']}**!", file=reveal)
                else:
                    await ctx.send(f"it's **{wtp_round['name']}**! {winner.author.mention} got it!", file=reveal)
            finally:
                Marnie.wtp_active_channels.discard(ctx.channel.id)

        @self.bot.command()
        async def top(ctx):
            async with ctx.typing():
                try:
                    channel_cache = await Marnie.refresh_wc_cache(ctx.channel)
                except discord.Forbidden:
                    await ctx.send("error: i can't read this channel's message history.")
                    return

                def name_for(user_id: int) -> str | None:
                    user = ctx.guild.get_member(user_id) if ctx.guild is not None else self.bot.get_user(user_id)
                    return Marnie.display_name(user) if user is not None else None

                await ctx.send(
                    Marnie.top_chatters_message(channel_cache, name_for),
                    allowed_mentions=discord.AllowedMentions.none(),
                )

    def start(self):
        '''Makes the bot to go online and start accepting commands.'''

        web_server.keep_alive()
        self.bot.run(self.token, log_handler=self.handler, log_level=logging.DEBUG)

    @staticmethod
    def plural(value: int, value_name: str) -> str:
        '''Useful for writing unit names with appropiate plurality.'''

        return f"{value} {value_name}{'s' if value != 1 else ''}"

    @staticmethod
    def display_name(user) -> str:
        '''Returns a user's best available display name.'''

        return user.global_name or getattr(user, "display_name", None) or user.name

    @staticmethod
    def is_timed_out(member: discord.Member) -> bool:
        '''Returns whether a member is currently timed out.'''

        return member.timed_out_until is not None and member.timed_out_until > datetime.datetime.now(datetime.UTC)

    @staticmethod
    def mute_duration(timed_out_until: datetime.datetime) -> str:
        '''Formats a timeout duration the same way the muted command does.'''

        total = max(0, int((timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds()))
        days, rem_hours = total // 86400, total % 86400
        hours, rem_min = rem_hours // 3600, rem_hours % 3600
        minutes, rem_sec = rem_min // 60, rem_min % 60
        duration_parts = []

        if days > 0:
            duration_parts.append(Marnie.plural(days, 'day'))
        if hours > 0:
            duration_parts.append(Marnie.plural(hours, 'hour'))
        if minutes > 0:
            duration_parts.append(Marnie.plural(minutes, 'minute'))
        if rem_sec > 0 or not duration_parts:
            duration_parts.append(Marnie.plural(rem_sec, 'second'))

        if len(duration_parts) == 1:
            return duration_parts[0]

        if len(duration_parts) == 2:
            return " and ".join(duration_parts)

        return f"{', '.join(duration_parts[:-1])}, and {duration_parts[-1]}"

    @staticmethod
    def remember_last_spoken_channel(message):
        '''Stores the last server channel a member spoke in.'''

        if message.guild is None or message.author.bot:
            return

        Marnie.last_spoken_channels[(message.guild.id, message.author.id)] = message.channel.id

    @staticmethod
    def can_send(channel, guild: discord.Guild) -> bool:
        '''Returns whether Marnie can send messages in a channel.'''

        if channel is None or guild.me is None:
            return False

        permissions = channel.permissions_for(guild.me)
        return permissions.view_channel and (permissions.send_messages or getattr(permissions, "send_messages_in_threads", False))

    @staticmethod
    def mute_announcement_channel(guild: discord.Guild, member: discord.Member):
        '''Finds the best channel for announcing a member timeout.'''

        channel_id = Marnie.last_spoken_channels.get((guild.id, member.id))
        get_channel_or_thread = getattr(guild, "get_channel_or_thread", None)
        channel = get_channel_or_thread(channel_id) if get_channel_or_thread and channel_id else guild.get_channel(channel_id)

        if Marnie.can_send(channel, guild):
            return channel

        general = discord.utils.get(guild.text_channels, name="general")
        return general if Marnie.can_send(general, guild) else None

    @staticmethod
    def mute_task_key(member: discord.Member) -> tuple[int, int]:
        '''Returns the cache key for a member's scheduled mute cease task.'''

        return (member.guild.id, member.id)

    @staticmethod
    def cancel_mute_cease(member: discord.Member):
        '''Cancels a scheduled mute cease announcement for a member.'''

        task = Marnie.mute_cease_tasks.pop(Marnie.mute_task_key(member), None)
        if task is not None:
            task.cancel()

    @staticmethod
    def schedule_mute_cease(member: discord.Member):
        '''Schedules a mute cease announcement for when the current timeout expires.'''

        if member.timed_out_until is None:
            return

        Marnie.cancel_mute_cease(member)
        task = asyncio.create_task(Marnie.announce_mute_cease_after_timeout(member.guild, member.id, member.timed_out_until))
        Marnie.mute_cease_tasks[Marnie.mute_task_key(member)] = task

    @staticmethod
    def schedule_existing_mute_ceases(bot: commands.Bot):
        '''Schedules mute cease announcements for timed-out members already in cache.'''

        for guild in bot.guilds:
            for member in guild.members:
                if Marnie.is_timed_out(member):
                    Marnie.schedule_mute_cease(member)

    @staticmethod
    async def fetch_fresh_member(guild: discord.Guild, member_id: int) -> discord.Member | None:
        '''Fetches a fresh member object when possible.'''

        try:
            return await guild.fetch_member(member_id)
        except discord.NotFound:
            return None
        except (discord.Forbidden, discord.HTTPException):
            return guild.get_member(member_id)

    @staticmethod
    async def announce_mute_cease_after_timeout(guild: discord.Guild, member_id: int, timed_out_until: datetime.datetime):
        '''Sleeps until a timeout expires, then announces if the member is no longer muted.'''

        delay = max(0, (timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds())

        try:
            await asyncio.sleep(delay)
            member = await Marnie.fetch_fresh_member(guild, member_id)
            if member is not None and not Marnie.is_timed_out(member):
                await Marnie.announce_mute_cease(member)
        except asyncio.CancelledError:
            return
        finally:
            key = (guild.id, member_id)
            if Marnie.mute_cease_tasks.get(key) is asyncio.current_task():
                Marnie.mute_cease_tasks.pop(key, None)

    @staticmethod
    async def announce_mute_start(member: discord.Member):
        '''Announces that a member was timed out.'''

        channel = Marnie.mute_announcement_channel(member.guild, member)
        if channel is None:
            return

        muted_name = Marnie.display_name(member).lower()
        duration = Marnie.mute_duration(member.timed_out_until)

        await channel.send(
            f"**{muted_name}** was muted for {duration}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @staticmethod
    async def announce_mute_cease(member: discord.Member):
        '''Announces that a member is no longer timed out.'''

        channel = Marnie.mute_announcement_channel(member.guild, member)
        if channel is None:
            return

        muted_name = Marnie.display_name(member).lower()
        await channel.send(
            f"**{muted_name}** is no longer muted",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @staticmethod
    def sanitize_wc_text(text: str) -> str:
        '''Drops URLs and normalizes message text before tokenization.'''

        without_urls = re.sub(r"https?://\S+|www\.\S+", " ", text)
        return without_urls.replace("\n", " ").strip()

    @staticmethod
    def tokenize_wc_text_unfiltered(text: str) -> list[str]:
        '''Returns lowercase word tokens without stopword filtering for fallback clouds.

        Words may contain any letters (so "Pokémon" stays whole) and digits after the
        first letter. Inner apostrophes and hyphens are kept; stray ones at the edges are not.'''

        normalized_text = text.lower().replace("’", "'")
        normalized_tokens = [token.replace("'", "") for token in Marnie.wc_token_pattern.findall(normalized_text)]
        return [token for token in normalized_tokens if len(token) > 1]

    @staticmethod
    def tokenize_wc_text(text: str) -> list[str]:
        '''Returns lowercase word tokens for the word cloud, without stopwords.'''

        return Marnie.filter_wc_stopwords(Marnie.tokenize_wc_text_unfiltered(text))

    @staticmethod
    def filter_wc_stopwords(tokens: list[str]) -> list[str]:
        '''Drops stopwords from an already-tokenized message.'''

        return [token for token in tokens if token not in Marnie.wc_stopwords]

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
    def find_user(users, query: str) -> discord.User | None:
        '''Finds a Discord user by username or global name outside a guild context.'''

        cleaned = query.strip().lstrip("@").casefold()

        def names_for(user: discord.User) -> list[str]:
            return [
                value.casefold()
                for value in [user.name, user.global_name]
                if value
            ]

        exact_matches = [user for user in users if cleaned in names_for(user)]
        if exact_matches:
            return exact_matches[0]

        partial_matches = [
            user for user in users
            if any(cleaned in value for value in names_for(user))
        ]
        if partial_matches:
            return partial_matches[0]

        return None

    @staticmethod
    async def collect_word_counts(channel, target_member: discord.Member | None) -> Counter:
        '''Brings the channel's wc cache up to date and returns word frequencies.'''

        channel_cache = await Marnie.refresh_wc_cache(channel)

        if target_member is None:
            return (channel_cache["message_counts"] or channel_cache["fallback_message_counts"]).copy()

        author_counts = channel_cache["author_counts"].get(target_member.id)
        if author_counts:
            return author_counts.copy()

        return channel_cache["fallback_author_counts"].get(target_member.id, Counter()).copy()

    @staticmethod
    def empty_wc_cache() -> dict:
        '''Creates an empty rolling wc cache entry.'''

        return {
            "messages": deque(),
            "by_id": {},
            "newest_id": None,
            "chatter_counts": Counter(),
            "message_counts": Counter(),
            "fallback_message_counts": Counter(),
            "author_counts": {},
            "fallback_author_counts": {},
        }

    @staticmethod
    def build_wc_entry(message) -> dict:
        '''Builds the cached representation for one message in the wc window.

        Bot messages, empty messages, and commands count toward the window but add no words.
        A message made only of stopwords is stored as a fallback entry.
        chatter_id is who gets credit for the message in !top: any non-bot message that is
        not a command, even one with no words (like an image).'''

        chatter_id = None
        author_id = None
        counts = None
        fallback = False
        content = message.content or ""

        if not message.author.bot and not content.startswith(Marnie.command_prefix):
            chatter_id = message.author.id
            all_tokens = Marnie.tokenize_wc_text_unfiltered(Marnie.sanitize_wc_text(content))

            if all_tokens:
                author_id = message.author.id
                tokens = Marnie.filter_wc_stopwords(all_tokens)
                fallback = not tokens
                counts = Counter(tokens or all_tokens)

        return {
            "id": message.id,
            "chatter_id": chatter_id,
            "author_id": author_id,
            "counts": counts,
            "fallback": fallback,
        }

    @staticmethod
    def adjust_wc_counter(counter: Counter, counts: Counter, direction: int):
        '''Adds (direction=1) or removes (direction=-1) counts, dropping words that reach zero.'''

        for word, amount in counts.items():
            new_amount = counter.get(word, 0) + amount * direction
            if new_amount > 0:
                counter[word] = new_amount
            else:
                counter.pop(word, None)

    @staticmethod
    def apply_wc_entry(cache: dict, entry: dict, direction: int):
        '''Applies or removes one cached message entry from aggregate counters.'''

        if entry["chatter_id"] is not None:
            Marnie.adjust_wc_counter(cache["chatter_counts"], {entry["chatter_id"]: 1}, direction)

        if entry["author_id"] is None:
            return

        if entry["fallback"]:
            total_counts, author_counters = cache["fallback_message_counts"], cache["fallback_author_counts"]
        else:
            total_counts, author_counters = cache["message_counts"], cache["author_counts"]

        Marnie.adjust_wc_counter(total_counts, entry["counts"], direction)

        author_counter = author_counters.setdefault(entry["author_id"], Counter())
        Marnie.adjust_wc_counter(author_counter, entry["counts"], direction)
        if not author_counter:
            del author_counters[entry["author_id"]]

    @staticmethod
    def add_wc_message(cache: dict, message) -> bool:
        '''Adds one message to the rolling window, unless it is already there, then trims the window back to the limit.'''

        if message.id in cache["by_id"]:
            return False

        entry = Marnie.build_wc_entry(message)
        cache["messages"].append(entry)
        cache["by_id"][entry["id"]] = entry
        if cache["newest_id"] is None or entry["id"] > cache["newest_id"]:
            cache["newest_id"] = entry["id"]
        Marnie.apply_wc_entry(cache, entry, direction=1)

        while len(cache["messages"]) > Marnie.wc_message_limit:
            removed_entry = cache["messages"].popleft()
            cache["by_id"].pop(removed_entry["id"], None)
            Marnie.apply_wc_entry(cache, removed_entry, direction=-1)

        return True

    @staticmethod
    def wc_lock(channel_id: int) -> asyncio.Lock:
        '''Returns the lock that keeps one channel's cache from being fetched twice at once.'''

        lock = Marnie.wc_locks.get(channel_id)
        if lock is None:
            lock = Marnie.wc_locks[channel_id] = asyncio.Lock()
        return lock

    @staticmethod
    async def rebuild_wc_cache(channel) -> dict:
        '''Rebuilds the cache from the latest wc window. Callers must hold the channel's wc lock.'''

        cache = Marnie.empty_wc_cache()
        recent_messages = [message async for message in channel.history(limit=Marnie.wc_message_limit)]

        # history() without `after` is newest-first; add oldest-first so the window trims correctly.
        for message in reversed(recent_messages):
            Marnie.add_wc_message(cache, message)

        Marnie.wc_cache[channel.id] = cache
        return cache

    @staticmethod
    async def refresh_wc_cache(channel) -> dict:
        '''Brings the rolling channel cache up to date, building it first if needed.'''

        async with Marnie.wc_lock(channel.id):
            cache = Marnie.wc_cache.get(channel.id)

            if cache is None or cache["newest_id"] is None:
                cache = await Marnie.rebuild_wc_cache(channel)
                if cache["newest_id"] is None:
                    return cache

            # Catches messages missed while the bot was disconnected or the rebuild was running.
            new_messages = [
                message async for message in channel.history(
                    limit=Marnie.wc_message_limit,
                    after=discord.Object(id=cache["newest_id"]),
                    oldest_first=True,
                )
            ]

            if len(new_messages) >= Marnie.wc_message_limit:
                return await Marnie.rebuild_wc_cache(channel)

            for message in new_messages:
                Marnie.add_wc_message(cache, message)

            return cache

    @staticmethod
    def update_wc_cache_with_message(message):
        '''Incrementally updates an existing channel wc cache with a new message.'''

        cache = Marnie.wc_cache.get(message.channel.id)
        if cache is None:
            return

        Marnie.add_wc_message(cache, message)

    @staticmethod
    def edit_wc_cache_message(channel_id: int, message):
        '''Replaces an edited message's words in the channel's wc cache.'''

        cache = Marnie.wc_cache.get(channel_id)
        if cache is None:
            return

        entry = cache["by_id"].get(message.id)
        if entry is None:
            return

        Marnie.apply_wc_entry(cache, entry, direction=-1)
        entry.update(Marnie.build_wc_entry(message))
        Marnie.apply_wc_entry(cache, entry, direction=1)

    @staticmethod
    def delete_wc_cache_messages(channel_id: int, message_ids):
        '''Removes deleted messages' words, keeping their slots so the window does not shift.'''

        cache = Marnie.wc_cache.get(channel_id)
        if cache is None:
            return

        for message_id in message_ids:
            entry = cache["by_id"].get(message_id)
            if entry is None:
                continue

            Marnie.apply_wc_entry(cache, entry, direction=-1)
            entry.update(chatter_id=None, author_id=None, counts=None, fallback=False)

    @staticmethod
    def schedule_wc_warmup(channel):
        '''Queues a background wc cache build the first time a server channel gets a message.'''

        guild = getattr(channel, "guild", None)
        if guild is None or guild.me is None:
            return

        channel_id = channel.id
        if channel_id in Marnie.wc_cache or channel_id in Marnie.wc_warm_pending or channel_id in Marnie.wc_warm_skipped:
            return

        if not channel.permissions_for(guild.me).read_message_history:
            return

        if Marnie.wc_warm_queue is None:
            Marnie.wc_warm_queue = asyncio.Queue()

        Marnie.wc_warm_pending.add(channel_id)
        Marnie.wc_warm_queue.put_nowait(channel)

        if Marnie.wc_warm_task is None or Marnie.wc_warm_task.done():
            Marnie.wc_warm_task = asyncio.create_task(Marnie.run_wc_warmups())

    @staticmethod
    async def run_wc_warmups():
        '''Builds queued channel caches one at a time so a restart does not flood Discord with requests.'''

        while True:
            channel = await Marnie.wc_warm_queue.get()
            try:
                if channel.id not in Marnie.wc_cache:
                    await Marnie.refresh_wc_cache(channel)
            except discord.Forbidden:
                Marnie.wc_warm_skipped.add(channel.id)
            except Exception:
                logging.getLogger(__name__).exception("wc warm-up failed for channel %s", channel.id)
            finally:
                Marnie.wc_warm_pending.discard(channel.id)


    @staticmethod
    def wc_color_func(*args, random_state=None, **kwargs) -> str:
        '''Color palette for the word cloud. Uses the seeded random_state from recolor() when given.'''

        palette = [
            "#ff76aa",
            "#ff9bc4",
            "#ffc2dd",
            "#f7f7fb",
            "#d7d9e4",
            "#c3a6ff",
        ]
        rng = random_state if isinstance(random_state, random.Random) else random
        return rng.choice(palette)

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
        '''Builds the final word cloud image. CPU-heavy, so the command runs it in a worker thread.

        Layout is computed at half size and drawn at scale=2, which is much faster than laying
        out at full size. The output is still 1800x1100; margin and min font size are halved
        because the scale multiplies them back up.'''

        cloud = WordCloud(
            width=900,
            height=550,
            scale=2,
            background_color="#1f1f28",
            collocations=False,
            max_words=180,
            margin=12,
            prefer_horizontal=0.9,
            min_font_size=7,
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

    @staticmethod
    def top_chatters_message(cache: dict, name_for) -> str:
        '''Formats the top chatters of a channel's wc window.

        name_for maps a user id to a display name, or None for people who can't be found
        (like members who left the server), who are skipped.'''

        ranked = []

        for user_id, message_count in cache["chatter_counts"].most_common():
            name = name_for(user_id)
            if name is None:
                continue

            ranked.append((name, message_count))
            if len(ranked) == Marnie.top_chatter_count:
                break

        if not ranked:
            return "nobody has chatted here yet..."

        medals = ("🥇", "🥈", "🥉")
        lines = [f"**top chatters** out of the last {Marnie.plural(len(cache['messages']), 'message')} here:"]

        for place, (name, message_count) in enumerate(ranked):
            medal = medals[place] if place < len(medals) else f"{place + 1}."
            lines.append(f"{medal} **{discord.utils.escape_markdown(name.lower())}** - {Marnie.plural(message_count, 'message')}")

        return "\n".join(lines)

    @staticmethod
    def wtp_normalize(text: str) -> str:
        '''Lowercases text and strips accents, spaces, dashes, and punctuation,
        so "Mr. Mime", "mr-mime", and "mrmime" all compare equal.'''

        decomposed = unicodedata.normalize("NFKD", text.casefold())
        return "".join(character for character in decomposed if character.isalnum())

    @staticmethod
    def wtp_species_id_map() -> dict:
        '''Maps every normalized Pokemon name, forms included, to its species (national dex) number.'''

        if Marnie.wtp_species_ids is None:
            dex = objects.pokemon.df
            Marnie.wtp_species_ids = {
                Marnie.wtp_normalize(identifier): species_id
                for identifier, species_id in zip(dex['identifier'], dex['species_id'])
            }

        return Marnie.wtp_species_ids

    @staticmethod
    def wtp_guess_matches(guess: str, wtp_round: dict) -> bool:
        '''Returns whether a chat message names the round's Pokemon. Forms never matter:
        for Landorus-Therian, "landorus", "landorus-therian", "landorustherian", and any
        other Landorus form are all correct. Small typos are forgiven, unless the guess
        is the name of a different Pokemon.'''

        guess = guess.strip()
        if not guess or len(guess) > 40:
            return False

        sanitized = Fetcher.sanitize(guess)
        candidates = (sanitized, Fetcher.mon_sanitize(sanitized), aliases.alias_map.get(sanitized))
        answers = (wtp_round["species_key"], wtp_round["identifier_key"])
        species_ids = Marnie.wtp_species_id_map()
        names_other_pokemon = False

        for candidate in candidates:
            key = Marnie.wtp_normalize(candidate) if candidate else ""
            if not key:
                continue

            if key in answers:
                return True

            species_id = species_ids.get(key)
            if species_id is not None:
                if species_id == wtp_round["species_id"]:
                    return True
                names_other_pokemon = True

        if names_other_pokemon:
            return False

        key = Marnie.wtp_normalize(guess)
        if not key:
            return False

        return any(fuzz.ratio(key, answer) >= Marnie.wtp_fuzzy_threshold for answer in answers)

    @staticmethod
    def wtp_image_url(data: dict) -> str | None:
        '''Picks the picture for a round from a PokeAPI Pokemon response: official artwork, else the sprite.'''

        sprites = data.get("sprites") or {}
        artwork = ((sprites.get("other") or {}).get("official-artwork") or {}).get("front_default")
        return artwork or sprites.get("front_default")

    @staticmethod
    def wtp_images(image_bytes: bytes) -> tuple[bytes, bytes]:
        '''Turns a transparent Pokemon picture into two PNGs: the black silhouette and the reveal.
        Raises ValueError if the picture is empty or has no transparent background to cut out.'''

        sprite = Image.open(BytesIO(image_bytes)).convert("RGBA")
        alpha = sprite.getchannel("A")
        bounds = alpha.getbbox()

        if bounds is None or alpha.getextrema()[0] == 255:
            raise ValueError("picture has no usable transparent background")

        sprite = sprite.crop(bounds)
        scale = min(Marnie.wtp_sprite_box / sprite.width, Marnie.wtp_sprite_box / sprite.height)
        size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
        # Small pixel-art sprites stay crisp with NEAREST; large artwork shrinks smoothly with LANCZOS.
        resample = Image.Resampling.NEAREST if scale >= 2 else Image.Resampling.LANCZOS
        sprite = sprite.resize(size, resample)

        left = (Marnie.wtp_canvas_size - sprite.width) // 2
        top = (Marnie.wtp_canvas_size - sprite.height) // 2
        canvas_size = (Marnie.wtp_canvas_size, Marnie.wtp_canvas_size)

        silhouette = Image.new("RGB", canvas_size, Marnie.wtp_background)
        silhouette.paste((0, 0, 0), (left, top, left + sprite.width, top + sprite.height), sprite.getchannel("A"))

        reveal = Image.new("RGB", canvas_size, Marnie.wtp_background)
        reveal.paste(sprite, (left, top), sprite)

        pngs = []
        for image in (silhouette, reveal):
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            pngs.append(buffer.getvalue())

        return pngs[0], pngs[1]

    @staticmethod
    def build_wtp_round(identifier: str, species: str, image_bytes: bytes) -> dict:
        '''Builds one round: the pictures plus everything needed to judge guesses.
        The answer is the species ("landorus"), whatever form the picture shows.'''

        silhouette, reveal = Marnie.wtp_images(image_bytes)

        return {
            "identifier": identifier,
            "name": species.title(),
            "species_id": objects.pokemon.get_species_id(identifier),
            "species_key": Marnie.wtp_normalize(species),
            "identifier_key": Marnie.wtp_normalize(identifier),
            "silhouette": silhouette,
            "reveal": reveal,
        }

    @staticmethod
    async def fetch_wtp_round() -> dict | None:
        '''Picks a random Pokemon (forms included) and builds its round.
        Some forms have no picture, so it tries a few picks. Returns None if every try fails.'''

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for _ in range(Marnie.wtp_pick_attempts):
                identifier = random.choice(objects.pokemon.list)

                try:
                    async with session.get(urls.poke_url + identifier) as response:
                        if response.status != 200:
                            continue
                        data = await response.json()

                    image_url = Marnie.wtp_image_url(data)
                    if not image_url:
                        continue

                    async with session.get(image_url) as response:
                        if response.status != 200:
                            continue
                        image_bytes = await response.read()

                    return Marnie.build_wtp_round(identifier, data["species"]["name"], image_bytes)
                except (aiohttp.ClientError, asyncio.TimeoutError, OSError, ValueError, KeyError, TypeError):
                    continue

        return None
