import requests
import json
import datetime as dt

# from TOKEN import base_url, headers, query
from variables.color import color
from variables.times import JSON_DATE_PAT
from variables.keys import MSG_BOT
from module.save_log import save_log
from module.json_save import json_save

# api link & args
base_api_url = "https://api.warframestat.us/"

"""
pc
items
mods
warframes
weapons
pc/rivens
"""
query = "pc"
base_url = f"{base_api_url}{query}"
headers = {"Accept-Language": "en"}  # en / ko


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
        print(f"{color['red']}ERR: response is NULL{color['default']}")

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        print(f"{color['red']}ERR: Failed API Request >> {res_code}{color['default']}")
        return response

    # process response
    response = response.json()
    fname = f"Warframe_{query}.json"  # file name to save

    # save received data to JSON file
    try:
        with open(fname, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{color['red']}ERR with saving file{color['default']}")

    return response, res_code


# usage
def API_Request(*args):
    if not args:
        save_log(cmd="API_Request()", user=MSG_BOT, msg=f"API Requested")
    else:
        save_log(cmd="API_Request()", user=MSG_BOT, msg=f"API Requested / from {args}")

    est, response = send_request()
    response, code = check_request(est, response)
    return code
