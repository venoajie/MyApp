#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio
import requests

# installed
import aioschedule as schedule
import time
from loguru import logger as log

# user defined formula
from configuration.label_numbering import get_now_unix_time
from db_management.sqlite_management import (
    insert_tables, querying_arithmetic_operator,)
from deribit_get import (
    get_instruments,
    get_currencies, 
    get_server_time)
from market_understanding.technical_analysis import (
    insert_market_condition_result,)
from strategies.config_strategies import (preferred_spot_currencies) 
from utilities.pickling import replace_data
from utilities.string_modification import (
    remove_redundant_elements, 
    transform_nested_dict_to_list,
    parsing_label,)
from utilities.system_tools import (
    catch_error_message, 
    provide_path_for_file,)
from websocket_management.allocating_ohlc import (
    ohlc_end_point, 
    last_tick_fr_sqlite,)

def catch_error(error, idle: int = None) -> list:
    """ """
    catch_error_message(error, idle)


async def get_instruments_from_deribit(connection_url, currency) -> float:
    """ """

    result = await get_instruments(connection_url, currency)

    return result


async def future_spreads(currency) -> float:
    """ """
    from strategies.futures_spread import get_futures_combo_instruments

    result = await get_futures_combo_instruments (currency)

    return result

async def get_currencies_from_deribit(connection_url) -> float:
    """ """

    result = await get_currencies(connection_url)

    print(f"get_currencies {connection_url} {result}")

    return result


async def back_up_db():
    import sqlite3

    src = sqlite3.connect("databases/trading.sqlite3")
    dst = sqlite3.connect("databases/trdg.bak")
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

async def current_server_time() -> float:
    """ """
    current_time = await get_server_time()
    return current_time["result"]


def get_label_transaction_net(my_trades_open_remove_closed_labels: list) -> float:
    """ """
    return (
        []
        if my_trades_open_remove_closed_labels == []
        else remove_redundant_elements(
            [
                parsing_label(o["label"])["transaction_net"]
                for o in my_trades_open_remove_closed_labels
            ]
        )
    )
    
async def run_every_5_seconds() -> None:
    """ """
    pass


async def run_every_60_seconds() -> None:
    """ """

    from websocket_management.cleaning_up_transactions import count_and_delete_ohlc_rows

    await count_and_delete_ohlc_rows()
    #await back_up_db()


async def run_every_15_seconds() -> None:
    """ """

    ONE_PCT = 1 / 100
    WINDOW = 9
    RATIO = 0.9
    THRESHOLD = 0.01 * ONE_PCT
    
    currencies=  preferred_spot_currencies()
    
    end_timestamp=     get_now_unix_time()  
    
    for currency in currencies:
        
        instrument_name= f"{currency}-PERPETUAL"

        await insert_market_condition_result(instrument_name, WINDOW, RATIO)
        
        time_frame= [3,5,15,60,30,"1D"]
            
        ONE_SECOND = 1000
        
        one_minute = ONE_SECOND * 60
        
        WHERE_FILTER_TICK: str = "tick"
        
        for resolution in time_frame:
            
            table_ohlc= f"ohlc{resolution}_{currency.lower()}_perp_json" 
            
            log.debug (f"table_ohlc {table_ohlc}")         
            
            last_tick_query_ohlc1: str = querying_arithmetic_operator (WHERE_FILTER_TICK, "MAX", table_ohlc)

            log.error (f"last_tick_query_ohlc1 {last_tick_query_ohlc1}")         
            
            start_timestamp: int = await last_tick_fr_sqlite (last_tick_query_ohlc1)

            log.error (f"start_timestamp {start_timestamp}")         
            
            if resolution == "1D":
                delta= (end_timestamp - start_timestamp)/(one_minute * 60 * 24)
        
            else:
                delta= (end_timestamp - start_timestamp)/(one_minute * resolution)
            
            #log.error (f"delta {delta}")         
            
            if delta > 1:
                end_point= ohlc_end_point(instrument_name,
                                resolution,
                                start_timestamp,
                                end_timestamp,
                                )

                ohlc_request = requests.get(end_point).json()["result"]
                
                result = [o for o in transform_nested_dict_to_list(ohlc_request) if o["tick"]> start_timestamp][0]
                
                log.info (f"result {result}")
                
                await insert_tables(table_ohlc, result)
        

async def check_and_save_every_60_minutes():
    connection_url: str = "https://www.deribit.com/api/v2/"

    try:

        get_currencies_all = await get_currencies_from_deribit(connection_url)
        currencies = [o["currency"] for o in get_currencies_all["result"]]
        #        print(currencies)

        for currency in currencies:

            instruments = await get_instruments_from_deribit(connection_url, currency)
            # print (f'instruments {instruments}')

            my_path_instruments = provide_path_for_file("instruments", currency)

            replace_data(my_path_instruments, instruments)

        my_path_cur = provide_path_for_file("currencies")

        replace_data(my_path_cur, currencies)
        # catch_error('update currencies and instruments')

    except Exception as error:
        catch_error(error)


if __name__ == "__main__":

    try:
        # asyncio.get_event_loop().run_until_complete(check_and_save_every_60_minutes())
        schedule.every().hour.do(check_and_save_every_60_minutes)

        schedule.every().hour.do(back_up_db)
        schedule.every(15).seconds.do(run_every_15_seconds)
        #schedule.every(3).seconds.do(run_every_3_seconds)
        #schedule.every(5).seconds.do(run_every_5_seconds)
        schedule.every(60).seconds.do(run_every_60_seconds)

        schedule.every().day.at("08:01").do(check_and_save_every_60_minutes)
        schedule.every().day.at("08:05").do(check_and_save_every_60_minutes)

        loop = asyncio.get_event_loop()

        while True:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(0.91)

    except Exception as error:
        print(error)
        catch_error(error, 30)
