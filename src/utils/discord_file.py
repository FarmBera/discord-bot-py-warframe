import discord


def img_file(fname: str) -> discord.File | None:
    if not fname:
        return None
    return discord.File(f"img/{fname}.webp", filename="i.webp")
