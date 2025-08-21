import discord
from translator import ts
from module.discord_file import img_file


def w_cambionCycle(cambion, *lang):
    if cambion == False:
        return (
            discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000),
            None,
        )

    if cambion is None:
        return None

    def color_decision(s):
        return 0x97D4D9 if s == "vome" else 0xECB448

    status: str = cambion["state"]

    output_msg = f"""### Cambion Cycle

# {status.capitalize()}

- expires in '{cambion['timeLeft']}'
"""

    f = img_file(status)
    embed = discord.Embed(description=output_msg, color=color_decision(status))
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
