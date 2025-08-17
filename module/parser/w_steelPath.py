import discord
from translator import ts


color_list = {
    "Umbra Forma Blueprint": 0x00FFFF,
    "50,000 Kuva": 0xB02121,
    "Kitgun Riven Mod": 0xA11EE3,
    "3x Forma": 0xA11EE3,
    "Zaw Riven Mod": 0xA11EE3,
    "30,000 Endo": 0xFBFF24,
    "Rifle Riven Mod": 0xA11EE3,
    "Shotgun Riven Mod": 0xA11EE3,
}


def W_SteelPathReward(steel, *lang):
    if steel == False:
        return ts.get("general.error-cmd")

    if steel is None:
        return None

    pf: str = "cmd.steel-path-reward"

    current = steel["currentReward"]
    output_msg: str = f"# {ts.get(f'{pf}.title')}\n\n"

    # current reward
    output_msg += f"- {ts.get(f'{pf}.curr-reward')}: **{current['name']}** ({current['cost']} {ts.get(f'{pf}.cost')})\n"

    # calculate next week item
    idx = 0
    for item in steel["rotation"]:
        # next week item
        if item["name"] == current["name"]:
            idx += 1
            if idx >= len(steel["rotation"]):  # fix index overflow
                idx = 0

            # output
            item = steel["rotation"][idx]
            output_msg += f"- {ts.get(f'{pf}.next')}: *{item['name']}* ({item['cost']} {ts.get(f'{pf}.cost')})"
            break
        else:
            idx += 1
    embed = discord.Embed(description=output_msg, colour=color_list[current["name"]])

    return embed
