import discord


def img_file(fname) -> discord.File | None:
    if not fname:
        return None
    return discord.File(f"img/{fname}.webp", filename="i.webp")
