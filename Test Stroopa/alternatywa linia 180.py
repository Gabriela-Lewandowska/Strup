else:
    bodziec = 0
    kolor = random.choice("pink", "red", "green", "blue")
    tablicaSlow=conf['STIM_TEXT']
    stim.color=kolor
    if kolor=="pink":
        nowa = tablicaSlow.remove("RÓ\u017BOWY")
        stim.text=random.choice(tablicaSlow)
        tablicaSlow.append("RÓ\u017BOWY")
    if kolor=="red":
        nowa = tablicaSlow.remove("CZERWONY")
        stim.text=random.choice(tablicaSlow)
        tablicaSlow.append("CZERWONY")
    if kolor=="green":
        nowa = tablicaSlow.remove("ZIELONY")
        stim.text=random.choice(tablicaSlow)
        tablicaSlow.append("ZIELONY")
    if kolor=="blue":
        nowa = tablicaSlow.remove("NIEBIESKI")
        stim.text=random.choice(tablicaSlow)
        tablicaSlow.append("NIEBIESKI")
