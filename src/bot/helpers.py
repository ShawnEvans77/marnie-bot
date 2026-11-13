'''Small helpers shared by more than one cog.'''

import discord


def display_name(user) -> str:
    '''Returns a user's best available display name.'''

    return user.global_name or getattr(user, "display_name", None) or user.name


def find_by_name(people, query: str, name_fields: tuple[str, ...]):
    '''Finds the first person whose name fields match the query exactly, else the first partial match.'''

    cleaned = query.strip().lstrip("@").casefold()

    def names_for(person) -> list[str]:
        return [value.casefold() for value in (getattr(person, field, None) for field in name_fields) if value]

    people = list(people)

    for person in people:
        if cleaned in names_for(person):
            return person

    for person in people:
        if any(cleaned in value for value in names_for(person)):
            return person

    return None


def find_member(guild: discord.Guild, query: str) -> discord.Member | None:
    '''Finds a guild member by username, display name, or nickname.'''

    return find_by_name(guild.members, query, ("name", "display_name", "global_name"))


def find_user(users, query: str) -> discord.User | None:
    '''Finds a Discord user by username or global name outside a guild context.'''

    return find_by_name(users, query, ("name", "global_name"))
