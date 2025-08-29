import discord
from translator import ts
from variables.times import time_calculate_with_curr
from module.discord_file import img_file
from module.return_err import err_embed


def w_cambionCycle(cambion) -> tuple:
    if not cambion:
        return err_embed("cambion cycle")

    def color_decision(s):
        return 0x97D4D9 if s == "vome" else 0xECB448

    status: str = cambion["state"]

    output_msg = f"""### Cambion Cycle

# {status.capitalize()}

- expires in {time_calculate_with_curr(cambion['expiry'])} ({cambion['timeLeft']})
"""

    f = img_file(status)
    embed = discord.Embed(description=output_msg, color=color_decision(status))
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
