import discord

from src.translator import ts
from src.utils.data_manager import getLanguage
from src.utils.emoji import get_emoji
from src.utils.return_err import err_embed

CODE_REWARD: str = "CET_REWARD"
CODE_CHALLENGE: str = "CET_CHALLENGE"

pf: str = "cmd.calendar."


def w_calendar(calendar) -> tuple[discord.Embed, str]:
    if not calendar:
        return err_embed("calendar"), ""

    output_msg: str = f"# {ts.get(f'{pf}title')}\n"
    prize: list = []
    todo: list = []

    idx: int = 0
    for day in calendar[0]["Days"]:
        event = day["events"]
        if len(event) <= 0:  # empty objects
            continue

        tmp: str = f"- Day {day['day']}: "
        # noinspection PyUnusedLocal
        tmp_emoji: list = []
        tmp_list: list = []
        for jtem in event:
            e_type = jtem["type"]

            # reward
            if e_type == CODE_REWARD:  # var
                tt = jtem["reward"]
                # tmp_emoji.append(get_emoji(tt))
                # tmp_list.append(getLanguage(tt))
                tmp_list.append(f"{get_emoji(tt)} {getLanguage(tt)}")

            # challenge
            elif e_type == CODE_CHALLENGE:  # var
                tmp_list.append(f"{getLanguage(jtem['challenge'],'desc')}")

            # # override
            # elif e_type == "CET_UPGRADE":  # var
            #     desc = jtem["upgrade"]
            #     override_info = f"\n- {getLanguage(desc)}: {getLanguage(desc,'desc')}"
            #     override.append(override_info)

        if event[0]["type"] == CODE_REWARD:
            prize.append(tmp + " / ".join(tmp_list))
            # prize.append(tmp + f"[{' / '.join(tmp_emoji)}] " + ", ".join(tmp_list))
        elif event[0]["type"] == CODE_CHALLENGE:
            todo.append(tmp + ", ".join(tmp_list))

        idx += 1

    output_msg += ts.get(f"{pf}prize")
    for day in prize:
        output_msg += f"{day}\n"

    output_msg += ts.get(f"{pf}todo")
    for day in todo:
        output_msg += f"{day}\n"

    embed = discord.Embed(description=output_msg, color=discord.Color.greyple())
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "hex"


# from src.utils.data_manager import get_obj
# from src.constants.keys import CALENDAR
# print(w_calendar(get_obj(CALENDAR))[0].description)
