from translator import ts


# cetus day/night state & cycle
def W_CetusCycle(cetus, lang) -> str:
    if not cetus or cetus is None:
        return ts.get("general.error-cmd")

    prefix: str = "cmd.cetus"
    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"
    output_msg += f"- {ts.get(f'{prefix}.current')} >> {cetus['state']}\n"
    output_msg += f"- {cetus['timeLeft']} to"
    output_msg += (
        ts.get(f"{prefix}.night") if cetus["isDay"] else ts.get(f"{prefix}.day")
    )

    return output_msg
