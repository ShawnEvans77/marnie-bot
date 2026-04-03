import src.constants.getters.get_objs as get_objs

mon_tests = ["galarian articuno", "alolan vulpix", "1026", "445", "321", "112", "001", "fishious-rend", "blaze", "fire punch", "heavy duty boots", "poke-ball", "arceus", "tera shell", "dragon dance", "swords dance", "pikachu", "diance", "diance-mega", "leftovers", "choice band", "choice scarf",
         "bulbasaur", "vensaur", "mega rayquaza", "cinccino"]

for mon_tests in mon_tests:
    print(get_objs.fetcher.dt(mon_tests))
    print()