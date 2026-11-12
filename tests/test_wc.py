import asyncio
from collections import Counter
from types import SimpleNamespace

import pytest
from PIL import Image

from src.bot.marnie import Marnie


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


@pytest.fixture(autouse=True)
def clean_wc_state(monkeypatch):
    monkeypatch.setattr(Marnie, "wc_cache", {})
    monkeypatch.setattr(Marnie, "wc_locks", {})


@pytest.mark.parametrize('text, expected', [
    ("Pokémon are cool", ["pokémon", "are", "cool"]),
    ("I don't KNOW", ["dont", "know"]),
    ("rock- -type well-known", ["rock", "type", "well-known"]),
    ("gen9 is 2good", ["gen9", "is", "good"]),
    ("a b c", []),
])
def test_tokenize_unfiltered(text, expected):
    assert Marnie.tokenize_wc_text_unfiltered(text) == expected


def test_tokenize_filters_stopwords():
    assert Marnie.tokenize_wc_text("the snom is the best") == ["snom", "best"]


@pytest.mark.parametrize('message', [
    make_message(1, "!wc someone"),
    make_message(1, "snom snom", bot=True),
    make_message(1, ""),
    make_message(1, "https://example.com"),
])
def test_build_entry_skips_messages_without_words(message):
    entry = Marnie.build_wc_entry(message)
    assert entry["author_id"] is None
    assert entry["counts"] is None


def test_build_entry_marks_stopword_only_messages_as_fallback():
    entry = Marnie.build_wc_entry(make_message(1, "the and the"))
    assert entry["fallback"] is True
    assert entry["counts"] == Counter({"the": 2, "and": 1})


def test_window_trims_oldest_and_drops_zero_counts(monkeypatch):
    monkeypatch.setattr(Marnie, "wc_message_limit", 2)
    cache = Marnie.empty_wc_cache()

    Marnie.add_wc_message(cache, make_message(1, "snom", author_id=7))
    Marnie.add_wc_message(cache, make_message(2, "frosmoth"))
    Marnie.add_wc_message(cache, make_message(3, "frosmoth"))

    assert cache["message_counts"] == Counter({"frosmoth": 2})
    assert 7 not in cache["author_counts"]
    assert 1 not in cache["by_id"]
    assert len(cache["messages"]) == 2


def test_duplicate_messages_are_not_counted_twice():
    cache = Marnie.empty_wc_cache()
    message = make_message(1, "snom")

    assert Marnie.add_wc_message(cache, message) is True
    assert Marnie.add_wc_message(cache, message) is False
    assert cache["message_counts"] == Counter({"snom": 1})


def test_edit_replaces_words():
    cache = Marnie.empty_wc_cache()
    Marnie.wc_cache[10] = cache
    Marnie.add_wc_message(cache, make_message(1, "snom snom"))

    Marnie.edit_wc_cache_message(10, make_message(1, "frosmoth"))

    assert cache["message_counts"] == Counter({"frosmoth": 1})
    assert cache["author_counts"] == {1: Counter({"frosmoth": 1})}


def test_delete_removes_words_but_keeps_slot():
    cache = Marnie.empty_wc_cache()
    Marnie.wc_cache[10] = cache
    Marnie.add_wc_message(cache, make_message(1, "snom"))
    Marnie.add_wc_message(cache, make_message(2, "frosmoth"))

    Marnie.delete_wc_cache_messages(10, [1, 999])

    assert cache["message_counts"] == Counter({"frosmoth": 1})
    assert len(cache["messages"]) == 2


def test_refresh_builds_then_adds_new_messages_in_order(monkeypatch):
    monkeypatch.setattr(Marnie, "wc_message_limit", 3)
    channel = FakeChannel(10, [make_message(i, f"word{i}") for i in range(1, 5)])

    cache = asyncio.run(Marnie.refresh_wc_cache(channel))
    assert [entry["id"] for entry in cache["messages"]] == [2, 3, 4]

    channel.messages += [make_message(5, "word5"), make_message(6, "word6")]
    cache = asyncio.run(Marnie.refresh_wc_cache(channel))

    assert [entry["id"] for entry in cache["messages"]] == [4, 5, 6]
    assert cache["message_counts"] == Counter({"word4": 1, "word5": 1, "word6": 1})


def test_collect_word_counts_for_one_member():
    channel = FakeChannel(10, [make_message(1, "snom", author_id=1), make_message(2, "frosmoth", author_id=2)])
    member = SimpleNamespace(id=2)

    assert asyncio.run(Marnie.collect_word_counts(channel, member)) == Counter({"frosmoth": 1})


def chatty_cache() -> dict:
    '''Author 1 sends 3 messages, author 2 sends 2, authors 3 and 4 send 1 each. A bot and a command are ignored.'''

    cache = Marnie.empty_wc_cache()
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
        Marnie.add_wc_message(cache, message)

    return cache


NAMES = {1: "Snom_Fan", 2: "Bea", 3: "Cy", 4: "Dee"}


def test_top_chatters_lists_three_in_order():
    assert Marnie.top_chatters_message(chatty_cache(), NAMES.get) == (
        "**top chatters** out of the last 9 messages here:\n"
        "🥇 **snom\\_fan** - 3 messages\n"
        "🥈 **bea** - 2 messages\n"
        "🥉 **cy** - 1 message"
    )


def test_top_chatters_skips_people_who_left():
    names = {2: "Bea", 3: "Cy", 4: "Dee"}

    assert Marnie.top_chatters_message(chatty_cache(), names.get) == (
        "**top chatters** out of the last 9 messages here:\n"
        "🥇 **bea** - 2 messages\n"
        "🥈 **cy** - 1 message\n"
        "🥉 **dee** - 1 message"
    )


def test_top_chatters_follow_deletes_and_window_trimming(monkeypatch):
    cache = chatty_cache()
    Marnie.wc_cache[10] = cache

    Marnie.delete_wc_cache_messages(10, [1, 2])
    assert cache["chatter_counts"] == Counter({1: 1, 2: 2, 3: 1, 4: 1})

    monkeypatch.setattr(Marnie, "wc_message_limit", 3)
    Marnie.add_wc_message(cache, make_message(10, "hi", author_id=3))
    assert cache["chatter_counts"] == Counter({3: 1})


def test_top_chatters_with_nobody():
    assert Marnie.top_chatters_message(Marnie.empty_wc_cache(), NAMES.get) == "nobody has chatted here yet..."


def test_wordcloud_image_is_full_size():
    file = Marnie.wordcloud_image(Counter({"snom": 5, "frosmoth": 3, "marnie": 2}))
    assert Image.open(file.fp).size == (1800, 1100)
