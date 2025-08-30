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

    idx: int = 1
    for value in archon["missions"]:
        if idx == 3:
            output_msg += (
                f"{idx}. " + ts.get(f"{pf}{value['type']}") + f" - {value['node']}\n"
            )
        else:
            output_msg += (
                f"{idx}. " + ts.trs(f"trs.{value['type']}") + f" - {value['node']}\n"
            )

        idx += 1

    return output_msg
