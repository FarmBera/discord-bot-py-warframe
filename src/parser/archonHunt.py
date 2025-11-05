from src.translator import ts
from src.constants.times import convert_remain
from src.utils.return_err import err_text
from src.utils.emoji import get_emoji
from src.utils.data_manager import getMissionType, getSolNode


shard_list: dict = {
    "SORTIE_BOSS_BOREAL": "Azure",  # blue shard
    "SORTIE_BOSS_AMAR": "Crimson",  # red shard
    "SORTIE_BOSS_NIRA": "Amber",  # yellow shard
}


def w_archonHunt(archon) -> str:
    if not archon:
        return err_text("archon hunt")

    archon = archon[0]
    pf: str = "cmd.archon-hunt."
    shard: str = shard_list[archon["Boss"]]

    # title
    output_msg = (
        f"# {ts.get(f'{pf}archon')} "
        + ts.get(f"{pf}{archon['Boss']}")
        + f" {ts.get(f'{pf}hunt')}\n\n"
    )
    # eta
    output_msg += f"{ts.get(f'{pf}eta')}: "
    output_msg += f"{convert_remain(archon['Expiry']['$date']['$numberLong'])}\n"
    # additional msg (obtain shard)
    output_msg += ts.get(f"{pf}obt").format(emoji=get_emoji(shard), shard=ts.trs(shard))
    # print missions
    idx: int = 1
    for value in archon["Missions"]:
        if idx == 3:
            output_msg += (
                f"{idx}. "
                + ts.get(f"{pf}{getMissionType(value['missionType'])}")
                + f" - {getSolNode(value['node'])}\n"
            )
        else:
            output_msg += f"{idx}. {getMissionType(value['missionType'])} - {getSolNode(value['node'])}\n"
        idx += 1

    return output_msg
