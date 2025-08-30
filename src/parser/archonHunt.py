from src.translator import ts
from src.utils.return_err import err_text
from src.utils.formatter import time_cal_with_curr


def w_archonHunt(archon) -> str:
    if not archon:
        return err_text("archon hunt")

    pf: str = "cmd.archon-hunt."

    # output_msg = f"# {ts.get(f'{pf}title')}\n\n"  # legacy title
    output_msg = f"# {ts.get(f'{pf}{archon['boss']}')} {ts.get(f'{pf}hunt')}\n\n"
    output_msg += f"{ts.get(f'{pf}eta')}: "
    output_msg += f"{time_cal_with_curr(archon['expiry'])}\n\n"

    # TODO: ADD MSG: you can obtain 'shard kind' in this week

    value = archon["missions"]
    output_msg += f"1. {ts.trs(f"trs.{value[0]['type']}")} - {value[0]['node']}\n"
    output_msg += f"2. {ts.trs(f"trs.{value[1]['type']}")} - {value[1]['node']}\n"
    output_msg += f"3. {ts.get(f"{pf}{value[2]['type']}")} - {value[2]['node']}\n"

    # legacy body
    # idx: int = 1
    # for value in archon["missions"]:
    #     output_msg += f"{idx}. {ts.get(f"{pf}{value['type']}")} - {value['node']}\n"
    #     idx += 1

    return output_msg
