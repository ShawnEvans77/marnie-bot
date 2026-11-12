import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
import requests
from discord.ext import commands

import src.constants.getters.get_objs as get_objs
from src.bot.marnie import Marnie
from src.constants.api import urls
from src.utils.fetcher import Fetcher

f = get_objs.fetcher


class FakeCtx:
    def __init__(self):
        self.command = "dt"
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append(content)


@pytest.fixture
def marnie(monkeypatch):
    '''A Marnie that does not open (and wipe) the real discord.log.'''

    monkeypatch.setattr(logging, "FileHandler", lambda **kwargs: logging.NullHandler())
    return Marnie()


def http_error(status_code: int) -> requests.HTTPError:
    return requests.HTTPError(response=SimpleNamespace(status_code=status_code))


def test_every_request_uses_the_shared_session_with_a_timeout(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            calls.append("checked")

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse()

    monkeypatch.setattr(Fetcher.session, "get", fake_get)

    assert isinstance(Fetcher.get("https://example.com/x"), FakeResponse)
    assert calls == [("https://example.com/x", {"timeout": Fetcher.timeout}), "checked"]
    assert Fetcher.timeout == 10


def test_session_retries_once():
    for prefix in ("https://", "http://"):
        retries = Fetcher.session.get_adapter(prefix + "pokeapi.co").max_retries
        assert retries.total == 1
        assert set(retries.status_forcelist) == {502, 503, 504}


def test_get_returns_fresh_data_each_time():
    first = Fetcher.get(urls.poke_url + "snom")
    second = Fetcher.get(urls.poke_url + "snom")

    assert first is not second
    assert first.json()["name"] == second.json()["name"] == "snom"


def test_get_raises_when_pokeapi_has_no_such_page():
    with pytest.raises(requests.HTTPError) as error:
        Fetcher.get(urls.poke_url + "definitely-not-a-pokemon")

    assert error.value.response.status_code == 404
    assert Marnie.pokeapi_error_message(error.value) == "sorry, pokeapi doesn't have any data on that one..."


def test_lookups_from_several_threads_at_once_all_succeed():
    queries = ["snom", "frosmoth", "morpeko", "garchomp", "mega alakazam", "swords dance", "blaze", "445"] * 2

    with ThreadPoolExecutor(max_workers=8) as pool:
        answers = list(pool.map(f.dt, queries))

    for query, answer in zip(queries, answers):
        assert answer == f.dt(query)
        assert "i don't know" not in answer


@pytest.mark.parametrize('error, expected', [
    (requests.ReadTimeout(), "sorry, pokeapi is taking too long to answer right now... try again in a bit?"),
    (requests.ConnectTimeout(), "sorry, pokeapi is taking too long to answer right now... try again in a bit?"),
    (requests.ConnectionError(), "sorry, i couldn't reach pokeapi right now... try again in a bit?"),
    (http_error(500), "sorry, i couldn't reach pokeapi right now... try again in a bit?"),
    (http_error(404), "sorry, pokeapi doesn't have any data on that one..."),
])
def test_error_messages(error, expected):
    assert Marnie.pokeapi_error_message(error) == expected


def test_failed_lookup_tells_the_user(marnie):
    async def scenario():
        ctx = FakeCtx()
        await marnie.bot.on_command_error(ctx, commands.CommandInvokeError(requests.ConnectionError()))
        return ctx.sent

    assert asyncio.run(scenario()) == ["sorry, i couldn't reach pokeapi right now... try again in a bit?"]


def test_other_errors_are_logged_and_not_sent(marnie, caplog):
    async def scenario():
        ctx = FakeCtx()
        await marnie.bot.on_command_error(ctx, commands.CommandNotFound('Command "lol" is not found'))
        return ctx.sent

    with caplog.at_level(logging.ERROR, logger="discord.ext.commands.bot"):
        assert asyncio.run(scenario()) == []

    assert "Ignoring exception in command" in caplog.text


def test_dt_command_fails_with_a_message_when_pokeapi_is_down(marnie, monkeypatch):
    '''Runs the real command through discord.py's own invoke path, which is what calls the error handler.'''

    def broken_get(url, **kwargs):
        raise requests.ConnectionError("pokeapi is down")

    monkeypatch.setattr(Fetcher.session, "get", broken_get)

    async def scenario():
        ctx = FakeCtx()
        command = marnie.bot.get_command("dt")
        ctx.command = command

        try:
            await command.callback(ctx, query="snom")
        except requests.RequestException as error:
            await marnie.bot.on_command_error(ctx, commands.CommandInvokeError(error))

        return ctx.sent

    assert asyncio.run(scenario()) == ["sorry, i couldn't reach pokeapi right now... try again in a bit?"]


def test_bot_keeps_running_while_a_lookup_waits(marnie, monkeypatch):
    '''A slow PokeAPI answer must not freeze the event loop.'''

    def slow_dt(query):
        time.sleep(0.5)
        return f"info on {query}"

    monkeypatch.setattr(get_objs.fetcher, "dt", slow_dt)

    async def scenario():
        ctx = FakeCtx()
        ticks = 0

        async def ticker():
            nonlocal ticks
            while True:
                await asyncio.sleep(0.02)
                ticks += 1

        ticking = asyncio.create_task(ticker())
        await marnie.bot.get_command("dt").callback(ctx, query="snom")
        ticking.cancel()

        return ctx.sent, ticks

    sent, ticks = asyncio.run(scenario())

    assert sent == ["info on snom"]
    assert ticks >= 10
