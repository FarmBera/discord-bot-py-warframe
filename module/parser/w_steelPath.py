import discord
from translator import ts
from module.discord_file import img_file


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

img_list = {
    "Umbra Forma Blueprint": "umbra-forma",
    "50,000 Kuva": "kuva",
    "Kitgun Riven Mod": "riven-mod",
    "3x Forma": "forma",
    "Zaw Riven Mod": "riven-mod",
    "30,000 Endo": "endo",
    "Rifle Riven Mod": "riven-mod",
    "Shotgun Riven Mod": "riven-mod",
}


def W_SteelPathReward(steel, *lang):
    if steel == False:
        return (
            discord.Embed(description=ts.get("general.error-cmd"), color=0xFF0000),
            None,
        )

    if steel is None:
        return None

    pf: str = "cmd.steel-path-reward"

    current = steel["currentReward"]
    cname: str = current["name"]
    output_msg: str = f"# {ts.get(f'{pf}.title')}\n\n"

    # current reward
    output_msg += f"- {ts.get(f'{pf}.curr-reward')}: **{cname}** ({current['cost']} {ts.get(f'{pf}.cost')})\n"

    # next week reward
    idx = 0
    for item in steel["rotation"]:
        # next week item
        if item["name"] == cname:
            idx += 1
            if idx >= len(steel["rotation"]):  # fix index overflow
                idx = 0

            # output
            item = steel["rotation"][idx]
            output_msg += f"- {ts.get(f'{pf}.next')}: *{item['name']}* ({item['cost']} {ts.get(f'{pf}.cost')})"
            break
        else:
            idx += 1

    f = img_file(img_list[cname])
    embed = discord.Embed(description=output_msg, colour=color_list[cname])
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
