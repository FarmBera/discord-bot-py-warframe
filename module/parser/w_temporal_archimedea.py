from translator import ts


def W_TemporalArchimedia(temporal, *lang) -> str:
    if temporal == False:
        return ts.get("general.error-cmd")

    if temporal is None:
        return None

    prefix = "cmd.temporal-archimedea"

    output_msg = f"# {ts.get(f'{prefix}.title')}\n\n"

    idx = 1
    for item in temporal["missions"]:
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
