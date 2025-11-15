import discord
from src.translator import ts
from src.utils.times import convert_remain
from src.utils.return_err import err_embed
from src.utils.data_manager import getLanguage, getMissionType, getSolNode
from src.utils.emoji import get_emoji


def color_decision(t):
    return 0x4DD2FF if t else 0xFFA826


def w_alerts(alerts):
    if alerts == []:  # empty list
        return discord.Embed(
            description=ts.get("cmd.alerts.desc-none"), color=color_decision(alerts)
        )

    if not alerts:
        return err_embed("alert obj error")

    pf: str = "cmd.alerts."
    activated_count = len(alerts)
    output_msg = f"# {ts.get('cmd.alerts.title').format(count=activated_count)}\n\n"

    idx = 1
    for i in alerts:
        ms = i["MissionInfo"]
        # id = (i["_id"]["$oid"],)
        # activation = int(i["Activation"]["$date"]["$numberLong"])
        # tag = i["Tag"]
        expiry = convert_remain(int(i["Expiry"]["$date"]["$numberLong"]))
        mission_location = getSolNode(ms["location"])
        mission_type = getMissionType(ms["missionType"])
        # [f"{int(ms['missionReward']['credits']):,} {ts.get('cmd.alerts.credit')}"]
        reward = " + ".join(
            # credit
            [f"{int(ms['missionReward']['credits']):,} {get_emoji('credit')}"]
            # single item
            + [getLanguage(item) for item in ms["missionReward"].get("items", [])]
            # multiple item
            + [
                f"{getLanguage(item['ItemType'])} {get_emoji(getLanguage(item['ItemType']))} x{item['ItemCount']}"
                for item in ms["missionReward"].get("countedItems", [])
            ]
        )

        enemy_lvl = f"{ms['minEnemyLevel']}-{ms['maxEnemyLevel']}"
        max_wave = ms["maxWaveNum"]

        output_msg += f"### {idx}. {reward}\n\n"
        output_msg += f"- **{mission_type}** - {mission_location}\n"
        output_msg += f"- {ts.get(f'{pf}lvl').format(lvl=enemy_lvl)} / {ts.get(f'{pf}waves').format(wave=max_wave)}\n"
        output_msg += f"- {ts.get(f'{pf}exp').format(time=expiry)}\n\n"
        idx += 1

    f = "alerts"
    return discord.Embed(description=output_msg, color=color_decision(alerts)), f
