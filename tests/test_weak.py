import pytest
import src.constants.getters.get_objs as get_objs

w = get_objs.weaker

@pytest.mark.parametrize('query, expected', [
        ('fire', "Fire:\n**Weaknesses:** Ground, Rock, Water\n**Resistances:** Bug, Fairy, Fire, Grass, Ice, Steel\n**Immunities:** None"),
        ('metagross', "Metagross - (Steel/Psychic):\n**Weaknesses:** Dark, Fire, Ghost, Ground\n**Resistances:** Dragon, Fairy, Flying, Grass, Ice, Normal, **Psychic**, Rock, Steel\n**Immunities:** Poison")
])
def test_weak(query: str, expected: str):
    assert w.weak(query) == expected

@pytest.mark.parametrize('type_1, type_2, expected', [
        ('fire', 'fairy', "Fire/Fairy:\n**Weaknesses:** Ground, Poison, Rock, Water\n**Resistances:** **Bug**, Dark, Fairy, Fighting, Fire, Grass, Ice\n**Immunities:** Dragon")
])
def test_weak(type_1: str, type_2: str, expected: str):
    assert w.weak(type_1, type_2) == expected