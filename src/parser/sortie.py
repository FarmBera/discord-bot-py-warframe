from enum import Enum, auto

import discord

from src.constants.keys import FIELD_PATTERN as pat
from src.translator import ts
from src.utils.data_manager import getMissionType, getSolNode, getSortieMod
from src.utils.times import convert_remain


class Mode(Enum):
    text = auto()
    field = auto()


pf: str = "cmd.sortie."


def w_sortie(sortie):
    if not sortie:
        return ts.get("general.error-cmd")

    sortie = sortie[0]

    # id = dd["_id"]["$oid"]
    # activation = int(dd["Activation"]["$date"]["$numberLong"])
    expiry = int(sortie["Expiry"]["$date"]["$numberLong"])

    # title
    output_msg: str = f"# {ts.get(f'{pf}title')}\n\n"
    # expiry
    output_msg += f"- {ts.get(f'{pf}eta').format(eta=convert_remain(expiry))}\n\n"

    mode = Mode.text
    f_type = []
    f_node = []
    f_mod = []

    # mission list
    idx = 1
    for i in sortie["Variants"]:
        miss_type = getMissionType(i["missionType"])
        node = getSolNode(i["node"])
        mod_type = getSortieMod(i["modifierType"])

        if mode == Mode.text:
            output_msg += f"{idx}. **{miss_type}** "
            output_msg += f"/ {node} - *{mod_type}*\n"
        elif mode == Mode.field:
            f_type.append(f"{idx}. {miss_type}")
            f_node.append(node)
            f_mod.append(mod_type)

        idx += 1

    embed = discord.Embed(
        description=output_msg,
        color=discord.Color.darker_grey(),
        # color=embed_color if embed_color else color_decision(trader),
    )
    if mode == Mode.field:
        embed.add_field(name=ts.get(f"{pf}type"), value=pat.join(f_type))
        embed.add_field(name=ts.get(f"{pf}node"), value=pat.join(f_node))
        embed.add_field(name=ts.get(f"{pf}mod"), value=pat.join(f_mod))

    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "sortie"
