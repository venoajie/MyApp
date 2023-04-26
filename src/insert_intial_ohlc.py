#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from datetime import datetime, timedelta
import json

# installed
import asyncio
from loguru import logger as log

# user defined formula
from utilities import system_tools, string_modification
from db_management import sqlite_management

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)


async def insert_ohlc(instrument_name: str='ETH-PERPETUAL', resolution: int =1, qty_candles: int =6000) -> None:

    from utilities import time_modification
    import requests

    now_utc = datetime.now()
    now_unix = time_modification.convert_time_to_unix (now_utc)
    start_timestamp = now_unix - 60000 * qty_candles
    
    ohlc_endPoint=  (f' https://deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp={now_unix}&instrument_name={instrument_name}&resolution={resolution}&start_timestamp={start_timestamp}')
    
    try:            

        log.warning (ohlc_endPoint)
        #log.warning (requests.get(ohlc_endPoint).json())
        ohlc_request= requests.get(ohlc_endPoint).json()['result']
        result= string_modification.transform_nested_dict_to_list(ohlc_request)
        #log.warning (result)
        
        for data in result:
            if resolution==1:
                await sqlite_management.insert_tables('ohlc1_eth_perp_json',data)

            if resolution==30:
                await sqlite_management.insert_tables('ohlc30_eth_perp_json',data)

    except Exception as error:
        system_tools.catch_error_message(error, 10,"WebSocket connection - failed to get ohlc",)
    

async def main():
    try:
        resolutions= [1,30]
        instrument_name= 'ETH-PERPETUAL'
        qty_candles= 6000
        for res in resolutions:
            await insert_ohlc(instrument_name, res, qty_candles )

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save MARKET data from deribit"
        )

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())

    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save MARKET data from deribit"
        )
