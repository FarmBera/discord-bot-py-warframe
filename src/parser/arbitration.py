import discord

from src.translator import ts
from src.utils.data_manager import solNodes
from src.utils.file_io import json_load
from src.utils.image import getThumbImg
from src.utils.times import timeNow, convert_remain

ARBITRATION = json_load("data/arbys.json")

pf: str = "cmd.arbitration."


def w_arbitration() -> discord.Embed:
    cnt: int = 0  # count
    curr_arbi: dict = {}

    # search current data
    for item in ARBITRATION:
        if item["time"] > timeNow():
            curr_arbi = ARBITRATION[cnt - 1]
            break
        cnt += 1

    next_arbi = ARBITRATION[cnt]
    curr_arbi = solNodes[curr_arbi["node"]]

    # current mission
    output_msg: str = ts.get(f"{pf}output").format(
        miss=curr_arbi["type"],
        node=curr_arbi["value"],
        faction=curr_arbi["enemy"],
        time=convert_remain(next_arbi["time"]),
    )
    # next missions
    output_msg = output_msg.strip()
    for i in range(cnt, cnt + 6):
        present = ARBITRATION[i]

        output_msg += ts.get(f"{pf}outnext").format(
            time=convert_remain(present["time"]), miss=solNodes[present["node"]]["type"]
        )

    embed = discord.Embed(description=output_msg, color=discord.Color.greyple())
    embed.set_thumbnail(url=getThumbImg("vitus-essence"))
    return embed


# print(w_arbitration()[0].description)
