import random

from src.constants.structs import objects


def test_randmon_never_picks_past_the_last_pokemon(monkeypatch):
    '''Forces the highest roll: it must still be a real Pokemon.'''

    monkeypatch.setattr(random, "randint", lambda low, high: high)
    highest = objects.pokemon.randmon()

    assert highest == objects.pokemon.get_num_pokemon()
    assert objects.pokemon.by_number(str(highest)) is not None


def test_randmon_lowest_pick_is_the_first_pokemon(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: low)

    assert objects.pokemon.by_number(str(objects.pokemon.randmon())) == "bulbasaur"
