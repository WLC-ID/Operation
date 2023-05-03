def pi(level, base, b, c):
    result = 0.0141 * level * level * (1.1 ** (0.1 * (c-1))) + 0.4969 * level * (1.2 ** (0.1 * (b-1))) + 8.49 + (base-9)
    return round(result, 2)

def pio(level, offset, base, b, c):
    lx = level+offset
    result = 0.0141 * lx * lx * (1.1 ** (0.1 * (c-1))) + 0.4969 * lx * (1.2 ** (0.1 * (b-1))) + 8.49 + (base-9)
    return round(result, 2)

def color(level):
    # https://colordesigner.io/gradient-generator
    # HSL
    assert level != None and type(level) is int and level > 0
    if level > 100:
        level = (level % 100)
        if (level == 0):
            level = 100
    switcher = [
        '<#23f108>', '<#52eb08>', '<#7ee508>', '<#a8de09>', '<#cfd809>',
        '<#d2b109>', '<#cc8409>', '<#c65809>', '<#c02f09>', '<#ba0909>',
        '<#c0091f>', '<#c60936>', '<#cd094f>', '<#d3096a>', '<#d90986>',
        '<#e009a3>', '<#e609c2>', '<#ec08e3>', '<#e008f3>', '<#c80af7>',
        '<#b50af7>', '<#a20af7>', '<#8f0af7>', '<#7c0af7>', '<#690af7>',
        '<#560af7>', '<#430af7>', '<#300af7>', '<#1d0af7>', '<#0a0af7>',
        '<#0a21f7>', '<#0a38f7>', '<#0a4ff7>', '<#0a66f7>', '<#0a7cf7>',
        '<#0a93f7>', '<#0aaaf7>', '<#0ac1f7>', '<#0ad8f7>', '<#0aeff7>',
        '<#1cf1f5>', '<#2ef3f4>', '<#40f3f1>', '<#51f2ee>', '<#62f2ec>',
        '<#73f1eb>', '<#84f2ea>', '<#94f2eb>', '<#a4f3eb>', '<#b3f4ed>',
        '<#b3f0ea>', '<#b4ece8>', '<#b4e8e4>', '<#b5e4e1>', '<#b6dfdd>',
        '<#b8dad9>', '<#b9d5d4>', '<#bbd0cf>', '<#becaca>', '<#c0c4c4>',
        '<#b1b5b5>', '<#a1a6a6>', '<#929797>', '<#838888>', '<#757878>',
        '<#666969>', '<#575959>', '<#494a4a>', '<#3a3a3a>', '<#2b2b2b>',
        '<#2a2827>', '<#292522>', '<#28231e>', '<#26201b>', '<#241d17>',
        '<#2c231c>', '<#342920>', '<#3c2f24>', '<#443529>', '<#4c3b2d>',
        '<#554131>', '<#5d4735>', '<#664d39>', '<#6e533c>', '<#775940>',
        '<#7e613e>', '<#856b3b>', '<#8c7638>', '<#938435>', '<#9b9432>',
        '<#a0a32f>', '<#9bab2b>', '<#95b327>', '<#8cbb23>', '<#81c41f>',
        '<#73cc1b>', '<#63d517>', '<#51de12>', '<#3be80d>', '<#47f130>',
    ]
    return switcher[level-1]