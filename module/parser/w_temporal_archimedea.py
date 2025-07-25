from translator import ts


def W_TemporalArchimedia(temporal, lang) -> str:
    if not temporal or temporal is None:
        return ts.get("general.error-cmd")

    output_msg = f"# Temporal Archimedia\n\n"

    idx = 1
    for item in temporal["missions"]:
        output_msg += f"## {idx}. {"Capture" if item['mission'] == 'EndlessCapture' else item['mission']}\n\n"

        devi = item["deviation"]
        output_msg += f"- Deviation: {devi['name']}"
        desc = devi["description"]
        if desc[0:3] == "[PH]":
            output_msg += "\n"
        else:
            output_msg += desc
        output_msg += "\n"

        output_msg += "- Risk Variation\n"
        for jtem in item["riskVariables"]:
            output_msg += f"    - {jtem['name']}"
            desc = jtem["description"]
            if desc[0:3] in "[PH]":
                output_msg += "\n"
                continue
            output_msg += f": {desc}\n"

        output_msg += "\n"
        # for jtem in item["riskVariables"]:
        idx += 1

    # print(output_msg)
    return output_msg
