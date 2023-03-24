#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp

# user defined formula
from utilities import pickling, system_tools
import deribit_get as get_dbt

symbol = "ETH-PERPETUAL"
currency = "ETH"

def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)

async def get_instruments(connection_url, currency) -> float:
    """ """

    result= await get_dbt.get_instruments (connection_url, currency)
    
    return result

async def get_currencies(connection_url) -> float:
    """ """

    result= await get_dbt.get_currencies (connection_url)

    return result

async def get_open_interest_history() -> float:
    """ """

    result= await get_dbt.get_open_interest_historical ()

    return result

async def check_and_save_every_60_minutes():
    open_interest_history = await get_open_interest_history()
    print (open_interest_history)
    
    connection_url: str = "https://www.deribit.com/api/v2/"
    
    try:
        
        currencies = ["ETH", "BTC"]
        
        for currency in currencies:
            
            instruments = await get_instruments(connection_url, currency)
            
            my_path_instruments = system_tools.provide_path_for_file(
                "instruments", currency
            )
            
            pickling.replace_data(my_path_instruments, instruments)

        my_path_cur = system_tools.provide_path_for_file("currencies")
        
        pickling.replace_data(my_path_cur, currencies)
        catch_error('update currencies and instruments')

    except Exception as error:
        catch_error(error)
        
        
async def main() -> None:
    headers = {
    "accept": "application/json",
    "coinglassSecret": "877ad9af931048aab7e468bda134942e",
}
    session = aiohttp.ClientSession()
    time_frame = 'm5'
    symbol = 'BTC'
    currency = 'USD'
    url = f"https://open-api.coinglass.com/public/v2/?symbol={symbol}&time_type=all&currency={currency}"

    async with session.get(url, headers=headers) as resp:
        print(await resp.text())
        
if __name__ == "__main__":
    asyncio.run(main())
    
    connection_url: str = "https://www.deribit.com/api/v2/"
    
    schedule.every().hour.do(check_and_save_every_60_minutes)
    
    schedule.every().day.at("08.01").do(check_and_save_every_60_minutes)
    schedule.every().day.at("08.05").do(check_and_save_every_60_minutes)

    loop = asyncio.get_event_loop()
    
    while True:
        loop.run_until_complete(schedule.run_pending())
        time.sleep(.91)
        