def W_VoidTraders(trader):
    idx = 1
    length = len(trader)

    output_msg: str = f"# Void Traders Status\n\n"

    for item in trader:
        if length >= 2:
            output_msg += f"{idx}. Trader: {item['character']}\n\n"
            idx += 1
        else:
            output_msg += f"- Trader: {item['character']}\n"

        status = item["active"]

        # OO 나타남
        if status:
            output_msg += f"- Status: **Activated**\n"
            output_msg += f"- Ends at {item['endString']}\n"
            output_msg += f"- Location: "
        # XX 안나타남
        else:
            output_msg += f"- Status: *Deactivated*\n"
            output_msg += f"- Appears at {item['startString']}\n"
            output_msg += f"- Coming to: "

        # appear location
        output_msg += f"{item['location']}\n\n"

        # print(status)
        # print(item["activation"])
        # print(item["startString"])

    # print(output_msg)
    return output_msg
