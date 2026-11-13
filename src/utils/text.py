'''Small text helpers.'''


def plural(value: int, value_name: str) -> str:
    '''Useful for writing unit names with appropiate plurality.'''

    return f"{value} {value_name}{'s' if value != 1 else ''}"
