import discord
from src.translator import ts
from src.utils.discord_file import img_file
from src.utils.return_err import err_embed

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


def w_steelPath(steel) -> tuple:
    if not steel:
        return err_embed("steelPath")

    pf: str = "cmd.steel-path-reward"

    current = steel["currentReward"]
    cname: str = current["name"]
    output_msg: str = f"# {ts.get(f'{pf}.title')}\n\n"

    # current reward
    output_msg += f"- {ts.get(f'{pf}.curr-reward')}: **{ts.trs(f'trs.{cname}')}** ({current['cost']} {ts.get(f'{pf}.cost')})\n"

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
            output_msg += f"- {ts.get(f'{pf}.next')}: *{ts.trs(f'trs.{item['name']}')}* ({item['cost']} {ts.get(f'{pf}.cost')})"
            break
        else:
            idx += 1

    f = img_file(img_list[cname])
    embed = discord.Embed(description=output_msg, colour=color_list[cname])
    embed.set_thumbnail(url="attachment://i.png")

    return embed, f
