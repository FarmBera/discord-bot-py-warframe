import requests
import json
import datetime as dt

from config.TOKEN import base_url, params, DEFAULT_JSON_PATH
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.logging_utils import save_log


def send_request(args):
    start_time = dt.datetime.now()
    response = None

    # API Request
    try:
        response = requests.get(base_url, params=params, timeout=60)
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
        with open(DEFAULT_JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] Error on saving file!"
        obj = f"{elapsed_time}\n{e}"
        print(dt.datetime.now(), C.red, msg, elapsed_time, C.default)
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=obj)
        return res_code

    elapsed_time = dt.datetime.now() - start_time
    msg = f"[info] API request successful. {args}"
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
def API_Request(args: str = "Unknown Source"):
    return send_request(args)
