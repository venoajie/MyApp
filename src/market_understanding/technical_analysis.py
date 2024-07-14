# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from db_management.sqlite_management import (
    executing_label_and_size_query,
    querying_hlc_vol,
    executing_query_with_return,
    querying_table,
    querying_ohlc_price_vol,
    insert_tables,
)
from utilities.system_tools import (
    raise_error_message,
)

# from loguru import logger as log


async def querying_label_and_size(table) -> list:
    """ """

    # execute query
    return await executing_label_and_size_query(table)


async def get_hlc_vol(window: int = 9, table: str = "ohlc1_eth_perp_json") -> list:
    """ """

    # get query for close price
    get_ohlc_query = querying_hlc_vol(table, window)

    # executing query above
    ohlc_all = await executing_query_with_return(get_ohlc_query)
    # log.info(ohlc_all)

    return ohlc_all


async def get_price_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    get_ohlc_query = querying_ohlc_price_vol(price, table, window)

    # executing query above
    ohlc_all = await executing_query_with_return(get_ohlc_query)

    return ohlc_all


async def cleaned_up_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    ohlc_all = await get_price_ohlc(price, window, table)
    #print (f"ohlc_60 ohlc_all {ohlc_all}")

    # pick value only
    ohlc = [o[price] for o in ohlc_all]
    tick = [o["tick"] for o in ohlc_all]

    ohlc.reverse()
    tick.reverse()
    print (f"ohlc_60 reverse {ohlc}")

    return dict(
        tick=max(tick[: window - 1]), ohlc=ohlc[: window - 1], last_price=ohlc[-1:][0]
    )


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


async def last_tick_fr_sqlite(last_tick_query_ohlc1) -> int:
    """ """
    try:
        last_tick1_fr_sqlite = await executing_query_with_return(last_tick_query_ohlc1)

    except Exception as error:
        await raise_error_message(
            error,
            "Capture market data - failed to fetch last_tick_fr_sqlite",
        )

    if "market_analytics_json" in last_tick_query_ohlc1:
        return last_tick1_fr_sqlite
    return last_tick1_fr_sqlite[0]["MAX (tick)"]


def get_last_tick_from_prev_TA(TA_result_data) -> int:
    """ """
    return (
        0 if TA_result_data == [] else max([o["tick"] for o in TA_result_data])
    )

async def get_market_condition(
    threshold, limit: int = 100, ratio: float = 0.9, table: str = "ohlc1_eth_perp_json"
) -> dict:
    """ """
    table_60= "ohlc60_eth_perp_json"
    ohlc_60= await cleaned_up_ohlc("close", 2, table_60)
    #print (f"ohlc_60 {ohlc_60}")

    result = {}
    ohlc_high_9 = await cleaned_up_ohlc("high", 9, table)
    current_tick = ohlc_high_9["tick"]

    TA_result = await querying_table("market_analytics_json")
    TA_result_data = TA_result["list_data_only"]
    # log.error(f'TA_result {TA_result_data}')
    last_tick_from_prev_TA = get_last_tick_from_prev_TA(TA_result_data)
    # log.error(f'last_tick {last_tick_from_prev_TA}')

    if last_tick_from_prev_TA == 0 or current_tick > last_tick_from_prev_TA:

        ohlc_low_9 = await cleaned_up_ohlc("low", 9, table)

        #    log.error(f'ohlc_high_9 {ohlc_high_9}')
        ema_high_9 = await get_ema(ohlc_high_9["ohlc"], ratio)
        #    log.error(f'ema_high_9 {ema_high_9}')
        result.update({"tick": current_tick})
        ema_low_9 = await get_ema(ohlc_low_9["ohlc"], ratio)

        ohlc_close_9 = await cleaned_up_ohlc("close", 9, table)
        ohlc_close_20 = await cleaned_up_ohlc("close", 20, table)

        # log.error(ema)
        ema_close_9 = await get_ema(ohlc_close_9["ohlc"], ratio)
        ema_close_20 = await get_ema(ohlc_close_20["ohlc"], ratio)

        result.update({"1m_ema_close_20": ema_close_20})
        result.update({"1m_ema_close_9": ema_close_9})
        result.update({"1m_ema_high_9": ema_high_9})
        result.update({"1m_ema_low_9": ema_low_9})

        result.update({"60_open": ohlc_60["ohlc"][0]})
        result.update({"60_last_price": ohlc_60["last_price"]})

        vwap_period = 100

        ohlc_all = await get_price_ohlc("close", vwap_period)

        # log.error(f'df {df}')
        df_vwap = await get_vwap(ohlc_all, vwap_period)
        vwap = df_vwap.iloc[-1]
        result.update({"1m_vwap": vwap})
        #print(f"TA {result}")

        await insert_tables("market_analytics_json", result)
