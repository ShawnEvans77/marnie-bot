import pytest
import src.constants.getters.get_objs as get_objs

w = get_objs.weaker

@pytest.mark.parametrize('query, expected', [
    
        ('fire', "Fire:\n**Weaknesses:** Ground, Rock, Water\n**Resistances:** Bug, Fairy, Fire, Grass, Ice, Steel\n**Immunities:** None"),
])

def test_weak(query, expected):
    assert w.weak(query) == expected