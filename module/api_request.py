import requests
import json
import datetime as dt

from TOKEN import base_url, headers, query
from variables.color import color
from variables.keys import MSG_BOT
from module.save_log import save_log


response = None
date_start = None
date_end = None
data = None


# api request func
def send_request():
    date_start = dt.datetime.now()
    response = requests.get(base_url, headers=headers)
    return dt.datetime.now() - date_start, response


def check_request(est, response):
    # check response value
    if response is None:
        print(f"{color['red']}[ERR] response is NULL{color['default']}")

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        print(
            f"{color['yellow']}[warn] response code is not 200 >> {res_code} (est: {est}){color['default']}"
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
        print(f"{color['red']}ERR with saving file{color['default']}")

    return response, res_code, est


# usage
def API_Request(*args):
    est, response = send_request()  # real request
    response, code, est = check_request(est, response)  # verify

    # save logs
    if args is not None:
        msg = (f"API Requested / from {args}",)
    else:
        msg = "API Requested"

    save_log(
        type="api",
        cmd="API_Request()",
        user=MSG_BOT,
        msg=msg,
        obj=est,
    )

    if code != 200:
        save_log(
            type="api",
            cmd="API_Request()",
            user=MSG_BOT,
            msg=f"{color['yellow']}response code error >> {code}",
            obj=est,
        )

    return code
