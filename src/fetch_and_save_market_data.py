#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
from pathlib import Path

# installed
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

def check_and_save_every_60_minutes():
    try:
        currencies = get_currencies()
        currencies = ["ETH", "BTC"]
        for currency in currencies:
            print (currency)
            
            instruments = get_instruments(currency)
            
            my_path_instruments = system_tools.provide_path_for_file(
                "instruments", currency
            )
            
            pickling.replace_data(my_path_instruments, instruments)

        my_path_cur = system_tools.provide_path_for_file("currencies")
        pickling.replace_data(my_path_cur, currencies)

    except Exception as error:
        catch_error(error)

async def ohlc():
    connection_url: str = "https://www.deribit.com/api/v2/"
    resolution = 15
    qty_candles = 100
    ohlc = await get_dbt.get_ohlc(
        connection_url, "eth-perpetual", resolution, qty_candles
    )
    print (ohlc)

    return (ohlc)
    
if __name__ == "__main__":
    
    #schedule.every().hour.do(check_and_save_every_60_minutes, message='things')
    schedule.every().day.at("12:07").do(ohlc)
    #schedule.every().day.at("12:02").do(check_and_save_every_60_minutes)

    loop = asyncio.get_event_loop()
    
    while True:
        loop.run_until_complete(schedule.run_pending())
        time.sleep(.91)
        