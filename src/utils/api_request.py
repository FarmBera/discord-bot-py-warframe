import requests
import json

from src.translator import language as lang
from config.TOKEN import base_url_warframe, base_url_market, WF_JSON_PATH
from config.config import LOG_TYPE
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.utils.times import timeNowDT
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback

params_market: dict = {"Language": lang, "Platform": "pc"}


# usage for main api
async def API_Request(pool, res_source: str = "Unknown Source"):
    """API request function for Warframe status

    Args:
        pool (aiomysql cursor pool)
        res_source (str, optional): code position of the api request. Defaults to "Unknown Source".

    Returns:

        None: failed to request api
    """
    start_time = timeNowDT()
    response = None

    # API Request
    try:
        response = requests.get(base_url_warframe, timeout=60)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time
        msg = f"[err] API request failed!: {elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, C.default)
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_Request()",
            user=MSG_BOT,
            msg=msg,
            obj=return_traceback(),
        )
        return None

    # check response code
    res_code: int = response.status_code
    if res_code != 200:
        elapsed_time = timeNowDT() - start_time

        msg = f"[warn] response code is not 200: {res_code}/{elapsed_time}"
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_Request()",
            user=MSG_BOT,
            msg=msg,
        )
        print(timeNowDT(), C.red, msg, C.default)
        return response

    # check response (is not empty or err value)
    if response is None:
        elapsed_time = timeNowDT() - start_time

        msg = f"[err] response is Empty!: {res_code}/{elapsed_time}"
        print(timeNowDT(), C.red, msg, C.default)
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_Request()",
            user=MSG_BOT,
            msg=msg,
            obj=response,
        )
        return None

    # save data
    try:
        with open(WF_JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(response.json(), json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time
        msg = f"[err] Error on saving file: {elapsed_time}/{e}"
        print(timeNowDT(), C.red, msg, C.default)
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_Request()",
            user=MSG_BOT,
            msg=msg,
            obj=return_traceback(),
        )

    msg = f"{res_code}//{res_source}//{response.elapsed}"
    # print(C.red, msg, C.default, sep="")
    await save_log(
        pool=pool,
        type=LOG_TYPE.api,
        cmd="API_Request()",
        user=MSG_BOT,
        msg=msg,
    )
    return response


# usage for market api
async def API_MarketSearch(pool, item_name: str):
    """API request function for warframe.market search

    Args:
        req_source (str): code position of the api request (for debugging)
        query (str): fixed name
        item_name (str): item name to search

    Returns:
        _type_: _description_
    """
    response: requests.Response = None

    # API Request
    try:
        # orders/item/{slug}
        response = requests.get(
            url=f"{base_url_market}orders/item/{item_name}",
            headers=params_market,
            timeout=60,
        )
    except Exception as e:
        msg = f"[err] API request failed!: {e}"
        print(timeNowDT(), C.red, msg, C.default)
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_MarketSearch()",
            user=MSG_BOT,
            msg=msg,
            obj=return_traceback(),
        )
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
        await save_log(
            pool=pool,
            type=LOG_TYPE.err,
            cmd="API_MarketSearch()",
            user=MSG_BOT,
            msg=msg,
        )
        print(C.red, msg, C.default)
        return response

    msg = f"{response.status_code}//{item_name}//{response.elapsed}"
    await save_log(
        pool=pool,
        type=LOG_TYPE.api,
        cmd="API_MarketSearch()",
        user=MSG_BOT,
        msg=msg,
    )

    return response
