import discord
import datetime as dt

from src.translator import ts
from src.utils.return_err import err_embed, return_traceback
from src.utils.times import check_timer_states


class VallisCycleData:
    name = "Orb Vallis Warm/Cold"
    start_date = dt.datetime(2021, 1, 9, 8, 13, 48, tzinfo=dt.timezone.utc)
    looptime = 1600  # total 26m
    delaytime = 1200  # cold 20m
    beforetext = "warm"
    aftertext = "cold"


vallis_color = {"warm": 0xFF9012, "cold": 0x00BFFF}


pf: str = "cmd.vallis."


def w_vallisCycle(tmp) -> tuple[discord.Embed, str]:
    # calculate vallis cycle
    try:
        vallis = check_timer_states(VallisCycleData)
        if not vallis:
            raise ValueError("ERROR FETCHING CAMIBON DATA")
    except Exception:
        print(return_traceback())
        return err_embed("vallis cycle"), ""

    status: str = vallis["current"]

    # generate output msg
    output_msg = ts.get(f"{pf}output").format(
        current=ts.get(f"{pf}{status}"),
        time=vallis["time_left"],
        next=ts.get(f'{pf}{vallis["next"]}'),
    )

    embed = discord.Embed(description=output_msg, color=vallis_color[status])
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, status


# print(w_vallisCycle()[0].description)
