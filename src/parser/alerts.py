import discord
from src.translator import ts
from src.constants.times import convert_remain
from src.utils.return_err import err_embed
from src.utils.data_manager import getLanguage, getMissionType, getSolNode


def color_decision(t):
    return 0x4DD2FF if t else 0xFFA826


def w_alerts(alerts) -> discord.Embed:
    if alerts == []:  # empty list
        return discord.Embed(
            description=ts.get("cmd.alerts.desc-none"), color=color_decision(alerts)
        )

    if not alerts:
        return err_embed("alert obj error")

    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title')}: {activated_count}\n\n"

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
            [f"{int(ms['missionReward']['credits']):,} {ts.get('cmd.alerts.credit')}"]
            + [getLanguage(item) for item in ms["missionReward"].get("items", [])]
        )

        enemy_lvl = f"{ms['minEnemyLevel']}-{ms['maxEnemyLevel']}"
        max_wave = ms["maxWaveNum"]

        output_msg += f"{idx}. {reward}\n"
        output_msg += f"- **{ts.trs(mission_type)}** at {mission_location}\n"
        output_msg += f"- lvl: {enemy_lvl} / Max Wave : {max_wave}\n"
        output_msg += f"- Expires in {expiry}\n\n"
        idx += 1

    return discord.Embed(description=output_msg, color=color_decision(alerts))
