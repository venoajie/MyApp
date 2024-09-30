#!/usr/bin/python3
# -*- coding: utf-8 -*-


# built ins
import asyncio

import json
from loguru import logger as log
import requests

from db_management.sqlite_management import (
    executing_query_with_return,
    insert_tables,update_status_data,
    querying_arithmetic_operator,)
from utilities.string_modification import (
    transform_nested_dict_to_list,)
from utilities.system_tools import raise_error_message

def ohlc_end_point(instrument_ticker: str,
                   resolution: int,
                   start_timestamp: int,
                   end_timestamp: int,):
    
    url=f"https://deribit.com/api/v2/public/get_tradingview_chart_data?"
    
    return  f"{url}end_timestamp={end_timestamp}&instrument_name={instrument_ticker}&resolution={resolution}&start_timestamp={start_timestamp}"

async def recording_multiple_time_frames(instrument_ticker: str,
                                         table_ohlc: str,
                                         resolution: int,
                                         start_timestamp: int, 
                                         end_timestamp: int, 
                                         ) -> float:
    """ """
    ONE_SECOND = 1000
    one_minute = ONE_SECOND * 60
    
    try:
        delta= (end_timestamp - start_timestamp)/(one_minute * resolution)
        
        if delta > 1:
            end_point= ohlc_end_point(instrument_ticker,
                              resolution,
                              start_timestamp,
                              end_timestamp,
                              )

            ohlc_request = requests.get(end_point).json()["result"]
            result = [o for o in transform_nested_dict_to_list(ohlc_request) if o["tick"]> start_timestamp][0]
            
            await insert_tables(table_ohlc, result)
        
    

    except Exception as error:
        await raise_error_message(
            error,
            "Capture market data - failed to fetch last open_interest",
        )
    


async def last_open_interest_tick_fr_sqlite(last_tick_query_ohlc1) -> float:
    """ """
    try:
        last_open_interest = await executing_query_with_return(last_tick_query_ohlc1)

    except Exception as error:
        await raise_error_message(
            error,
            "Capture market data - failed to fetch last open_interest",
        )
    return 0 if last_open_interest == 0 else last_open_interest[0]["open_interest"]


async def last_tick_fr_sqlite(last_tick_query_ohlc1) -> int:
    """ """
    try:
        last_tick1_fr_sqlite = await executing_query_with_return(last_tick_query_ohlc1)

    except Exception as error:
        await raise_error_message(
            error,
            "Capture market data - failed to fetch last_tick_fr_sqlite",
        )
    return last_tick1_fr_sqlite[0]["MAX (tick)"]

async def replace_previous_ohlc_using_fix_data(instrument_ticker,
                                               TABLE_OHLC1, 
                                               resolution,
                                               last_tick1_fr_sqlite, 
                                               last_tick_fr_data_orders, 
                                               WHERE_FILTER_TICK) -> int:
    """ """
    try:

        ohlc_endPoint = ohlc_end_point(instrument_ticker, 
                                       resolution, 
                                       last_tick1_fr_sqlite, 
                                       last_tick_fr_data_orders,)

        f" https://deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp={last_tick_fr_data_orders}&instrument_name={instrument_ticker}&resolution=1&start_timestamp={last_tick1_fr_sqlite}"

        ohlc_request = requests.get(ohlc_endPoint).json()["result"]
        result = [o for o in transform_nested_dict_to_list(ohlc_request) if o["tick"]== last_tick1_fr_sqlite][0]
        
        await update_status_data(TABLE_OHLC1, "data", last_tick1_fr_sqlite, WHERE_FILTER_TICK, result, "is")
        
    except Exception as error:
        await raise_error_message(
            error,
            "Capture market data - failed to fetch last_tick_fr_sqlite",
        )

async def ohlc_result_per_time_frame(
    instrument_ticker,
    resolution,
    data_orders,
    TABLE_OHLC1: str,
    WHERE_FILTER_TICK: str = "tick",
) -> None:

    last_tick_query_ohlc1: str = querying_arithmetic_operator (WHERE_FILTER_TICK, "MAX", TABLE_OHLC1)

    last_tick1_fr_sqlite: int = await last_tick_fr_sqlite (last_tick_query_ohlc1)

    last_tick_fr_data_orders: int = data_orders ["tick"]

    # refilling current ohlc table with updated data
    refilling_current_ohlc_table_with_updated_streaming_data = last_tick1_fr_sqlite == last_tick_fr_data_orders
    
    insert_new_ohlc_and_replace_previous_ohlc_using_fix_data = last_tick_fr_data_orders > last_tick1_fr_sqlite
    
    if refilling_current_ohlc_table_with_updated_streaming_data:
    
        await update_status_data(TABLE_OHLC1, "data", last_tick1_fr_sqlite, WHERE_FILTER_TICK, data_orders, "is")
    
    if insert_new_ohlc_and_replace_previous_ohlc_using_fix_data:
        
        await insert_tables(TABLE_OHLC1, data_orders)
        
        await replace_previous_ohlc_using_fix_data (instrument_ticker,
                                                    TABLE_OHLC1, 
                                                    resolution,
                                                    last_tick1_fr_sqlite, 
                                                    last_tick_fr_data_orders,
                                                    WHERE_FILTER_TICK)
                                                        
def currency_inline_with_database_address (currency: str, database_address: str) -> bool:
    return currency.lower()  in str(database_address)


async def inserting_open_interest(currency, 
                                  WHERE_FILTER_TICK,
                                  TABLE_OHLC1, 
                                  data_orders) -> None:
    """ """
    try:

        if currency_inline_with_database_address(currency, TABLE_OHLC1) and "open_interest" in data_orders:
        
            open_interest = data_orders["open_interest"]
                            
            last_tick_query_ohlc1: str = querying_arithmetic_operator("tick", "MAX", TABLE_OHLC1)

            last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(last_tick_query_ohlc1)
                
            await update_status_data(TABLE_OHLC1, "open_interest", last_tick1_fr_sqlite, WHERE_FILTER_TICK, open_interest, "is")

    except Exception as error:
        print (f"error allocating ohlc {error}")