from translator import ts


def W_DeepArchimedea(deep, *lang) -> str:
    if deep == False:
        return ts.get("general.error-cmd")

    if deep is None:
        return None

    prefix = f"cmd.deep-archimedea"

    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"

    idx = 1
    for item in deep["missions"]:
        output_msg += f"### {idx}. {item['mission']}\n\n"
        for jtem in item["riskVariables"]:
            output_msg += f"- {jtem['name']}"
            desc = jtem["description"]
            if desc[0:3] in "[PH]":
                output_msg += "\n"
                continue
            output_msg += f": {desc}\n"
        output_msg += f"\n"
        idx += 1

    return output_msg
