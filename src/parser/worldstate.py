import discord

from src.parser.cambionCycle import CambionCycleData
from src.parser.cetusCycle import CetusTimerData
from src.parser.duviriCycle import get_current_mood
from src.parser.vallisCycle import VallisCycleData
from src.translator import ts
from src.utils.emoji import worldstate_emoji
from src.utils.return_err import err_embed
from src.utils.times import check_timer_states, convert_remain

pattern = "\n"
pf: str = "cmd.worldstate."


def w_worldstate() -> tuple[discord.Embed, str]:
    # calculate vallis cycle
    try:
        cetus = check_timer_states(CetusTimerData)
        duviri = get_current_mood()
        cambion = check_timer_states(CambionCycleData)
        vallis = check_timer_states(VallisCycleData)
        if not cetus or not duviri or not cambion or not vallis:
            raise ValueError("ERROR FETCHING DATA")
    except Exception:
        return err_embed("WorldState"), ""

    title: str = ts.get(f"{pf}title")

    worlds = ts.get(f"{pf}world_names")
    states = [
        f"{worldstate_emoji[cetus['current']]} {ts.get(f'cmd.cetus.{cetus['current']}')}",
        f"{worldstate_emoji[duviri["mood"]]} {ts.get(f'cmd.duviri-cycle.{duviri["mood"]}')}",
        f"{worldstate_emoji[cambion["current"]]} {ts.get(f'cmd.cambion.{cambion["current"]}')}",
        f"{worldstate_emoji[vallis["current"]]} {ts.get(f'cmd.vallis.{vallis["current"]}')}",
    ]
    expiry = [
        cetus["time_left"],
        convert_remain(duviri["timestamp"]),
        cambion["time_left"],
        vallis["time_left"],
    ]

    embed = discord.Embed(description=title, color=discord.Color.darker_grey())
    embed.add_field(name=ts.get(f"{pf}world"), value=pattern.join(worlds), inline=True)
    embed.add_field(name=ts.get(f"{pf}state"), value=pattern.join(states), inline=True)
    embed.add_field(name=ts.get(f"{pf}expiry"), value=pattern.join(expiry), inline=True)
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "worldstate"


# print(w_worldstate()[0].fields)
