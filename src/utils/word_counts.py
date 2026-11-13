'''The rolling message window behind !wc and !top, and the word cloud picture.

A window is a plain dict (see empty_window) holding the last `limit` messages of one
channel, plus running totals so neither command has to recount everything.'''

from ..constants.output import wordcloud as wc, command
from .text import plural
from collections import Counter, deque
from io import BytesIO
from PIL import Image
from wordcloud import WordCloud
import discord, random, re

MESSAGE_LIMIT = 10000
TOP_CHATTER_COUNT = 3
STOPWORDS = wc.stopwords
TOKEN_PATTERN = re.compile(r"[^\W\d_][^\W_]*(?:['\-][^\W_]+)*")
BACKGROUND = "#1f1f28"
PALETTE = ("#ff76aa", "#ff9bc4", "#ffc2dd", "#f7f7fb", "#d7d9e4", "#c3a6ff")


def sanitize_text(text: str) -> str:
    '''Drops URLs and normalizes message text before tokenization.'''

    without_urls = re.sub(r"https?://\S+|www\.\S+", " ", text)
    return without_urls.replace("\n", " ").strip()


def tokenize_unfiltered(text: str) -> list[str]:
    '''Returns lowercase word tokens without stopword filtering for fallback clouds.

    Words may contain any letters (so "Pokémon" stays whole) and digits after the
    first letter. Inner apostrophes and hyphens are kept; stray ones at the edges are not.'''

    normalized_text = text.lower().replace("’", "'")
    normalized_tokens = [token.replace("'", "") for token in TOKEN_PATTERN.findall(normalized_text)]
    return [token for token in normalized_tokens if len(token) > 1]


def filter_stopwords(tokens: list[str]) -> list[str]:
    '''Drops stopwords from an already-tokenized message.'''

    return [token for token in tokens if token not in STOPWORDS]


def tokenize(text: str) -> list[str]:
    '''Returns lowercase word tokens for the word cloud, without stopwords.'''

    return filter_stopwords(tokenize_unfiltered(text))


def empty_window() -> dict:
    '''Creates an empty rolling window.'''

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


def build_entry(message) -> dict:
    '''Builds the window's record of one message.

    Bot messages, empty messages, and commands count toward the window but add no words.
    A message made only of stopwords is stored as a fallback entry.
    chatter_id is who gets credit for the message in !top: any non-bot message that is
    not a command, even one with no words (like an image).'''

    chatter_id = None
    author_id = None
    counts = None
    fallback = False
    content = message.content or ""

    if not message.author.bot and not content.startswith(command.prefix):
        chatter_id = message.author.id
        all_tokens = tokenize_unfiltered(sanitize_text(content))

        if all_tokens:
            author_id = message.author.id
            tokens = filter_stopwords(all_tokens)
            fallback = not tokens
            counts = Counter(tokens or all_tokens)

    return {
        "id": message.id,
        "chatter_id": chatter_id,
        "author_id": author_id,
        "counts": counts,
        "fallback": fallback,
    }


def adjust_counter(counter: Counter, counts, direction: int):
    '''Adds (direction=1) or removes (direction=-1) counts, dropping keys that reach zero.'''

    for key, amount in counts.items():
        new_amount = counter.get(key, 0) + amount * direction
        if new_amount > 0:
            counter[key] = new_amount
        else:
            counter.pop(key, None)


def apply_entry(window: dict, entry: dict, direction: int):
    '''Adds or removes one message entry from the window's running totals.'''

    if entry["chatter_id"] is not None:
        adjust_counter(window["chatter_counts"], {entry["chatter_id"]: 1}, direction)

    if entry["author_id"] is None:
        return

    if entry["fallback"]:
        total_counts, author_counters = window["fallback_message_counts"], window["fallback_author_counts"]
    else:
        total_counts, author_counters = window["message_counts"], window["author_counts"]

    adjust_counter(total_counts, entry["counts"], direction)

    author_counter = author_counters.setdefault(entry["author_id"], Counter())
    adjust_counter(author_counter, entry["counts"], direction)
    if not author_counter:
        del author_counters[entry["author_id"]]


def add_message(window: dict, message, limit: int = MESSAGE_LIMIT) -> bool:
    '''Adds one message to the window, unless it is already there, then trims the window back to the limit.'''

    if message.id in window["by_id"]:
        return False

    entry = build_entry(message)
    window["messages"].append(entry)
    window["by_id"][entry["id"]] = entry
    if window["newest_id"] is None or entry["id"] > window["newest_id"]:
        window["newest_id"] = entry["id"]
    apply_entry(window, entry, direction=1)

    while len(window["messages"]) > limit:
        removed_entry = window["messages"].popleft()
        window["by_id"].pop(removed_entry["id"], None)
        apply_entry(window, removed_entry, direction=-1)

    return True


def edit_message(window: dict, message):
    '''Replaces an edited message's words.'''

    entry = window["by_id"].get(message.id)
    if entry is None:
        return

    apply_entry(window, entry, direction=-1)
    entry.update(build_entry(message))
    apply_entry(window, entry, direction=1)


def delete_messages(window: dict, message_ids):
    '''Removes deleted messages' words, keeping their slots so the window does not shift.'''

    for message_id in message_ids:
        entry = window["by_id"].get(message_id)
        if entry is None:
            continue

        apply_entry(window, entry, direction=-1)
        entry.update(chatter_id=None, author_id=None, counts=None, fallback=False)


def word_counts(window: dict, member_id: int | None = None) -> Counter:
    '''The words to draw: the whole channel's, or one member's. Falls back to stopwords
    when there is nothing else.'''

    if member_id is None:
        return (window["message_counts"] or window["fallback_message_counts"]).copy()

    author_counts = window["author_counts"].get(member_id)
    if author_counts:
        return author_counts.copy()

    return window["fallback_author_counts"].get(member_id, Counter()).copy()


def top_chatters_message(window: dict, name_for) -> str:
    '''Formats the top chatters of a window.

    name_for maps a user id to a display name, or None for people who can't be found
    (like members who left the server), who are skipped.'''

    ranked = []

    for user_id, message_count in window["chatter_counts"].most_common():
        name = name_for(user_id)
        if name is None:
            continue

        ranked.append((name, message_count))
        if len(ranked) == TOP_CHATTER_COUNT:
            break

    if not ranked:
        return "nobody has chatted here yet..."

    medals = ("🥇", "🥈", "🥉")
    lines = [f"**top chatters** out of the last {plural(len(window['messages']), 'message')} here:"]

    for place, (name, message_count) in enumerate(ranked):
        medal = medals[place] if place < len(medals) else f"{place + 1}."
        lines.append(f"{medal} **{discord.utils.escape_markdown(name.lower())}** - {plural(message_count, 'message')}")

    return "\n".join(lines)


def color_func(*args, random_state=None, **kwargs) -> str:
    '''Color palette for the word cloud. Uses the seeded random_state from recolor() when given.'''

    rng = random_state if isinstance(random_state, random.Random) else random
    return rng.choice(PALETTE)


def png_file(image: Image.Image) -> discord.File:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="wc.png")


def blank_image() -> discord.File:
    '''A blank picture for when there is nothing to draw.'''

    return png_file(Image.new("RGB", (1200, 700), BACKGROUND))


def wordcloud_image(frequencies: Counter) -> discord.File:
    '''Builds the word cloud picture. CPU-heavy, so callers should run it in a worker thread.

    Layout is computed at half size and drawn at scale=2, which is much faster than laying
    out at full size. The output is still 1800x1100; margin and min font size are halved
    because the scale multiplies them back up.'''

    cloud = WordCloud(
        width=900,
        height=550,
        scale=2,
        background_color=BACKGROUND,
        collocations=False,
        max_words=180,
        margin=12,
        prefer_horizontal=0.9,
        min_font_size=7,
    ).generate_from_frequencies(frequencies)

    cloud = cloud.recolor(color_func=color_func, random_state=17)
    return png_file(cloud.to_image().convert("RGB"))
