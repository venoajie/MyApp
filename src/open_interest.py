import asyncio

from market_understanding.MP import MpFunctions
import requests
import pandas as pd
import datetime as dt
import numpy as np
from loguru import logger as log
from db_management import sqlite_management

pd.set_option("display.max_rows", None)


async def querying_all(
    table: list, database: str = "databases/trading.sqlite3"
) -> dict:
    """ """
    from utilities import string_modification as str_mod

    query = sqlite_management.querying_open_interest("close", table)

    result = await sqlite_management.executing_query_with_return(
        query, None, None, database
    )
    return result


def transform_result_to_data_frame(data: object):

    df = pd.DataFrame(data)

    return df


database = "databases/trading.sqlite3"
loop = asyncio.get_event_loop()
open_interest = loop.run_until_complete(querying_all("ohlc1_eth_perp_json", database))
# print (open_interest)
df = transform_result_to_data_frame(open_interest)
df.fillna(0)
# df['sum']= df['delta_oi'].rolling(5, min_periods=1).sum()
df["ma_3"] = (df["open_interest"].rolling(window=3).mean()).astype(int, errors="ignore")
df["ma_5"] = (df["open_interest"].rolling(window=5).mean()).astype(int, errors="ignore")
df["ma_10"] = (df["open_interest"].rolling(window=10).mean()).astype(
    int, errors="ignore"
)
df["curent>ma_3"] = df["open_interest"] > df["ma_3"]
df["curent>ma_5"] = df["open_interest"] > df["ma_5"]
df["curent>ma_10"] = df["open_interest"] > df["ma_10"]
# df['pct_chg']= (df['sum']/df['open_interest'].shift(1))*100

if __name__ == "__main__":
    log.warning("START")
    # market_profile= get_market_profile()
    print(df)
    log.warning("DONE")
