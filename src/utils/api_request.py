import requests
import json
import datetime as dt

from config.TOKEN import (
    base_url_warframe,
    base_url_market,
    params_warframe,
    DEFAULT_JSON_PATH,
    DEFAULT_MARKET_JSON_PATH,
)
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.logging_utils import save_log


def send_request(
    _req_source: str, _base_url: str, _query: str, _param: dict, _json_path: str
):
    start_time = dt.datetime.now()
    response = None

    # API Request
    try:
        response = requests.get(f"{_base_url}{_query}", params=_param, timeout=60)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] API request failed!"
        obj = f"{elapsed_time}\n{e}"
        print(dt.datetime.now(), C.red, msg, elapsed_time, C.default)
        save_log(type="err", cmd="send_request()", user=MSG_BOT, msg=msg, obj=obj)
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[warn] response code is not 200"
        obj = f"{res_code} / {elapsed_time}"
        print(dt.datetime.now(), C.red, msg, res_code, elapsed_time, C.default)
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    # check response (is not empty or err value)
    if response is None:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] response is Empty!"
        obj = f"{res_code} {elapsed_time}\n{response}"
        print(dt.datetime.now(), C.red, msg, res_code, elapsed_time, C.default)
        save_log(type="api", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    # parse JSON
    try:
        response = response.json()
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] JSON Decode ERROR ({elapsed_time})"
        obj = f"{elapsed_time}\n{e}"
        print(dt.datetime.now(), C.red, msg, elapsed_time, C.default)
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    # save data
    try:
        with open(_json_path, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] Error on saving file!"
        obj = f"{elapsed_time}\n{e}"
        print(dt.datetime.now(), C.red, msg, elapsed_time, C.default)
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    elapsed_time = dt.datetime.now() - start_time
    msg = f"[info] API request successful. {_req_source}"
    # print(C.red, msg, C.default, sep="")
    save_log(
        type="api",
        cmd="API_REQUEST()",
        user=MSG_BOT,
        msg=msg,
        obj=f"{res_code} / ({elapsed_time})",
    )

    return res_code


# usage
def API_Request(
    request_source: str = "Unknown Source",
    base_url=base_url_warframe,
    param=params_warframe,
    json_path=DEFAULT_JSON_PATH,
):
    return send_request(
        _req_source=request_source,
        _base_url=base_url,
        _query="",
        _param=param,
        _json_path=json_path,
    )


def API_Request_Market(
    request_source: str = "Unknown Source",
    query="",
    base_url=base_url_market,
    param=params_warframe,
    json_path=DEFAULT_MARKET_JSON_PATH,
):
    item_name = item_name.replace(" ", "_")
    response = send_request(
        _req_source=request_source,
        _base_url=base_url,
        _query=f"/{query}/{item_name}/orders",
        _param=param,
        _json_path=json_path,
    )
    ingame_orders = []
    for item in response["payload"]["orders"]:
        if item["user"]["status"] != "ingame":
            continue
        ingame_orders.append(item)

    # print(len(ingame_orders))  # , ingame_orders)
    return send_request
