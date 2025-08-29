from translator import ts
from module.return_err import err_text


def w_archonHunt(archon) -> str:
    if not archon:
        return err_text("archon hunt")

    pf: str = "cmd.archon-hunt"
    output_msg = f"# {ts.get(f'{pf}.title')}\n\n"
    output_msg += f"{ts.get(f'{pf}.eta')}: {archon['eta']}\n\n"

    idx: int = 1
    for value in archon["missions"]:
        output_msg += f"{idx}. {value['type']} - {value['node']}\n"
        idx += 1

    return output_msg
