import discord

from src.parser.worldstate import weekly_remain
from src.translator import ts as _ts, language as _default_lang
from src.utils.data_manager import getSolNodeData
from src.utils.file_io import json_load
from src.utils.image import getThumbImg
from src.utils.times import timeNow

steel_incursions_data = json_load("data/steel-incursions.json")

pf: str = "cmd.steel-incursion."


def w_steelIncursions(ts=_ts, lang=_default_lang) -> discord.Embed:
    cnt: int = 0
    this_node = []
    for item in steel_incursions_data:
        if item["time"] > timeNow():
            this_node = steel_incursions_data[cnt - 1]["node"]
            break
        cnt += 1

    output_msg: str = ts.get(f"{pf}output").format(time=weekly_remain()).strip()

    idx: int = 1
    for item in this_node:
        node = getSolNodeData(item)
        output_msg += f"\n{idx}. **{node['type']}** - {node['value']}"
        idx += 1

    embed = discord.Embed(description=output_msg.strip(), color=0xB49D89)
    embed.set_thumbnail(url=getThumbImg("steel-essence"))
    return embed


# print(w_steelIncursions().description)
