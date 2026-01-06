import discord
from src.translator import ts
from src.utils.times import convert_remain
from src.utils.return_err import err_embed
from src.utils.emoji import get_emoji
from src.utils.data_manager import getMissionType, getSolNode


S_BLUE = "Azure"
S_RED = "Crimson"
S_YEL = "Amber"

shard_list: dict = {
    "SORTIE_BOSS_BOREAL": S_BLUE,
    "SORTIE_BOSS_AMAR": S_RED,
    "SORTIE_BOSS_NIRA": S_YEL,
}

shard_color: dict = {
    S_BLUE: 0x4EB8FC,
    S_RED: 0xEE575C,
    S_YEL: 0xE6CB38,
}

pf: str = "cmd.archon-hunt."


def w_archonHunt(archon) -> tuple[discord.Embed, str]:
    """
    parse archon hunt data

    :param archon: archon hunt data
    :return: parsed archon hunt data & img file name
    """
    if not archon:
        return err_embed("archon hunt"), ""

    archon = archon[0]
    shard: str = shard_list[archon["Boss"]]

    # title
    output_msg = (
        f"# {ts.get(f'{pf}archon')} "
        + ts.get(f"{pf}{archon['Boss']}")
        + f" {ts.get(f'{pf}hunt')}\n\n"
    )
    # eta
    output_msg += f"{ts.get(f'{pf}eta').format(time=convert_remain(archon['Expiry']['$date']['$numberLong']))}\n"
    # additional msg (obtain shard)
    output_msg += ts.get(f"{pf}obt").format(emoji=get_emoji(shard), shard=ts.trs(shard))
    # print missions
    idx: int = 1
    for value in archon["Missions"]:
        if idx == 3:
            output_msg += (
                f"{idx}. **"
                + ts.get(f"{getMissionType(value['missionType'])}")
                + f"** - {getSolNode(value['node'])}\n"
            )
        else:
            output_msg += f"{idx}. {getMissionType(value['missionType'])} - {getSolNode(value['node'])}\n"
        idx += 1

    f = "archon"
    embed = discord.Embed(description=output_msg, color=shard_color[shard])
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, f
