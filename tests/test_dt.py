import src.constants.getters.get_objs as get_objs
import src.constants.output.formatters as format

f = get_objs.fetcher

def test_dt():
    art = f.dt("galarian articuno")
    assert "Articuno-Galar" in art
    assert "_Psychic_/_Flying_" in art
    assert "Competitive" in art
    assert "**Dex #**: 144" in art

    sn = format.stat_names
    assert f"**{sn[0]}**: 90 | **{sn[1]}**: 85 | **{sn[2]}**: 85 | **{sn[3]}**: 125 | **{sn[4]}**: 100 | **{sn[5]}**: 95 | **BST**: 580\n" in art

    assert "Vulpix-Alola" in f.dt("alolan vulpix")
    assert f.dt("1026") == "i don't know what \"1026\" is... check your spelling?"
    assert "Garchomp" in f.dt("445")
    assert "_Dragon_/_Ground_" in f.dt("445")
    assert "Wailord" in f.dt("321")
    assert "Charizard-Mega-Y" in f.dt("mega charizard y")
    assert "_Fire_/_Flying_" in f.dt("zardy")
    assert "Bulbasaur" in f.dt("001")
    assert "Fishious Rend" in f.dt("fishious-rend")
    assert "**Blaze**" in f.dt("blaze")
    assert "**Rayquaza-Mega" in f.dt("mega rayquaza")
    assert "ummmm... \"diance\"? perhaps you meant diancie?" in f.dt("diance")
    assert f"**{format.generation}**: 9" in f.dt("tera shell")
    assert "Poke Ball" in f.dt("poke-ball")
    assert "Mega Punch" in f.dt("mega-punch")
    assert "Swords Dance" in f.dt("swords dance")
    assert "Komala" in f.dt("kamala")