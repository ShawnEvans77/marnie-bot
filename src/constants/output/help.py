'''The words in Marnie's help menu.

Each page has a title, an emoji, a short blurb, and its commands.
Each command is (emoji, usage, description). Usage is written without the command prefix.'''

intro = "type a command just like the examples. i'll forgive your typos! <3"

pages = (
    {
        "title": "pokemon commands",
        "emoji": "🌸",
        "blurb": "everything i know about pokemon!",
        "commands": (
            ("📖", "dt {query}", "info on a pokemon, ability, item, or move. you can look pokemon up by name or dex number, like ``!dt morpeko`` or ``!dt 877``."),
            ("🛡️", "weak {type or pokemon}", "weaknesses, resistances, and immunities of a type or a pokemon. for two types, split them with a slash or a comma, like ``!weak fire/water``."),
            ("🎲", "randmon", "info on a random pokemon."),
            ("👾", "sprite {pokemon}", "a pokemon's sprite, by name or dex number."),
            ("✨", "shiny {pokemon}", "a pokemon's shiny sprite, by name or dex number."),
            ("🎨", "art {pokemon}", "a pokemon's big official artwork, by name or dex number."),
            ("🎁", "randsprite", "a random pokemon's sprite."),
            ("🖼️", "randart", "a random pokemon's official artwork."),
        ),
    },
    {
        "title": "fun & server commands",
        "emoji": "🎀",
        "blurb": "games, chat stats, and server stuff!",
        "commands": (
            ("❓", "wtp", "who's that pokemon! i show a silhouette, and the first person to type its name within 30 seconds wins. forms don't matter, so \"landorus\" is right for landorus-therian."),
            ("🎯", "pick {options...}", "i pick one option at random. split them with commas, like ``!pick socks, shoes``."),
            ("☁️", "wc {user}", "a word cloud from up to 10000 recent messages in this channel. add a username or nickname to see just that person's words."),
            ("🏆", "top", "the top 3 chatters in this channel, out of up to 10000 recent messages. bots, commands, and people who left don't count."),
            ("🔇", "muted", "everyone who is timed out, and for how much longer."),
            ("🪪", "id {user}", "a discord id. with no name it's yours, with a username or nickname it's theirs."),
        ),
    },
)
