import discord
import datetime as dt

from src.translator import ts
from src.utils.return_err import err_embed
from src.utils.times import check_timer_states


class CambionCycleData:
    name = "Cambion Drift Fass/Vome"
    start_date = dt.datetime(2021, 2, 5, 12, 27, 54, tzinfo=dt.timezone.utc)
    looptime = 8998.874  # total 150m
    delaytime = 3000  # Vome 50m
    beforetext = "fass"
    aftertext = "vome"


pf: str = "cmd.cambion."

cambion_color = {"fass": 0xECB448, "vome": 0x97D4D9}


previous_state_cambion = check_timer_states(CambionCycleData)["current"]


def checkNewCambionState() -> bool:
    global previous_state_cambion
    current = check_timer_states(CambionCycleData)["current"]
    if previous_state_cambion != current:
        previous_state_cambion = current
        return True
    return False


def w_cambionCycle() -> tuple[discord.Embed, str]:
    # calculate cambion cycle
    try:
        cambion = check_timer_states(CambionCycleData)
        if not cambion:
            raise ValueError("ERROR FETCHING CAMIBON DATA")
    except Exception:
        return err_embed("cambion cycle"), ""

    status: str = cambion["current"]

    # generate output msg
    output_msg = ts.get(f"{pf}output").format(
        current=ts.get(f"{pf}{status}"),
        time=cambion["time_left"],
        next=ts.get(f'{pf}{cambion["next"]}'),
    )

    embed = discord.Embed(description=output_msg.strip(), color=cambion_color[status])
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, status


# print(w_cambionCycle()[0].description)
# print(checkNewCambionState())
