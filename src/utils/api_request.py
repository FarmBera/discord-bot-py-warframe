import requests
import json
import datetime as dt

from config.TOKEN import (
    base_url_warframe,
    base_url_market,
    params_warframe,
    params_market,
    DEFAULT_JSON_PATH,
    DEFAULT_MARKET_JSON_PATH,
)
from src.utils.file_io import json_load
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.logging_utils import save_log


def send_request(res_source: str, query: str = ""):
    start_time = dt.datetime.now()
    response = None

    # setup variables
    if query:  # market api
        base_url = f"{base_url_market}/{query}"
        param = params_market
        JSON_PATH = DEFAULT_MARKET_JSON_PATH
    else:  # warframe api
        base_url = base_url_warframe
        param = params_warframe
        JSON_PATH = DEFAULT_JSON_PATH

    # API Request
    try:
        response = requests.get(base_url, params=param, timeout=60)
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
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        if not query:
            print(dt.datetime.now(), C.red, msg, res_code, elapsed_time, C.default)
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
        with open(JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] Error on saving file!"
        obj = f"{elapsed_time}\n{e}"
        print(dt.datetime.now(), C.red, msg, elapsed_time, C.default)
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    elapsed_time = dt.datetime.now() - start_time
    msg = f"[info] API request successful. {res_source}"
    # print(C.red, msg, C.default, sep="")
    save_log(
        type="api",
        cmd="API-Market" if query else "API_REQUEST()",
        user=MSG_BOT,
        msg=msg,
        obj=f"{res_code} / ({elapsed_time})",
    )

    return res_code


# usage for main api
def API_Request(args: str = "Unknown Source"):
    return send_request(args)


# usage for market api
def API_MarketSearch(req_source: str, query: str, item_name: str):
    item_name = item_name.replace(" ", "_")
    return send_request(req_source, f"{query}/{item_name}/orders")
