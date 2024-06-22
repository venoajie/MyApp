# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
# user defined formula
from db_management.sqlite_management import (
    executing_label_and_size_query,
    querying_hlc_vol,
    executing_query_with_return,
    querying_ohlc_price_vol,
    querying_additional_params,
)

from loguru import logger as log


async def querying_label_and_size(table) -> list:
    """ """

    # execute query
    return await sqlite_management.executing_label_and_size_query(table)


async def get_hlc_vol(window: int = 9, table: str = "ohlc1_eth_perp_json") -> list:
    """ """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_hlc_vol(table, window)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)
    # log.info(ohlc_all)

    return ohlc_all


async def get_price_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_ohlc_price_vol(price, table, window)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)

    return ohlc_all


async def cleaned_up_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    ohlc_all = await get_price_ohlc(price, window, table)

    # pick value only
    ohlc = [o[price] for o in ohlc_all]

    ohlc.reverse()

    return dict(ohlc=ohlc[: window - 1], last_price=ohlc[-1:][0])


async def get_ema(ohlc, ratio: float = 0.9) -> dict:
    """
    https://stackoverflow.com/questions/488670/calculate-exponential-moving-average-in-python
    https://stackoverflow.com/questions/59294024/in-python-what-is-the-faster-way-to-calculate-an-ema-by-reusing-the-previous-ca
    """

    return round(
        sum([ratio * ohlc[-x - 1] * ((1 - ratio) ** x) for x in range(len(ohlc))]), 2
    )


async def get_vwap(ohlc_all, vwap_period) -> dict:
    """
    https://github.com/vishnugovind10/emacrossover/blob/main/emavwap1.0.py
    https://stackoverflow.com/questions/44854512/how-to-calculate-vwap-volume-weighted-average-price-using-groupby-and-apply

    """
    import numpy as np
    import pandas as pd

    df = pd.DataFrame(ohlc_all, columns=["close", "volume"])

    return (
        df["volume"]
        .rolling(window=vwap_period)
        .apply(lambda x: np.dot(x, df["close"]) / x.sum(), raw=False)
    )


async def get_market_condition(
    threshold, limit: int = 100, ratio: float = 0.9, table: str = "ohlc1_eth_perp_json"
) -> dict:
    """ """

    ohlc_high_9 = await cleaned_up_ohlc("high", 9, table)
    ohlc_low_9 = await cleaned_up_ohlc("low", 9, table)

    #    log.error(f'ohlc_high_9 {ohlc_high_9}')
    ema_high_9 = await get_ema(ohlc_high_9["ohlc"], ratio)
    #    log.error(f'ema_high_9 {ema_high_9}')

    ema_low_9 = await get_ema(ohlc_low_9["ohlc"], ratio)

    ohlc_short = await cleaned_up_ohlc("close", 9, table)
    ohlc_long = await cleaned_up_ohlc("close", 20, table)

    ohlc = await cleaned_up_ohlc("close", limit, table)

    vwap_period = 100

    ohlc_all = await get_price_ohlc("close", vwap_period)

    # log.error(f'df {df}')
    df_vwap = await get_vwap(ohlc_all, vwap_period)
    vwap = df_vwap.iloc[-1]

    ema = await get_ema(ohlc["ohlc"], ratio)

    # log.error(ema)
    ema_short = await get_ema(ohlc_short["ohlc"], ratio)

    ema_long = await get_ema(ohlc_long["ohlc"], ratio)

    last_price = ohlc["last_price"]
