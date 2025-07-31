from translator import ts


def W_VoidTraders(trader, *lang):
    if trader == False:
        return ts.get("general.error-cmd")

    if trader is None:
        return None

    idx = 1
    length = len(trader)
    prefix: str = "cmd.void-traders"

    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"

    for item in trader:
        if length >= 2:
            output_msg += (
                f"{idx}. {ts.get(f'{prefix}.tdr-name')}: {item['character']}\n\n"
            )
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{prefix}.tdr-name')}: {item['character']}\n"

        status = item["active"]

        # OO appeared
        if status:
            output_msg += (
                f"- {ts.get(f'{prefix}.status')}: **{ts.get(f'{prefix}.activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{prefix}.end')} {item['endString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.location')}: "
        # XX NOT appeared
        else:
            output_msg += f"- {ts.get(f'{prefix}.status')}: *Deactivated*\n"
            output_msg += f"- {ts.get(f'{prefix}.appear')} {item['startString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.place')}: "

        # appear location
        output_msg += f"{item['location']}\n\n"

    return output_msg


def W_voidTradersItem(traderItem, *lang):
    return None
