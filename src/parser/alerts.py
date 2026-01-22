import discord

from src.translator import ts
from src.utils.data_manager import getLanguage, getMissionType, getSolNode
from src.utils.emoji import get_emoji
from src.utils.times import convert_remain


def color_decision(t):
    return 0x4DD2FF if t else 0xFFA826


def w_alerts(alerts) -> tuple[discord.Embed, str]:
    """
    parse alert missions

    :param alerts: 'Alerts' object received from warframe api
    :return: parsed discord.Embed & img file name
    """
    if not alerts:  # empty list
        return (
            discord.Embed(
                description=ts.get("cmd.alerts.desc-none"), color=color_decision(alerts)
            ),
            "",
        )

    pf: str = "cmd.alerts."
    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title').format(count=activated_count)}\n"

    idx = 1
    for i in alerts:
        ms = i["MissionInfo"]
        # id = (i["_id"]["$oid"],)
        # activation = int(i["Activation"]["$date"]["$numberLong"])
        # tag = i["Tag"]
        expiry = convert_remain(int(i["Expiry"]["$date"]["$numberLong"]))
        mission_location = getSolNode(ms["location"])
        mission_type = getMissionType(ms["missionType"])
        reward = " + ".join(
            # credit
            [f"{int(ms['missionReward']['credits']):,} {get_emoji('credit')}"]
            # single item
            + [
                f"{getLanguage(item)} {get_emoji(item)}"
                for item in ms["missionReward"].get("items", [])
            ]
            # multiple item
            + [
                f"{getLanguage(item['ItemType'])} {get_emoji(getLanguage(item['ItemType']))} x{item['ItemCount']}"
                for item in ms["missionReward"].get("countedItems", [])
            ]
        )
        try:  # check emeny level
            enemy_lvl = f"{ms['minEnemyLevel']}-{ms['maxEnemyLevel']}"
        except:
            enemy_lvl = ""

        try:  # check max wave
            max_wave = ms["maxWaveNum"]
        except:
            max_wave = ""

        # base output
        output_msg += ts.get(f"{pf}output").format(
            idx=idx,
            reward=reward,
            type=mission_type,
            location=mission_location,
            args=(ts.get(f"{pf}lvl").format(lvl=enemy_lvl) if enemy_lvl else "")
            + (", " if enemy_lvl and max_wave else "")
            + (ts.get(f"{pf}waves").format(wave=max_wave) if max_wave else ""),
            expiry=expiry,
        )
        idx += 1

    embed = discord.Embed(description=output_msg.strip(), color=color_decision(alerts))
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, "alert"


# from src.utils.data_manager import get_obj
# from src.constants.keys import ALERTS
# print(w_alerts(get_obj(ALERTS))[0].description)
