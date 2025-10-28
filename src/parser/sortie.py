from src.translator import ts
from src.constants.times import convert_remain
from src.utils.data_manager import getMissionType, getSolNode, getSortieMod


def w_sortie(sortie):
    if not sortie:
        return ts.get("general.error-cmd")

    sortie = sortie[0]
    prefix: str = "cmd.sortie"

    # id = dd["_id"]["$oid"]
    # activation = int(dd["Activation"]["$date"]["$numberLong"])
    expiry = int(sortie["Expiry"]["$date"]["$numberLong"])

    # title
    output_msg: str = f"# {ts.get(f'{prefix}.title')}\n\n"
    # expiry
    output_msg += f"- {ts.get(f'{prefix}.eta')}: {convert_remain(expiry)}\n\n"

    # mission list
    idx = 1
    for i in sortie["Variants"]:
        miss_type = getMissionType(i["missionType"])
        node = getSolNode(i["node"])
        mod_type = getSortieMod(i["modifierType"])

        output_msg += f"{idx}. **{miss_type}** "
        output_msg += f"at {node} - *{mod_type}*\n"
        idx += 1

    return output_msg
