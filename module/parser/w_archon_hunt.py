def W_archonHunt(archon):
    output_msg = f"# Archon Hunt\n\n"

    idx: int = 1
    for value in archon["missions"]:
        output_msg += f"{idx}. {value['type']} - {value['node']}\n"
        idx += 1

    # print(output_msg)
    return output_msg
