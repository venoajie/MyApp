#!/usr/bin/python3
# -*- coding: utf-8 -*-


# built ins
import asyncio

import json
from utilities.string_modification import (transform_nested_dict_to_list)
from loguru import logger as log
import requests

from db_management.sqlite_management import (
    update_status_data,
    querying_last_open_interest,
    deleting_row,
    querying_arithmetic_operator,
    executing_query_with_return,
    insert_tables,
)

from utilities.system_tools import raise_error_message


async def last_open_interest_fr_sqlite(last_tick_query_ohlc1) -> float:
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


async def ohlc_result_per_time_frame(
    message_channel,
    instrument_ticker,
    data_orders,
    TABLE_OHLC1: str,
    TABLE_OHLC30: str,
    TABLE_OHLC60: str,
    TABLE_OHLC1D: str,
    WHERE_FILTER_TICK: str = "tick",
    DATABASE: str = "databases/trading.sqlite3",
) -> None:

    last_tick_query_ohlc1: str = querying_arithmetic_operator(
        WHERE_FILTER_TICK, "MAX", TABLE_OHLC1
    )

    last_tick_query_ohlc30: str = querying_arithmetic_operator(
        WHERE_FILTER_TICK, "MAX", TABLE_OHLC30
    )
    last_tick_query_ohlc60: str = querying_arithmetic_operator(
        WHERE_FILTER_TICK, "MAX", TABLE_OHLC60
    )

    last_tick_query_ohlc1D: str = querying_arithmetic_operator(
        WHERE_FILTER_TICK, "MAX", TABLE_OHLC1D
    )

    last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(last_tick_query_ohlc1)

    last_tick_fr_data_orders: int = data_orders["tick"]

    if (
        TABLE_OHLC30 != None
        or TABLE_OHLC1 != None
        or TABLE_OHLC60 != None
        or TABLE_OHLC1 != None
    ):
        #print(f"allocating ohlc message_channel {message_channel} instrument_ticker {instrument_ticker}")
        #print(f"last_tick_fr_data_orders {last_tick_fr_data_orders} last_tick1_fr_sqlite {last_tick1_fr_sqlite}")
        #print(message_channel == f"chart.trades.{instrument_ticker}.1")

        if message_channel == f"chart.trades.{instrument_ticker}.1":

            
            
            # refilling current ohlc table with updated data
            if last_tick1_fr_sqlite == last_tick_fr_data_orders:
                await update_status_data(TABLE_OHLC1, "data", last_tick1_fr_sqlite, WHERE_FILTER_TICK, data_orders, "is")

            # new tick ohlc
            else:
                
                ohlc_endPoint = f" https://deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp={last_tick_fr_data_orders}&instrument_name={instrument_ticker}&resolution=1&start_timestamp={last_tick1_fr_sqlite}"

                ohlc_request = requests.get(ohlc_endPoint).json()["result"]
                result = transform_nested_dict_to_list(ohlc_request)
                
                #log.debug (f"ohlc {result}")
                #if "PERPETUAL" in instrument_ticker:
                    #log.debug (f"ohlc {result}")
                
                    #log.error (f"{instrument_ticker} last_tick1_fr_sqlite {last_tick1_fr_sqlite} last_tick_fr_data_orders {last_tick_fr_data_orders} {last_tick1_fr_sqlite == last_tick_fr_data_orders}")
                
                # prepare query
                open_interest_last_value_query = querying_last_open_interest(
                    last_tick1_fr_sqlite, TABLE_OHLC1
                )

                # get current oi
                open_interest_last_value = await last_open_interest_fr_sqlite(
                    open_interest_last_value_query
                )

                # insert new ohlc data
                await insert_tables(TABLE_OHLC1, data_orders)

                # update last tick
                last_tick1_fr_sqlite = await last_tick_fr_sqlite(last_tick_query_ohlc1)


                # insert open interest in previous tick to the new tick
                
                log.error (f"data_orders {data_orders}")
                log.error (f"open_interest_last_value {open_interest_last_value}")
                log.error (f"last_tick1_fr_sqlite {last_tick1_fr_sqlite}")
                
                await update_status_data(TABLE_OHLC1, "open_interest", last_tick1_fr_sqlite, WHERE_FILTER_TICK, open_interest_last_value, "is")
                
                
        if message_channel == f"chart.trades.{instrument_ticker}.30":

            last_tick30_fr_sqlite = await last_tick_fr_sqlite(last_tick_query_ohlc30)

            if last_tick30_fr_sqlite == last_tick_fr_data_orders:

                await deleting_row(
                    TABLE_OHLC30,
                    DATABASE,
                    WHERE_FILTER_TICK,
                    "=",
                    last_tick30_fr_sqlite,
                )

                await insert_tables(TABLE_OHLC30, data_orders)

            else:
                await insert_tables(TABLE_OHLC30, data_orders)

        if message_channel == f"chart.trades.{instrument_ticker}.60":

            last_tick60_fr_sqlite = await last_tick_fr_sqlite(last_tick_query_ohlc60)

            if last_tick60_fr_sqlite == last_tick_fr_data_orders:

                await deleting_row(
                    TABLE_OHLC60,
                    DATABASE,
                    WHERE_FILTER_TICK,
                    "=",
                    last_tick60_fr_sqlite,
                )

                await insert_tables(TABLE_OHLC60, data_orders)

            else:
                await insert_tables(TABLE_OHLC60, data_orders)

        if message_channel == f"chart.trades.{instrument_ticker}.1D":

            last_tick1D_fr_sqlite = await last_tick_fr_sqlite(last_tick_query_ohlc1D)

            if last_tick1D_fr_sqlite == last_tick_fr_data_orders:

                await deleting_row(
                    TABLE_OHLC1D,
                    DATABASE,
                    WHERE_FILTER_TICK,
                    "=",
                    last_tick1D_fr_sqlite,
                )

                await insert_tables(TABLE_OHLC1D, data_orders)

            else:
                await insert_tables(TABLE_OHLC1D, data_orders)


def currency_inline_with_database_address (currency: str, database_address: str) -> bool:
    return currency.lower()  in str(database_address)


async def inserting_open_interest(currency, DATABASE, WHERE_FILTER_TICK, TABLE_OHLC1, data_orders) -> None:
    """ """
    try:

        if currency_inline_with_database_address(currency,TABLE_OHLC1) and "open_interest" in data_orders:
        
            open_interest = data_orders["open_interest"]
                            
            last_tick_query_ohlc1: str = querying_arithmetic_operator(
                "tick", "MAX", TABLE_OHLC1
            )

            last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(
                last_tick_query_ohlc1
            )
            
            log.debug (f"open_interest_last_value {open_interest_last_value}")
            log.debug (f"last_tick1_fr_sqlite {last_tick1_fr_sqlite}")
                
            await update_status_data(TABLE_OHLC1, "open_interest", last_tick1_fr_sqlite, WHERE_FILTER_TICK, data_orders, "is")

    except Exception as error:
        print (f"error allocating ohlc {error}")