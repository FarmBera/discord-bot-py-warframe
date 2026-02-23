import discord

from src.constants.keys import FIELD_PATTERN as pat
from src.parser.worldstate import weekly_remain
from src.translator import ts
from src.utils.emoji import get_emoji
from src.utils.return_err import err_embed

color_list = {
    "Umbra Forma Blueprint": 0x00FFFF,
    "50,000 Kuva": 0xB02121,
    "3x Forma": 0xFBFF24,
    "30,000 Endo": 0xFBFF24,
    "Kitgun Riven Mod": 0xA11EE3,
    "Zaw Riven Mod": 0xA11EE3,
    "Rifle Riven Mod": 0xA11EE3,
    "Shotgun Riven Mod": 0xA11EE3,
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
}
pf: str = "cmd.steel-path-reward."


def w_steelPath(steel) -> tuple[discord.Embed, str]:
    if not steel:
        return err_embed("steelPath"), ""

    curr_idx: int = steel["currentReward"]
    stl = steel["rotation"]
    length: int = len(stl)

    # current item
    current_reward_item = stl[curr_idx]
    cname: str = current_reward_item["name"]

    output_msg = ts.get(f"{pf}output").format(timer=weekly_remain())

    # data list
    weeks: list = []
    items: list = []
    costs: list = []

    # print item list
    for i in range(length):
        target_item = stl[i]
        origin_name = target_item["name"]
        name = f"{get_emoji(origin_name)} {ts.trs(origin_name)}"
        cost = f"{target_item['cost']}x {get_emoji('essense')}"

        # this week item
        if i == curr_idx:
            weeks.append(f"__**{ts.get(f'{pf}current')}**__")
            items.append(f"__**{name}**__")
            costs.append(f"__**{cost}**__")
        else:
            if i > curr_idx:
                delta = i - curr_idx
            else:
                delta = length - curr_idx + i
            delta -= 1

            weeks.append(weekly_remain(delta))
            items.append(name)
            costs.append(cost)

    embed = discord.Embed(
        description=output_msg.strip(),
        colour=color_list.get(cname, discord.Color.darker_grey()),
    )
    embed.set_thumbnail(url="attachment://i.webp")

    embed.add_field(name=ts.get(f"{pf}week"), value=pat.join(weeks), inline=True)
    embed.add_field(name=ts.get(f"{pf}item"), value=pat.join(items), inline=True)
    embed.add_field(name=ts.get(f"{pf}cost"), value=pat.join(costs), inline=True)

    return embed, img_list.get(cname, "")


# from src.utils.data_manager import get_obj
# from src.constants.keys import STEELPATH
# print(w_steelPath(get_obj(STEELPATH))[0].fields[1].value)
