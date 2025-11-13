import discord

from config.config import Lang
from src.translator import ts, language as lang
from src.utils.return_err import err_embed
from src.utils.data_manager import getLanguage
from src.utils.times import convert_remain


def color_decision(t):
    return 0x4DD2FF if t else 0xFFA826


def w_events(events) -> discord.Embed:
    if events == []:  # empty list
        return discord.Embed(
            description=ts.get("cmd.events.desc-none"), color=color_decision(events)
        )

    elif not events:
        return err_embed("events obj error")

    pf: str = "cmd.events."

    output_msg: str = "# 이벤트\n"

    for e in events:
        # title
        output_msg += f"## {getLanguage(e['Desc'])}\n"
        # desc
        # output_msg += f"- {getLanguage(e['ToolTip'])}\n"
        # expiry
        output_msg += f"- 종료까지 {convert_remain(e['Expiry']['$date']['$numberLong'])} 남았습니다!\n\n"
        # rewards
        if e.get("InterimGoals") and e.get("InterimRewards"):
            for i in range(4):
                output_msg += f"- {e['InterimGoals'][i]}% : {
                        ", ".join([getLanguage(item) for item in e['InterimRewards'][i]['items'] ])}\n"
        # final rewards
        if e.get("Reward"):
            output_msg += f"""- 100% : {", ".join([getLanguage(item) for item in e['Reward']['items']])}

"""

    embed = discord.Embed(
        description=output_msg,
        color=0x00FFFF,
    )
    # set embed thumb
    img_url = None
    if img_url:
        embed.set_image(url=img_url)

    return embed
