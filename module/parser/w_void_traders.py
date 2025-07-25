from translator import ts


def W_VoidTraders(trader, lang):
    if not trader or trader is None:
        return ts.get("general.error-cmd")

    idx = 1
    length = len(trader)
    prefix: str = "cmd.void-traders"

    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"

    for item in trader:
        if length >= 2:
            output_msg += f"{idx}. {ts.get(f'{prefix}.tdr')}: {item['character']}\n\n"
            idx += 1
        else:
            output_msg += f"- {ts.get(f'{prefix}.tdr')}: {item['character']}\n"

        status = item["active"]

        # OO 나타남
        if status:
            output_msg += (
                f"- {ts.get(f'{prefix}.status')}: **{ts.get(f'{prefix}.activate')}**\n"
            )
            output_msg += f"- {ts.get(f'{prefix}.end')} {item['endString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.location')}: "
        # XX 안나타남
        else:
            output_msg += f"- {ts.get(f'{prefix}.status')}: *Deactivated*\n"
            output_msg += f"- {ts.get(f'{prefix}.appear')} {item['startString']}\n"
            output_msg += f"- {ts.get(f'{prefix}.place')}: "

        # appear location
        output_msg += f"{item['location']}\n\n"

        # print(status)
        # print(item["activation"])
        # print(item["startString"])

    # print(output_msg)
    return output_msg
