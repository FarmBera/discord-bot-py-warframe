import discord
from src.translator import ts
from src.utils.return_err import err_embed

color_list = {
    "Umbra Forma Blueprint": 0x00FFFF,
    "50,000 Kuva": 0xB02121,
    "3x Forma": 0xA11EE3,
    "30,000 Endo": 0xFBFF24,
    "Kitgun Riven Mod": 0xA11EE3,
    "Zaw Riven Mod": 0xA11EE3,
    "Rifle Riven Mod": 0xA11EE3,
    "Shotgun Riven Mod": 0xA11EE3,
    "주 무기 리벤 모드": 0xA11EE3,
    "산탄총 리벤 모드": 0xA11EE3,
}

img_list = {
    "Umbra Forma Blueprint": "umbra-forma",
    "50,000 Kuva": "kuva",
    "3x Forma": "forma",
    "30,000 Endo": "endo",
    "Kitgun Riven Mod": "riven-mod",
    "Zaw Riven Mod": "riven-mod",
    "Rifle Riven Mod": "riven-mod",
    "Shotgun Riven Mod": "riven-mod",
    "주 무기 리벤 모드": "riven-mod",
    "산탄총 리벤 모드": "riven-mod",
}

pf: str = "cmd.steel-path-reward."


def w_steelPath(steel) -> tuple[discord.Embed, str]:
    if not steel:
        return err_embed("steelPath"), ""

    curr_idx: int = steel["currentReward"]
    current: dict = steel["rotation"][curr_idx]

    cname: str = current["name"]
    cost = current["cost"]

    output_msg: str = f"# {ts.get(f'{pf}title')}\n\n"

    # current reward
    output_msg += f"- {ts.get(f'{pf}curr-reward')}: **{ts.trs(cname)}** ({cost} {ts.get(f'{pf}cost')})\n"

    # next week reward
    idx = 0
    stl = steel["rotation"]
    for item in stl:
        if item["name"] == cname:
            idx = (idx + 1) % len(stl)

            # output
            item = stl[idx]
            output_msg += f"- {ts.get(f'{pf}next')}: *{ts.trs(item['name'])}* ({item['cost']} {ts.get(f'{pf}cost')})"
            break
        else:
            idx += 1

    f = img_list[cname]
    embed = discord.Embed(description=output_msg, colour=color_list[cname])
    embed.set_thumbnail(url="attachment://i.webp")

    return embed, f
