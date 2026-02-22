import discord

from src.translator import ts
from src.utils.data_manager import solNodes
from src.utils.file_io import json_load
from src.utils.image import getThumbImg
from src.utils.times import timeNow

steel_incursions_data = json_load("data/steel-incursions.json")

pf: str = "cmd.steel-incursion."


def w_steelIncursions() -> discord.Embed:
    cnt: int = 0
    this_node = []
    for item in steel_incursions_data:
        if item["time"] > timeNow():
            this_node = steel_incursions_data[cnt - 1]["node"]
            # print(item["time"])
            # print(item["node"])
            # print(cnt)
            break
        cnt += 1

    output_msg: str = ts.get(f"{pf}output")

    idx: int = 1
    for item in this_node:
        node = solNodes[item]
        output_msg += f"\n{idx}. **{node['type']}** - {node['value']}"
        idx += 1

    embed = discord.Embed(description=output_msg.strip(), color=0xB49D89)
    embed.set_thumbnail(url=getThumbImg("steel-essence"))
    return embed


# print(w_steelIncursions()[0].description)
