import discord
import datetime as dt

from src.translator import ts
from src.utils.times import check_timer_states
from src.utils.return_err import err_embed


class CetusTimerData:
    name = "Cetus Day/Night Cycle"
    start_date = dt.datetime(2021, 2, 5, 12, 27, 54, tzinfo=dt.timezone.utc)
    looptime = 8998.874  # total 150m
    delaytime = 3000  # Night 50m
    beforetext = "day"
    aftertext = "night"


cetus_color = {"day": 0xFFBB00, "night": 0x2B79FF}

previous_state_cetus: str = check_timer_states(CetusTimerData)["current"]

pf: str = "cmd.cetus."


def checkNewCetusState() -> bool:
    """check cetus state changed

    :return: True if changed (different) else False (same state)
    """
    global previous_state_cetus
    current = check_timer_states(CetusTimerData)["current"]
    if previous_state_cetus != current:
        previous_state_cetus = current
        return True
    return False


# cetus day/night state & cycle
def w_cetusCycle() -> tuple[discord.Embed, str]:
    # calculate cetus cycle
    try:
        cetus = check_timer_states(CetusTimerData)
        if not cetus:
            raise ValueError("ERROR FETCHING CETUS DATA")
    except Exception:
        return err_embed("cetusCycle"), ""

    curr_state = cetus.get("current")

    # generate output msg
    output_msg: str = ts.get(f"{pf}output").format(
        curr_state=ts.get(f"{pf}{curr_state}"),
        time=cetus.get("time_left"),
        new=ts.get(f'{pf}{cetus.get("next")}'),
    )
    embed = discord.Embed(description=output_msg.strip(), color=cetus_color[curr_state])
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, f"cetus-{curr_state}"


# print(w_cetusCycle()[0].description)
# print(checkNewCetusState())
