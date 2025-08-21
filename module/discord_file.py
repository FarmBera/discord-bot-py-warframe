import discord


def img_file(fname) -> discord.File:
    return discord.File(f"img/{fname}.png", filename="i.png")
