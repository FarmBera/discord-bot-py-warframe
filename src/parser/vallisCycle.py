import discord
from src.translator import ts
from src.utils.formatter import time_cal_with_curr
from src.utils.discord_file import img_file
from src.utils.return_err import err_embed


def w_vallisCycle(vallis) -> tuple:
    if not vallis:
        return err_embed("vallis cycle")

    def color_decision(s):
        return 0xFF9012 if s == "warm" else 0x00BFFF

    pf: str = "cmd.vallis."

    status: str = vallis["state"]
    output_msg = f"""### {ts.get(f'{pf}title')}

# < {ts.get(f'{pf}{status}')} >

- {ts.get(f'{pf}exp')} {time_cal_with_curr(vallis['expiry'])}
"""

    f = img_file(status)
    embed = discord.Embed(description=output_msg, color=color_decision(status))
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
