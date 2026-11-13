import asyncio
from collections import Counter
from types import SimpleNamespace

import pytest
from PIL import Image

from src.bot.cogs.chat_stats import ChatStats
from src.utils import word_counts as wcount


def make_message(message_id: int, content: str, author_id: int = 1, bot: bool = False):
    return SimpleNamespace(id=message_id, content=content, author=SimpleNamespace(id=author_id, bot=bot))


class FakeChannel:
    '''Mimics discord.py history(): newest-first by default, oldest-first when `after` is given.'''

    def __init__(self, channel_id: int, messages):
        self.id = channel_id
        self.messages = sorted(messages, key=lambda message: message.id)

    async def history(self, limit=None, after=None, oldest_first=None):
        if oldest_first is None:
            oldest_first = after is not None

        selected = [message for message in self.messages if after is None or message.id > after.id]
        selected = selected[:limit] if oldest_first else list(reversed(selected))[:limit]

        for message in selected:
            yield message


@pytest.fixture
def stats():
    return ChatStats(bot=None)


@pytest.mark.parametrize('text, expected', [
    ("Pokémon are cool", ["pokémon", "are", "cool"]),
    ("I don't KNOW", ["dont", "know"]),
    ("rock- -type well-known", ["rock", "type", "well-known"]),
    ("gen9 is 2good", ["gen9", "is", "good"]),
    ("a b c", []),
])
def test_tokenize_unfiltered(text, expected):
    assert wcount.tokenize_unfiltered(text) == expected


def test_tokenize_filters_stopwords():
    assert wcount.tokenize("the snom is the best") == ["snom", "best"]


@pytest.mark.parametrize('message', [
    make_message(1, "!wc someone"),
    make_message(1, "snom snom", bot=True),
    make_message(1, ""),
    make_message(1, "https://example.com"),
])
def test_build_entry_skips_messages_without_words(message):
    entry = wcount.build_entry(message)
    assert entry["author_id"] is None
    assert entry["counts"] is None


def test_build_entry_marks_stopword_only_messages_as_fallback():
    entry = wcount.build_entry(make_message(1, "the and the"))
    assert entry["fallback"] is True
    assert entry["counts"] == Counter({"the": 2, "and": 1})


def test_window_trims_oldest_and_drops_zero_counts():
    cache = wcount.empty_window()

    wcount.add_message(cache, make_message(1, "snom", author_id=7), limit=2)
    wcount.add_message(cache, make_message(2, "frosmoth"), limit=2)
    wcount.add_message(cache, make_message(3, "frosmoth"), limit=2)

    assert cache["message_counts"] == Counter({"frosmoth": 2})
    assert 7 not in cache["author_counts"]
    assert 1 not in cache["by_id"]
    assert len(cache["messages"]) == 2


def test_duplicate_messages_are_not_counted_twice():
    cache = wcount.empty_window()
    message = make_message(1, "snom")

    assert wcount.add_message(cache, message) is True
    assert wcount.add_message(cache, message) is False
    assert cache["message_counts"] == Counter({"snom": 1})


def test_edit_replaces_words(stats):
    cache = wcount.empty_window()
    stats.windows[10] = cache
    wcount.add_message(cache, make_message(1, "snom snom"))

    asyncio.run(stats.on_raw_message_edit(SimpleNamespace(channel_id=10, message=make_message(1, "frosmoth"))))

    assert cache["message_counts"] == Counter({"frosmoth": 1})
    assert cache["author_counts"] == {1: Counter({"frosmoth": 1})}


def test_delete_removes_words_but_keeps_slot(stats):
    cache = wcount.empty_window()
    stats.windows[10] = cache
    wcount.add_message(cache, make_message(1, "snom"))
    wcount.add_message(cache, make_message(2, "frosmoth"))

    stats.delete_messages(10, [1, 999])

    assert cache["message_counts"] == Counter({"frosmoth": 1})
    assert len(cache["messages"]) == 2


def test_refresh_builds_then_adds_new_messages_in_order():
    stats = ChatStats(bot=None, message_limit=3)
    channel = FakeChannel(10, [make_message(i, f"word{i}") for i in range(1, 5)])

    cache = asyncio.run(stats.refresh(channel))
    assert [entry["id"] for entry in cache["messages"]] == [2, 3, 4]

    channel.messages += [make_message(5, "word5"), make_message(6, "word6")]
    cache = asyncio.run(stats.refresh(channel))

    assert [entry["id"] for entry in cache["messages"]] == [4, 5, 6]
    assert cache["message_counts"] == Counter({"word4": 1, "word5": 1, "word6": 1})


def test_collect_word_counts_for_one_member(stats):
    channel = FakeChannel(10, [make_message(1, "snom", author_id=1), make_message(2, "frosmoth", author_id=2)])
    member = SimpleNamespace(id=2)

    assert asyncio.run(stats.collect_word_counts(channel, member)) == Counter({"frosmoth": 1})


def chatty_cache() -> dict:
    '''Author 1 sends 3 messages, author 2 sends 2, authors 3 and 4 send 1 each. A bot and a command are ignored.'''

    cache = wcount.empty_window()
    messages = [
        make_message(1, "snom", author_id=1),
        make_message(2, "", author_id=1),
        make_message(3, "the", author_id=1),
        make_message(4, "frosmoth", author_id=2),
        make_message(5, "frosmoth", author_id=2),
        make_message(6, "hello", author_id=3),
        make_message(7, "hello", author_id=4),
        make_message(8, "beep", author_id=9, bot=True),
        make_message(9, "!top", author_id=4),
    ]

    for message in messages:
        wcount.add_message(cache, message)

    return cache


NAMES = {1: "Snom_Fan", 2: "Bea", 3: "Cy", 4: "Dee"}


def test_top_chatters_lists_three_in_order():
    assert wcount.top_chatters_message(chatty_cache(), NAMES.get) == (
        "**top chatters** out of the last 9 messages here:\n"
        "🥇 **snom\\_fan** - 3 messages\n"
        "🥈 **bea** - 2 messages\n"
        "🥉 **cy** - 1 message"
    )


def test_top_chatters_skips_people_who_left():
    names = {2: "Bea", 3: "Cy", 4: "Dee"}

    assert wcount.top_chatters_message(chatty_cache(), names.get) == (
        "**top chatters** out of the last 9 messages here:\n"
        "🥇 **bea** - 2 messages\n"
        "🥈 **cy** - 1 message\n"
        "🥉 **dee** - 1 message"
    )


def test_top_chatters_follow_deletes_and_window_trimming():
    cache = chatty_cache()

    wcount.delete_messages(cache, [1, 2])
    assert cache["chatter_counts"] == Counter({1: 1, 2: 2, 3: 1, 4: 1})

    wcount.add_message(cache, make_message(10, "hi", author_id=3), limit=3)
    assert cache["chatter_counts"] == Counter({3: 1})


def test_top_chatters_with_nobody():
    assert wcount.top_chatters_message(wcount.empty_window(), NAMES.get) == "nobody has chatted here yet..."


def test_wordcloud_image_is_full_size():
    file = wcount.wordcloud_image(Counter({"snom": 5, "frosmoth": 3, "marnie": 2}))
    assert Image.open(file.fp).size == (1800, 1100)


def test_new_messages_update_a_warm_window(stats):
    cache = wcount.empty_window()
    stats.windows[10] = cache
    message = make_message(1, "snom")
    message.channel = SimpleNamespace(id=10, guild=None)

    asyncio.run(stats.on_message(message))

    assert cache["message_counts"] == Counter({"snom": 1})
