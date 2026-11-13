from discord.ext import commands
from ..helpers import display_name, find_member
from ...utils import word_counts
from collections import Counter
import discord, asyncio, logging


class ChatStats(commands.Cog):
    '''!wc and !top. Both read one cached window of each channel's latest messages,
    which is warmed in the background on a channel's first message after startup.'''

    def __init__(self, bot: commands.Bot, message_limit: int = word_counts.MESSAGE_LIMIT):
        self.bot = bot
        self.message_limit = message_limit
        self.windows = {}
        self.locks = {}
        self.warm_queue = None
        self.warm_task = None
        self.warm_pending = set()
        self.warm_skipped = set()

    def cog_unload(self):
        if self.warm_task is not None:
            self.warm_task.cancel()

    @commands.command()
    async def wc(self, ctx, *, query: str = None):
        async with ctx.typing():
            target_member = None

            if query is not None:
                if ctx.guild is None:
                    await ctx.send("error: i can only look up a user's messages inside a server.")
                    return

                target_member = find_member(ctx.guild, query)
                if target_member is None:
                    await ctx.send(f"error: user \"{query}\" not recognized.")
                    return

            try:
                frequencies = await self.collect_word_counts(ctx.channel, target_member)
            except discord.Forbidden:
                await ctx.send(file=word_counts.blank_image())
                return

            if not frequencies:
                if target_member is not None:
                    name = target_member.display_name or target_member.global_name or target_member.name
                    await ctx.send(f"error: {name}'s messages do not exist in the last {self.message_limit} messages.")
                else:
                    await ctx.send(file=word_counts.blank_image())
                return

            await ctx.send(file=await asyncio.to_thread(word_counts.wordcloud_image, frequencies))

    @commands.command()
    async def top(self, ctx):
        async with ctx.typing():
            try:
                window = await self.refresh(ctx.channel)
            except discord.Forbidden:
                await ctx.send("error: i can't read this channel's message history.")
                return

            def name_for(user_id: int) -> str | None:
                user = ctx.guild.get_member(user_id) if ctx.guild is not None else self.bot.get_user(user_id)
                return display_name(user) if user is not None else None

            await ctx.send(
                word_counts.top_chatters_message(window, name_for),
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        window = self.windows.get(message.channel.id)
        if window is not None:
            word_counts.add_message(window, message, self.message_limit)

        self.schedule_warmup(message.channel)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        window = self.windows.get(payload.channel_id)
        if window is not None:
            word_counts.edit_message(window, payload.message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        self.delete_messages(payload.channel_id, [payload.message_id])

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        self.delete_messages(payload.channel_id, payload.message_ids)

    def delete_messages(self, channel_id: int, message_ids):
        window = self.windows.get(channel_id)
        if window is not None:
            word_counts.delete_messages(window, message_ids)

    async def collect_word_counts(self, channel, target_member: discord.Member | None) -> Counter:
        '''Brings the channel's window up to date and returns word frequencies.'''

        window = await self.refresh(channel)
        return word_counts.word_counts(window, target_member.id if target_member is not None else None)

    def lock(self, channel_id: int) -> asyncio.Lock:
        '''Returns the lock that keeps one channel's window from being fetched twice at once.'''

        if channel_id not in self.locks:
            self.locks[channel_id] = asyncio.Lock()
        return self.locks[channel_id]

    async def rebuild(self, channel) -> dict:
        '''Rebuilds a channel's window from its history. Callers must hold the channel's lock.'''

        window = word_counts.empty_window()
        recent_messages = [message async for message in channel.history(limit=self.message_limit)]

        # history() without `after` is newest-first; add oldest-first so the window trims correctly.
        for message in reversed(recent_messages):
            word_counts.add_message(window, message, self.message_limit)

        self.windows[channel.id] = window
        return window

    async def refresh(self, channel) -> dict:
        '''Brings a channel's window up to date, building it first if needed.'''

        async with self.lock(channel.id):
            window = self.windows.get(channel.id)

            if window is None or window["newest_id"] is None:
                window = await self.rebuild(channel)
                if window["newest_id"] is None:
                    return window

            # Catches messages missed while the bot was disconnected or the rebuild was running.
            new_messages = [
                message async for message in channel.history(
                    limit=self.message_limit,
                    after=discord.Object(id=window["newest_id"]),
                    oldest_first=True,
                )
            ]

            if len(new_messages) >= self.message_limit:
                return await self.rebuild(channel)

            for message in new_messages:
                word_counts.add_message(window, message, self.message_limit)

            return window

    def schedule_warmup(self, channel):
        '''Queues a background window build the first time a server channel gets a message.'''

        guild = getattr(channel, "guild", None)
        if guild is None or guild.me is None:
            return

        channel_id = channel.id
        if channel_id in self.windows or channel_id in self.warm_pending or channel_id in self.warm_skipped:
            return

        if not channel.permissions_for(guild.me).read_message_history:
            return

        if self.warm_queue is None:
            self.warm_queue = asyncio.Queue()

        self.warm_pending.add(channel_id)
        self.warm_queue.put_nowait(channel)

        if self.warm_task is None or self.warm_task.done():
            self.warm_task = asyncio.create_task(self.run_warmups())

    async def run_warmups(self):
        '''Builds queued windows one at a time so a restart does not flood Discord with requests.'''

        while True:
            channel = await self.warm_queue.get()
            try:
                if channel.id not in self.windows:
                    await self.refresh(channel)
            except discord.Forbidden:
                self.warm_skipped.add(channel.id)
            except Exception:
                logging.getLogger(__name__).exception("wc warm-up failed for channel %s", channel.id)
            finally:
                self.warm_pending.discard(channel.id)
