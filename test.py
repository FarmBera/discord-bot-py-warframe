import discord
import datetime as dt

from translator import ts


# TODO: remove
from module.get_obj import get_obj


def W_duviriCycle(duviri, *lang):
    if duviri == False:
        return ts.get("general.error-cmd")

    if duviri is None:
        return None

    output_msg: str = ""
    date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    output_msg += f"# Duviri Cycle\n\n"
    output_msg += f"- State: < {duviri['state'].capitalize()} >\n"

    t = dt.datetime.strptime(duviri["expiry"], date_format) + dt.timedelta(hours=9)
    t -= dt.datetime.now()

    h, r = divmod(t.seconds, 3600)
    m = divmod(r, 60)

    output_msg += "- Expires in "
    if h <= 0:
        output_msg += f"{m[0]}m"
    else:
        output_msg += f"{h}h {m[0]}m"

    return output_msg


# TODO: remove
print("\n", W_duviriCycle(get_obj("duviriCycle")), sep="")
