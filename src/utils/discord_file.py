import discord


def img_file(fname) -> discord.File:
    return discord.File(f"img/{fname}.webp", filename="i.webp")
