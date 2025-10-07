from config.TOKEN import DEFAULT_MARKET_JSON_PATH
from src.utils.api_request import API_MarketSearch
from src.utils.file_io import json_load


THRESHOLD: int = 7


def w_market_search(item_name) -> str:
    # rename input name
    iname: list = []
    for item in item_name.split(" "):
        if item in ["p", "pr", "pri", "prim"]:
            iname.append("prime")
        elif item in ["c", "ch", "cha", "chas", "chass", "chassi"]:
            iname.append("chassis")
        elif item in ["s", "sy", "sys", "syst"]:
            iname.append("systems")
        elif item in ["n", "ne", "neu", "neur", "neuro", "neurop"]:
            iname.append("neuroptics")
        elif item in ["b", "bl", "bp", "blue", "bluep"]:
            iname.append("blueprint")
        else:
            iname.append(item)
    item_name = "_".join(iname)

    # api request
    result = API_MarketSearch(req_source="market", query="items", item_name=item_name)

    # if result not found
    if result != 200:
        return f"No Result Found: **{item_name}**"

    # init categorize
    result = json_load(DEFAULT_MARKET_JSON_PATH)
    ingame_orders = []
    output_msg = ""

    # categorize only 'ingame' stocks (ignores online, offline)
    for item in result["payload"]["orders"]:
        if item["user"]["status"] != "ingame":
            continue
        ingame_orders.append(item)

    ingame_orders = sorted(ingame_orders, key=lambda x: x["platinum"])

    # create output msg
    idx: int = 0
    output_msg = f"### Search Result: {item_name}\n"
    for item in ingame_orders:
        if item["order_type"] != "sell":
            continue

        idx += 1
        if idx > THRESHOLD:
            break

        output_msg += f"- **{item['platinum']} P** : {item['quantity']} qty ({item['user']['ingame_name']})\n"

    return output_msg
