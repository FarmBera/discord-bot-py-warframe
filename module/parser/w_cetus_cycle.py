# cetus day/night state & cycle
def W_CetusCycle(cetus):
    if not cetus or cetus is None:
        return False

    output_msg = f"# Cetus Day/Night Cycle\n\n"
    output_msg += f"- Current State >> {cetus['state']}\n"
    output_msg += f"- {cetus['timeLeft']} to {'Night' if cetus['isDay'] else 'Day'}"

    # print(output_msg)
    return output_msg
