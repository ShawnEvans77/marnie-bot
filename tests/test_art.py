import pytest
import src.constants.getters.get_objs as get_objs

f = get_objs.fetcher

ART_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"


class FakeResponse:
    def __init__(self, data: dict):
        self.data = data

    def json(self) -> dict:
        return self.data


@pytest.mark.parametrize('query, expected', [
    ('pikachu', [ART_URL + "25.png", "pikachu"]),
    ('25', [ART_URL + "25.png", "pikachu"]),
    ('pikachuu', [ART_URL + "25.png", "pikachu"]),
    ('mega alakazam', [ART_URL + "10037.png", "alakazam-mega"]),
    ('landorus', [ART_URL + "645.png", "landorus-incarnate"]),
    ('zard', [ART_URL + "6.png", "charizard"]),
    ('qwertyuiopasdf', "i don't think qwertyuiopasdf is a pokemon... check your spelling?"),
])
def test_art(query: str, expected):
    assert f.art(query) == expected


@pytest.mark.parametrize('data', [
    {"sprites": {"front_default": "sprite.png", "other": {"official-artwork": {"front_default": None}}}},
    {"sprites": {"front_default": "sprite.png", "other": None}},
    {"sprites": {"front_default": "sprite.png"}},
    {},
])
def test_art_missing(data: dict):
    assert f.get_art("snom", FakeResponse(data)) == "sorry, snom has no art right now"


def test_sprite_still_works_after_sharing_lookup_with_art():
    sprite_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"

    assert f.sprite('pikachu', shiny=False) == [sprite_url + "25.png", "pikachu"]
    assert f.sprite('pikachu', shiny=True) == [sprite_url + "shiny/25.png", "pikachu"]
