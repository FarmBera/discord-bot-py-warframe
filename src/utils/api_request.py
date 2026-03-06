import requests

from config.TOKEN import base_url_warframe, base_url_market, WF_JSON_PATH
from config.config import LOG_TYPE
from src.constants.color import C
from src.constants.keys import MSG_BOT
from src.translator import language as lang
from src.utils.file_io import json_save_async
from src.utils.logging_utils import save_log
from src.utils.return_err import return_traceback
from src.utils.times import timeNowDT

params_market: dict = {"Language": lang, "Platform": "pc"}


async def API_internal(pool, url=base_url_warframe):
    start_time = timeNowDT()

    # API Request
    try:
        response = requests.get(url, timeout=60)
    except Exception as e:
        elapsed_time = timeNowDT() - start_time
        msg = f"API request failed!: {elapsed_time}/{e}"
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
        msg = f"response code is not 200: {res_code}/{elapsed_time}"
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
        msg = f"response is Empty!: {res_code}/{elapsed_time}"
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

    return response


# usage for main api
async def API_Request(pool, URL=base_url_warframe, fname=WF_JSON_PATH):
    """API request function for Warframe status

    :param pool: aiomysql cursor pool
    :param URL: request url
    :param fname:
    :return:
        None: failed to request api
        dict: successfully parsed object
    """
    response = await API_internal(pool, URL)
    response = response.json()
    if not response:
        return None

    await json_save_async(response, fname)
    return response


# usage for market api
async def API_MarketSearch(pool, item_name: str):
    """API request function for warframe.market search

    :param pool: db pool object
    :param item_name: item name to search
    :return:
    """
    try:
        response = requests.get(
            url=f"{base_url_market}orders/item/{item_name}",
            headers=params_market,
            timeout=60,
        )
    except Exception as e:
        msg = f"API request failed!: {e}"
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
        msg = f"response is Empty!"
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
