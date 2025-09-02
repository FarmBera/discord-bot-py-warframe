from src.translator import ts
from src.utils.return_err import err_text
from src.utils.formatter import time_cal_with_curr
from src.utils.emoji import get_emoji


shard_list: dict = {
    "Archon Boreal": "Azure",  # blue shard
    "Archon Amar": "Crimson",  # red shard
    "Archon Nira": "Amber",  # yellow shard
}


def w_archonHunt(archon) -> str:
    if not archon:
        return err_text("archon hunt")

    pf: str = "cmd.archon-hunt."
    shard: str = shard_list[archon["boss"]]

    # title
    output_msg = f"# " + ts.get(f"{pf}{archon['boss']}") + f" {ts.get(f'{pf}hunt')}\n\n"
    # eta
    output_msg += f"{ts.get(f'{pf}eta')}: "
    output_msg += f"{time_cal_with_curr(archon['expiry'])}\n"
    # additional msg
    output_msg += f"{ts.get(f'{pf}obt1')} {get_emoji(shard)} **{ts.trs(shard)} {ts.get(f'{pf}shardname')}** {ts.get(f'{pf}obt2')}\n\n"
    # print missions
    idx: int = 1
    for value in archon["missions"]:
        if idx == 3:
            output_msg += (
                f"{idx}. " + ts.get(f"{pf}{value['type']}") + f" - {value['node']}\n"
            )
        else:
            output_msg += f"{idx}. {ts.trs(value['type'])} - {value['node']}\n"
        idx += 1

    return output_msg
