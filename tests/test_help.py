import asyncio
import logging
from types import SimpleNamespace

import discord
import pytest

from src.bot import help_menu
from src.bot.marnie import Marnie
from src.constants.output import help as h


class FakeResponse:
    def __init__(self):
        self.edits = []

    async def edit_message(self, **kwargs):
        self.edits.append(kwargs)


class FakeMessage:
    def __init__(self):
        self.edits = []

    async def edit(self, **kwargs):
        self.edits.append(kwargs)


class FakeCtx:
    def __init__(self, embed_links: bool):
        self.me = SimpleNamespace()
        self.channel = SimpleNamespace(permissions_for=lambda member: SimpleNamespace(embed_links=embed_links))
        self.sent = []

    async def send(self, content=None, **kwargs):
        self.sent.append((content, kwargs))
        return FakeMessage()


@pytest.fixture
def marnie(monkeypatch):
    '''A Marnie that does not open (and wipe) the real discord.log.'''

    monkeypatch.setattr(logging, "FileHandler", lambda **kwargs: logging.NullHandler())
    return Marnie()


def documented_commands() -> list[str]:
    return [usage.split(" ")[0] for page in h.pages for _, usage, _ in page["commands"]]


def test_every_command_is_documented_exactly_once(marnie):
    real_commands = sorted(command.name for command in marnie.bot.commands if command.name != "help")

    assert sorted(documented_commands()) == real_commands


def test_embeds_fit_discord_limits():
    embeds = help_menu.build_embeds("!", "https://example.com/avatar.png")

    assert len(embeds) == len(h.pages) == 2

    for number, embed in enumerate(embeds, start=1):
        assert len(embed.title) <= 256
        assert len(embed.description) <= 4096
        assert 1 <= len(embed.fields) <= 25
        assert all(len(field.name) <= 256 and 1 <= len(field.value) <= 1024 for field in embed.fields)
        assert len(embed) <= 6000
        assert embed.footer.text.startswith(f"page {number}/2")
        assert embed.color.value == 0xff76aa
        assert embed.thumbnail.url == "https://example.com/avatar.png"


def test_embed_fields_show_the_prefix_and_usage():
    first_page = help_menu.build_embeds("!")[0]

    assert first_page.fields[0].name == "📖 !dt {query}"
    assert first_page.thumbnail.url is None


def test_text_pages_fit_in_discord_messages():
    texts = help_menu.build_text_pages("!")

    assert len(texts) == 2
    assert all(len(text) <= 2000 for text in texts)
    assert "* !**dt** {query} - " in texts[0]
    assert "* !**wtp** - " in texts[1]


def test_buttons_flip_pages_and_switch_off_at_the_ends():
    async def scenario():
        menu = help_menu.HelpMenu(help_menu.build_embeds("!"))
        assert (menu.previous_page.disabled, menu.next_page.disabled, menu.page_number.label) == (True, False, "page 1/2")
        assert menu.page_number.disabled is True

        forward = SimpleNamespace(response=FakeResponse())
        await menu.next_page.callback(forward)
        assert forward.response.edits == [{"embed": menu.embeds[1], "view": menu}]
        assert (menu.previous_page.disabled, menu.next_page.disabled, menu.page_number.label) == (False, True, "page 2/2")

        back = SimpleNamespace(response=FakeResponse())
        await menu.previous_page.callback(back)
        assert back.response.edits == [{"embed": menu.embeds[0], "view": menu}]
        assert (menu.previous_page.disabled, menu.next_page.disabled, menu.page_number.label) == (True, False, "page 1/2")

        # A stray press past either end stays on a real page.
        await menu.show_page(SimpleNamespace(response=FakeResponse()), 99)
        assert menu.page == 1
        await menu.show_page(SimpleNamespace(response=FakeResponse()), -5)
        assert menu.page == 0

        menu.stop()

    asyncio.run(scenario())


def test_buttons_grey_out_on_timeout():
    async def scenario():
        menu = help_menu.HelpMenu(help_menu.build_embeds("!"))
        menu.message = FakeMessage()

        await menu.on_timeout()

        assert all(button.disabled for button in menu.children)
        assert menu.message.edits == [{"view": menu}]
        menu.stop()

    asyncio.run(scenario())


def test_help_command_sends_the_menu(marnie):
    async def scenario():
        ctx = FakeCtx(embed_links=True)
        await marnie.bot.get_command("help").callback(ctx)

        assert len(ctx.sent) == 1
        content, kwargs = ctx.sent[0]
        menu = kwargs["view"]
        assert content is None
        assert isinstance(menu, help_menu.HelpMenu)
        assert kwargs["embed"] is menu.embeds[0]
        assert isinstance(menu.message, FakeMessage)
        assert isinstance(kwargs["embed"], discord.Embed)
        menu.stop()

    asyncio.run(scenario())


def test_help_command_falls_back_to_text_without_embed_permission(marnie):
    async def scenario():
        ctx = FakeCtx(embed_links=False)
        await marnie.bot.get_command("help").callback(ctx)

        assert [content for content, _ in ctx.sent] == help_menu.build_text_pages("!")
        assert all(kwargs == {} for _, kwargs in ctx.sent)

    asyncio.run(scenario())
