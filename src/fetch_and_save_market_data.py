#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
from pathlib import Path

# installed
from rocketry import Rocketry
from rocketry.conds import every
import requests

# user defined formula
from utilities import pickling, system_tools
from market_data import get_market_data
import deribit_get as get_dbt
import asyncio
import aioschedule as schedule
import time

symbol = "ETH-PERPETUAL"
currency = "ETH"
market_data = get_market_data.MarketData(currency, symbol)

app = Rocketry(
    config={"task_execution": "async", "restarting": "relaunch", "cycle_sleep": 1}
)

root = Path(".")


def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)


def get_currencies() -> float:
    """ """

    endpoint = f"https://test.deribit.com/api/v2/public/get_currencies?"
    return requests.get(endpoint).json()["result"]


def get_instruments(currency) -> float:
    """ """

    endpoint = (
        f"https://test.deribit.com/api/v2/public/get_instruments?currency={currency}"
    )
    return requests.get(endpoint).json()["result"]


@app.task(every("3600 seconds"))
def check_and_save_every_60_minutes():
    try:
        currencies = get_currencies()
        currencies = ["ETH", "BTC"]
        for currency in currencies:
            instruments = get_instruments(currency)
            my_path_instruments = system_tools.provide_path_for_file(
                "instruments", currency
            )
            pickling.replace_data(my_path_instruments, instruments)

        my_path_cur = system_tools.provide_path_for_file("currencies")
        pickling.replace_data(my_path_cur, currencies)

    except Exception as error:
        catch_error(error)


# @app.task(every("5 seconds"))
def check_and_save_every_30_seconds():
    try:
        from synchronizing_files import main
        import asyncio

        print("AAAAAAA")
        asyncio.get_event_loop().run_until_complete(main())
        print("c")

    except Exception as error:
        catch_error(error)


@app.task(every("300 seconds"))
def check_and_save_every_5_minutes():
    try:
        # https://towardsdatascience.com/understand-async-await-with-asyncio-for-asynchronous-programming-in-python-e0bc4d25808e
        open_interest_historical = market_data.open_interest_historical()
        my_path = system_tools.provide_path_for_file(
            "openInterestHistorical", currency.lower()
        )
        print (open_interest_historical)
        pickling.replace_data(my_path, open_interest_historical)

        open_interest_symbol = market_data.open_interest_symbol()
        file_name = f"{currency.lower()}-openInterestSymbol.pkl"
        my_path = system_tools.provide_path_for_file(
            "openInterestHistorical", currency.lower()
        )
        pickling.replace_data(my_path, open_interest_symbol)

        open_interest_aggregated_ohlc = market_data.open_interest_aggregated_ohlc()
        my_path = system_tools.provide_path_for_file(
            "openInterestAggregated", currency.lower()
        )
        pickling.replace_data(my_path, open_interest_aggregated_ohlc)

    except Exception as error:
        catch_error(error)


async def job(message='stuff', n=1):
    resolution = "m5"
    connection_url: str = "https://open-api.coinglass.com/public/v2/"

    open_interest_historical = await get_dbt.get_open_interest_aggregated_ohlc(
        connection_url, "eth-perpetual", resolution
    )
    print (open_interest_historical)


if __name__ == "__main__":
    
        
    for i in range(1,3):
        schedule.every(1).seconds.do(job, n=i)
    schedule.every(5).to(10).days.do(job)
    schedule.every().hour.do(job, message='things')
    schedule.every().day.at("16:43").do(job)

    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(schedule.run_pending())
        time.sleep(0.1)
        