def pi(level, base, b, c):
    result = 0.0141 * level * level * (1.1 ** (0.1 * (c-1))) + 0.4969 * level * (1.2 ** (0.1 * (b-1))) + 8.49 + (base-9)
    return round(result, 2)

def color(level):
    switcher = {
        1: '<#23f108>',
        2: '<#73da00>',
        3: '<#96c100>',
        4: '<#aca800>',
        5: '<#bb8e00>',
        6: '<#c37300>',
        7: '<#c55700>',
        8: '<#c23700>',
        9: '<#ba0909>'
    }
    return switcher[level]