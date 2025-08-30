import requests
import json
import datetime as dt

from config.TOKEN import base_url, params, query
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.logging_utils import save_log


response = None
date_start = None
date_end = None
data = None


# api request func
def send_request():
    date_start = dt.datetime.now()
    response = requests.get(base_url, params=params)
    return dt.datetime.now() - date_start, response


def check_request(est, response):
    # check response value
    if response is None:
        print(f"{C.red}[err] response is Empty!{C.default}")

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        print(
            f"{C.yellow}[warn] response code is not 200 >> {res_code} (est: {est}){C.default}"
        )
        return response, res_code, est

    # process response
    response = response.json()
    fname = f"Warframe_{query}.json"  # file name to save

    # save received data to JSON file
    try:
        with open(fname, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{C.red}[err] Exception on saving file! {e}{C.default}")

    return response, res_code, est


# usage
def API_Request(args: str = ""):
    est, response = send_request()  # real request
    response, code, est = check_request(est, response)  # verify

    # save logs
    if args:
        msg = args
    else:
        msg = "API Requested from unknown source"

    save_log(
        type="api",
        cmd="API_Request()",
        user=MSG_BOT,
        msg=f"{msg} / {est}",
        obj=code,
    )

    if code != 200:
        save_log(
            type="api",
            cmd="API_Request()",
            user=MSG_BOT,
            msg=f"response code error >> {code} / {est}",
            obj=code,
        )

    return code
