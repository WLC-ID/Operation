def pi(level, base, b, c):
    result = 0.0141 * level * level * (1.1 ** (0.1 * (c-1))) + 0.4969 * level * (1.2 ** (0.1 * (b-1))) + 8.49 + (base-9)
    return round(result, 2)

def pio(level, offset, base, b, c):
    lx = level+offset
    result = 0.0141 * lx * lx * (1.1 ** (0.1 * (c-1))) + 0.4969 * lx * (1.2 ** (0.1 * (b-1))) + 8.49 + (base-9)
    return round(result, 2)

def color(level):
    # 1 ke 9, 9 ke 15
    # https://colordesigner.io/gradient-generator
    switcher = {
        1: '<#23f108>',
        2: '<#73da00>',
        3: '<#96c100>',
        4: '<#aca800>',
        5: '<#bb8e00>',
        6: '<#c37300>',
        7: '<#c55700>',
        8: '<#c23700>',
        9: '<#ba0909>',
        10:'<#c50029>',
        11:'<#cb0045>',
        12:'<#c90065>',
        13:'<#bc0088>',
        14:'<#a100ab>',
        15:'<#7014cc>'
    }
    return switcher[level]