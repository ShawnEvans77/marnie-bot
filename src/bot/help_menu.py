'''Marnie's help menu: one embed per page, with buttons to flip between pages.'''

from ..constants.output import help as h
import discord

color = 0xff76aa
timeout_seconds = 120


def build_embeds(prefix: str, avatar_url: str | None = None) -> list[discord.Embed]:
    '''Builds one embed for each help page.'''

    embeds = []

    for number, page in enumerate(h.pages, start=1):
        embed = discord.Embed(
            title=f"{page['emoji']} {page['title']}",
            description=f"{page['blurb']}\n{h.intro}",
            color=color,
        )

        for emoji, usage, description in page["commands"]:
            embed.add_field(name=f"{emoji} {prefix}{usage}", value=description, inline=False)

        embed.set_footer(text=f"page {number}/{len(h.pages)} • marnie's help menu")
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        embeds.append(embed)

    return embeds


def build_text_pages(prefix: str) -> list[str]:
    '''Builds the same pages as plain messages, for channels where Marnie can't send embeds.'''

    texts = []

    for page in h.pages:
        lines = [f"**{page['emoji']} {page['title']}**"]

        for emoji, usage, description in page["commands"]:
            name, _, arguments = usage.partition(" ")
            lines.append(f"* {prefix}**{name}**{' ' + arguments if arguments else ''} - {description}")

        texts.append("\n".join(lines))

    return texts


class HelpMenu(discord.ui.View):
    '''The page buttons under the help embed. Anyone can press them.
    They switch off after two minutes without a press.'''

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=timeout_seconds)
        self.embeds = embeds
        self.page = 0
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        '''Shows the page number and switches off the button that has nowhere to go.'''

        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = self.page == len(self.embeds) - 1
        self.page_number.label = f"page {self.page + 1}/{len(self.embeds)}"

    async def show_page(self, interaction: discord.Interaction, page: int):
        '''Flips the help message to the given page.'''

        self.page = max(0, min(page, len(self.embeds) - 1))
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="◀ back", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, self.page - 1)

    @discord.ui.button(label="page 1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_number(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="next ▶", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, self.page + 1)

    async def on_timeout(self):
        '''Greys out every button once the menu stops listening.'''

        for button in self.children:
            button.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
