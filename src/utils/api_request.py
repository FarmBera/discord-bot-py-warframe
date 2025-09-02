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
        response = requests.get(base_url, params=params, timeout=15)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] API request failed! ({elapsed_time})"
        print(C.red, msg, C.default, sep="")
        save_log(type="err", cmd="send_request()", user=MSG_BOT, msg=msg, obj=e)
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[warn] response code is not 200 >> {res_code} ({elapsed_time})"
        print(C.red, msg, C.default, sep="")
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=res_code)
        return res_code

    # check response (is not empty or err value)
    if response is None:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] response is Empty! > {res_code} ({elapsed_time})"
        print(C.red, msg, C.default, sep="")
        save_log(type="api", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=response)
        return res_code

    # parse JSON
    try:
        response = response.json()
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time

        msg = f"[err] JSON Decode ERROR"
        print(C.red, msg, C.default, elapsed_time, sep="")
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=e)
        return res_code

    # save data
    try:
        with open(DEFAULT_JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = dt.datetime.now() - start_time
        msg = f"[err] Error on saving file! {elapsed_time}"
        print(C.red, msg, C.default, sep="")
        save_log(type="err", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=e)
        return res_code

    elapsed_time = dt.datetime.now() - start_time
    msg = f"[info] API request successful. ({elapsed_time}) {args}"
    # print(C.red, msg, C.default, sep="")
    save_log(type="api", cmd="API_REQUEST()", user=MSG_BOT, msg=msg, obj=res_code)

    return res_code


# usage
def API_Request(args: str = "API Requested from unknown source"):
    return send_request(args)
