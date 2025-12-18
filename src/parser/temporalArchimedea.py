from src.translator import ts
from src.utils.times import convert_remain
from src.utils.data_manager import getMissionType, getFactions

pf: str = "cmd.temporal-archimedea."


def w_temporalArchimedia(archimedea) -> str:
    # find temporal archimedea
    temporal = None
    for item in archimedea:
        if item.get("Type") == "CT_HEX":
            temporal = item

    if temporal is None or not temporal:
        return ts.get("general.error-cmd")

    output_msg = ts.get(f"{pf}content").format(
        time=convert_remain(temporal["Expiry"]["$date"]["$numberLong"]),
    )

    idx = 1
    for item in temporal["Missions"]:
        output_msg += f"{idx}. {getMissionType(item['missionType'])} ({getFactions(item['faction'])})\n"
        # for jtem in item["difficulties"]:
        #     if jtem.get("type") == "CD_HARD":
        #         output_msg += ", ".join(jtem.get("risks")) + "\n"
        #         break
        idx += 1

    return output_msg


# from src.constants.keys import ARCHIMEDEA
# from src.utils.data_manager import get_obj

# print(w_temporalArchimedia(get_obj(ARCHIMEDEA)))
