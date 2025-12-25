import requests
import json
import datetime as dt

from src.translator import language as lang
from config.TOKEN import base_url_warframe, base_url_market, WF_JSON_PATH
from src.utils.times import KST, timeNowDT
from src.constants.color import C


# usage for main api
def API_Request() -> requests.Response | None:
    """Legacy API request function for `init` script

    Returns:
        requests.Response: API Response object
        None: failed to request API
    """

    start_time = dt.datetime.now(tz=KST)
    response: requests.Response = None

    # API Request
    try:
        response = requests.get(base_url_warframe, timeout=60)
    except Exception as e:
        elapsed_time = dt.datetime.now(tz=KST) - start_time
        msg = f"[err] API request failed! ({elapsed_time})\n{e}"
        print(dt.datetime.now(tz=KST), C.red, msg, C.default)
        return None

    # check response (is not empty or err value)
    if not response:
        elapsed_time = dt.datetime.now(tz=KST) - start_time
        msg = f"[err] response is Empty! > ({res_code}/{elapsed_time})\n{response}"
        print(dt.datetime.now(tz=KST), C.red, msg, res_code, elapsed_time, C.default)
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        elapsed_time = dt.datetime.now(tz=KST) - start_time
        msg = f"[warn] response code is not 200 > {res_code} / {response.elapsed} ({elapsed_time})"
        print(dt.datetime.now(tz=KST), C.red, msg, res_code, elapsed_time, C.default)
        return None

    try:
        with open(WF_JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response.json(), json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time
        msg = f"[err] Error on saving file!"
        # obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, elapsed_time, C.default)

    return response


def API_MarketSearch(item_name: str):
    response: requests.Response = None

    try:
        response = requests.get(
            url=f"{base_url_market}orders/item/{item_name}",
            headers={"Language": lang, "Platform": "pc"},
            timeout=60,
        )
    except Exception as e:
        msg = f"[err] API request failed! (from API_MarketSearch)"
        print(timeNowDT(), C.yellow, msg, C.red, e, C.default)
        return None

    # check response code
    # res_code: int = response.status_code
    # if res_code != 200:
    #     msg = f"[warn] response code is not 200 (from API_MarketSearch)"
    #     print(C.red, res_code, msg, C.default)
    #     return response

    # check response (is not empty)
    if response is None:
        msg = f"[err] response is Empty!"
        print(C.red, msg, C.default)
        return response

    try:
        with open("market-search-result.json", "w", encoding="utf-8") as json_file:
            json.dump(response.json(), json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        msg = f"[err] Error on saving file!"
        # obj = f"{elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, C.default)

    return response


# API_MarketSearch("gauss_prime_set")
