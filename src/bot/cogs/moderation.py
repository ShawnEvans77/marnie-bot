from discord.ext import commands
from ..helpers import display_name
from ...utils.text import plural
import discord, asyncio, datetime


def is_timed_out(member: discord.Member) -> bool:
    '''Returns whether a member is currently timed out.'''

    return member.timed_out_until is not None and member.timed_out_until > datetime.datetime.now(datetime.UTC)


def mute_duration(timed_out_until: datetime.datetime) -> str:
    '''Formats how long is left on a timeout, like "1 hour and 5 minutes".'''

    total = max(0, int((timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds()))
    days, rem_hours = total // 86400, total % 86400
    hours, rem_min = rem_hours // 3600, rem_hours % 3600
    minutes, rem_sec = rem_min // 60, rem_min % 60
    duration_parts = []

    if days > 0:
        duration_parts.append(plural(days, 'day'))
    if hours > 0:
        duration_parts.append(plural(hours, 'hour'))
    if minutes > 0:
        duration_parts.append(plural(minutes, 'minute'))
    if rem_sec > 0 or not duration_parts:
        duration_parts.append(plural(rem_sec, 'second'))

    if len(duration_parts) == 1:
        return duration_parts[0]

    if len(duration_parts) == 2:
        return " and ".join(duration_parts)

    return f"{', '.join(duration_parts[:-1])}, and {duration_parts[-1]}"


def can_send(channel, guild: discord.Guild) -> bool:
    '''Returns whether Marnie can send messages in a channel.'''

    if channel is None or guild.me is None:
        return False

    permissions = channel.permissions_for(guild.me)
    return permissions.view_channel and (permissions.send_messages or getattr(permissions, "send_messages_in_threads", False))


async def fetch_fresh_member(guild: discord.Guild, member_id: int) -> discord.Member | None:
    '''Fetches a fresh member object when possible.'''

    try:
        return await guild.fetch_member(member_id)
    except discord.NotFound:
        return None
    except (discord.Forbidden, discord.HTTPException):
        return guild.get_member(member_id)


class Moderation(commands.Cog):
    '''!muted, plus announcing when members are muted and unmuted.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_spoken_channels = {}
        self.mute_cease_tasks = {}

    def cog_unload(self):
        for task in self.mute_cease_tasks.values():
            task.cancel()
        self.mute_cease_tasks.clear()

    @commands.command()
    async def muted(self, ctx):
        if ctx.guild is None:
            await ctx.send("i can only check who's muted inside a server, silly!")
            return

        answer = ""

        for member in ctx.guild.members:
            if member.is_timed_out():
                present_member = await fetch_fresh_member(ctx.guild, member.id)
                if present_member is None or not is_timed_out(present_member):
                    continue

                answer += f"**{display_name(present_member).lower()}** is muted for"
                answer += f" {mute_duration(present_member.timed_out_until)}\n"

        await ctx.send(answer if len(answer) != 0 else "nobody is muted right now")

    @commands.Cog.listener()
    async def on_ready(self):
        self.schedule_existing_mute_ceases()

    @commands.Cog.listener()
    async def on_message(self, message):
        self.remember_last_spoken_channel(message)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        was_timed_out = is_timed_out(before)
        now_timed_out = is_timed_out(after)

        if was_timed_out and not now_timed_out:
            self.cancel_mute_cease(after)
            await self.announce_mute_cease(after)
            return

        if was_timed_out and now_timed_out:
            if before.timed_out_until != after.timed_out_until:
                self.schedule_mute_cease(after)
            return

        if not now_timed_out:
            return

        await self.announce_mute_start(after)
        self.schedule_mute_cease(after)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.cancel_mute_cease(member)
        self.last_spoken_channels.pop((member.guild.id, member.id), None)

    def remember_last_spoken_channel(self, message):
        '''Stores the last server channel a member spoke in.'''

        if message.guild is None or message.author.bot:
            return

        self.last_spoken_channels[(message.guild.id, message.author.id)] = message.channel.id

    def mute_announcement_channel(self, guild: discord.Guild, member: discord.Member):
        '''Finds the best channel for announcing a member timeout: where they last spoke, else #general.'''

        channel_id = self.last_spoken_channels.get((guild.id, member.id))
        get_channel_or_thread = getattr(guild, "get_channel_or_thread", None)
        channel = get_channel_or_thread(channel_id) if get_channel_or_thread and channel_id else guild.get_channel(channel_id)

        if can_send(channel, guild):
            return channel

        general = discord.utils.get(guild.text_channels, name="general")
        return general if can_send(general, guild) else None

    @staticmethod
    def mute_task_key(member: discord.Member) -> tuple[int, int]:
        return (member.guild.id, member.id)

    def cancel_mute_cease(self, member: discord.Member):
        '''Cancels a scheduled mute cease announcement for a member.'''

        task = self.mute_cease_tasks.pop(self.mute_task_key(member), None)
        if task is not None:
            task.cancel()

    def schedule_mute_cease(self, member: discord.Member):
        '''Schedules a mute cease announcement for when the current timeout expires.'''

        if member.timed_out_until is None:
            return

        self.cancel_mute_cease(member)
        task = asyncio.create_task(self.announce_mute_cease_after_timeout(member.guild, member.id, member.timed_out_until))
        self.mute_cease_tasks[self.mute_task_key(member)] = task

    def schedule_existing_mute_ceases(self):
        '''Schedules mute cease announcements for timed-out members already in cache.'''

        for guild in self.bot.guilds:
            for member in guild.members:
                if is_timed_out(member):
                    self.schedule_mute_cease(member)

    async def announce_mute_cease_after_timeout(self, guild: discord.Guild, member_id: int, timed_out_until: datetime.datetime):
        '''Sleeps until a timeout expires, then announces if the member is no longer muted.'''

        delay = max(0, (timed_out_until - datetime.datetime.now(datetime.UTC)).total_seconds())

        try:
            await asyncio.sleep(delay)
            member = await fetch_fresh_member(guild, member_id)
            if member is not None and not is_timed_out(member):
                await self.announce_mute_cease(member)
        except asyncio.CancelledError:
            return
        finally:
            key = (guild.id, member_id)
            if self.mute_cease_tasks.get(key) is asyncio.current_task():
                self.mute_cease_tasks.pop(key, None)

    async def announce_mute_start(self, member: discord.Member):
        '''Announces that a member was timed out.'''

        channel = self.mute_announcement_channel(member.guild, member)
        if channel is None:
            return

        await channel.send(
            f"**{display_name(member).lower()}** was muted for {mute_duration(member.timed_out_until)}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def announce_mute_cease(self, member: discord.Member):
        '''Announces that a member is no longer timed out.'''

        channel = self.mute_announcement_channel(member.guild, member)
        if channel is None:
            return

        await channel.send(
            f"**{display_name(member).lower()}** is no longer muted",
            allowed_mentions=discord.AllowedMentions.none(),
        )
