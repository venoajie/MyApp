import asyncio

from market_understanding.MP import MpFunctions
import requests
import pandas as pd
import datetime as dt
import numpy as np
from loguru import logger as log
from db_management import sqlite_management


async def querying_all(
    table: list, database: str = "databases/trading.sqlite3"
) -> dict:
    """ """
    from utilities import string_modification as str_mod

    result = await sqlite_management.querying_table(table, database)
    return str_mod.parsing_sqlite_json_output([o["data"] for o in result])


def transform_result_to_data_frame(data: object):

    # log.debug (data)
    df = pd.DataFrame(data)

    # Column name standardization
    df = df.rename(
        columns={
            "tick": "datetime",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "volume",
            "cost": "cost",
        }
    )

    # transform unix date to utc
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

    df = df.loc[:, ["datetime", "Open", "High", "Low", "Close", "volume"]]
    df = df.set_index(df["datetime"], drop=True, inplace=False)

    df["Open"] = df["Open"].round(decimals=2)
    df["High"] = df["High"].round(decimals=2)
    df["Low"] = df["Low"].round(decimals=2)
    df["Close"] = df["Close"].round(decimals=2)
    df["volume"] = df["volume"].round(decimals=2)

    return df


def get_ticksize(data, freq=30):
    # data = dflive30
    numlen = int(len(data) / 2)
    # sample size for calculating ticksize = 50% of most recent data
    tztail = data.tail(numlen).copy()
    tztail["tz"] = tztail.Close.rolling(freq).std()  # std. dev of 30 period rolling
    tztail = tztail.dropna()
    ticksize = np.ceil(
        tztail["tz"].mean() * 0.25
    )  # 1/4 th of mean std. dev is our ticksize

    if ticksize < 0.2:
        ticksize = 0.2  # minimum ticksize limit

    return int(ticksize)


def get_data(url):
    """
    :param url: binance url
    :return: ohlcv dataframe
    """
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df = df.apply(pd.to_numeric)
    df[0] = pd.to_datetime(df[0], unit="ms")
    df = df[[0, 1, 2, 3, 4, 5]]
    df.columns = ["datetime", "Open", "High", "Low", "Close", "volume"]
    df = df.set_index("datetime", inplace=False, drop=False)
    return df


loop = asyncio.get_event_loop()
df = loop.run_until_complete(querying_all("ohlc30_eth_perp_json"))
df = transform_result_to_data_frame(df)

# params
context_days = len(
    [group[1] for group in df.groupby(df.index.date)]
)  # Number of days used for context
freq = 2  # for 1 min bar use 30 min frequency for each TPO, here we fetch default 30 min bars server
avglen = context_days - 2  # num days to calculate average values
mode = "tpo"  # for volume --> 'vol'
trading_hr = 24  # Default for BTC USD or Forex
day_back = (
    0  # -1 While testing sometimes maybe you don't want current days data then use -1
)
# ticksz = 28 # If you want to use manual tick size then uncomment this. Really small number means convoluted alphabets (TPO)
ticksz = (
    get_ticksize(df.copy(), freq=freq)
) * 2  # Algorithm will calculate the optimal tick size based on volatility
textsize = 10

dfnflist = [group[1] for group in df.groupby(df.index.date)]  #

dates = []
for d in range(0, len(dfnflist)):
    dates.append(dfnflist[d].index[0])

date_time_close = dt.datetime.today().strftime("%Y-%m-%d") + " " + "23:59:59"
append_dt = pd.Timestamp(date_time_close)
dates.append(append_dt)

mp = MpFunctions(
    data=df.copy(),
    freq=freq,
    style=mode,
    avglen=avglen,
    ticksize=ticksz,
    session_hr=trading_hr,
)
mplist = mp.get_context()


def get_market_profile():

    distribution_hist = mplist[1]

    df = loop.run_until_complete(
        querying_all("ohlc30_eth_perp_json")
    )  # this line fetches new data for current day
    df = transform_result_to_data_frame(df)
    df_live1 = df.dropna()

    dflive30 = df_live1.resample("30min").agg(
        {
            "datetime": "last",
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "volume": "sum",
        }
    )
    df2 = pd.concat([df, dflive30])
    df2 = df2.drop_duplicates("datetime")

    ticksz_live = get_ticksize(dflive30.copy(), freq=2)
    mplive = MpFunctions(
        data=dflive30.copy(),
        freq=freq,
        style=mode,
        avglen=avglen,
        ticksize=ticksz_live,
        session_hr=trading_hr,
    )

    mplist_live = mplive.get_context()

    df_distribution_live = mplist_live[1]
    df_distribution_concat = pd.concat(
        [distribution_hist, df_distribution_live], axis=0
    )
    df_distribution_concat = df_distribution_concat.reset_index(
        inplace=False, drop=True
    )

    df_updated_rank = mp.get_dayrank()
    ranking = df_updated_rank[0]

    value = [len(dates) - 2, len(dates) - 1]

    for inc in range(value[1] - value[0]):
        i = value[0]

        i += inc

        irank = ranking.iloc[i]  # select single row from ranking df

    return irank.to_dict()


if __name__ == "__main__":
    log.warning("START")
    market_profile = get_market_profile()
    print(market_profile)
    log.warning("DONE")
