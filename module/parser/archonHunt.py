from translator import ts


def w_archonHunt(archon, *lang):
    if archon == False:
        return ts.get("general.error-cmd")

    if archon is None:
        return None

    prefix: str = "cmd.archon-hunt"
    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"
    output_msg += f"{ts.get(f'{prefix}.eta')}: {archon['eta']}\n\n"

    idx: int = 1
    for value in archon["missions"]:
        output_msg += f"{idx}. {value['type']} - {value['node']}\n"
        idx += 1

    return output_msg
