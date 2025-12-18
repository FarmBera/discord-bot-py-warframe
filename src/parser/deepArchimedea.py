from src.translator import ts
from src.utils.return_err import err_text

from src.translator import ts
from src.constants.keys import ARCHIMEDEA
from src.utils.times import convert_remain
from src.utils.data_manager import get_obj, getMissionType, getFactions

pf: str = "cmd.deep-archimedea."


def w_deepArchimedea(archimedea) -> str:
    # find deep archimedea
    deep = None
    for item in archimedea:
        if item.get("Type") == "CT_LAB":
            deep = item

    if deep is None or not deep:
        return ts.get("general.error-cmd")

    # generate output msg
    output_msg = ts.get(f"{pf}content").format(
        time=convert_remain(deep["Expiry"]["$date"]["$numberLong"])
    )

    idx = 1
    for item in deep["Missions"]:
        output_msg += f"{idx}. {getMissionType(item['missionType'])}\n"  # ({getFactions(item['faction'])})\n"
        # for jtem in item["difficulties"]:
        #     if jtem.get("type") == "CD_HARD":
        #         output_msg += ", ".join(jtem.get("risks")) + "\n"
        #         break
        idx += 1

    return output_msg


# print(w_deepArchimedea(get_obj(ARCHIMEDEA)))
