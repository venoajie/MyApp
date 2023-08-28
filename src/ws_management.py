#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools
from market_understanding import futures_analysis
from db_management import sqlite_management


async def ws_manager_market(
    message_channel, data_orders, instruments_kind, currency
) -> None:

    log.warning(message_channel)
    DATABASE: str = "databases/trading.sqlite3"
    TABLE_OHLC1: str = "ohlc1_eth_perp_json"
    TABLE_OHLC30: str = "ohlc30_eth_perp_json"
    TABLE_OHLC60: str = "ohlc60_eth_perp_json"
    TABLE_OHLC1D: str = "ohlc1D_eth_perp_json"
    WHERE_FILTER_TICK: str = "tick"

    last_tick_query_ohlc1: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC1
    )

    last_tick_query_ohlc30: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC30
    )
    last_tick_query_ohlc60: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC60
    )

    last_tick_query_ohlc1D: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC1D
    )

    last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(last_tick_query_ohlc1)

    if "chart.trades.ETH-PERPETUAL." in message_channel:

        last_tick_fr_data_orders: int = data_orders["tick"]

        if (
            TABLE_OHLC30 != None
            or TABLE_OHLC1 != None
            or TABLE_OHLC60 != None
            or TABLE_OHLC1 != None
        ):

            # log.warning(f"message_channel {message_channel}")
            if message_channel == "chart.trades.ETH-PERPETUAL.1":
                log.error(message_channel)

                # refilling current ohlc table with updated data
                if last_tick1_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.replace_row(
                        data_orders,
                        "data",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

                # new tick ohlc
                else:
                    # prepare query
                    open_interest_last_value_query = sqlite_management.querying_last_open_interest(
                        last_tick1_fr_sqlite, TABLE_OHLC1
                    )

                    # get current oi
                    open_interest_last_value = await last_open_interest_fr_sqlite(
                        open_interest_last_value_query
                    )

                    # insert new ohlc data
                    await sqlite_management.insert_tables(TABLE_OHLC1, data_orders)

                    # update last tick
                    last_tick1_fr_sqlite = await last_tick_fr_sqlite(
                        last_tick_query_ohlc1
                    )

                    # insert open interest in previous tick to the new tick
                    await sqlite_management.replace_row(
                        open_interest_last_value,
                        "open_interest",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

            if message_channel == "chart.trades.ETH-PERPETUAL.30":

                last_tick30_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc30
                )

                if last_tick30_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC30,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick30_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC30, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC30, data_orders)

            if message_channel == "chart.trades.ETH-PERPETUAL.60":

                last_tick60_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc60
                )

                if last_tick60_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC60,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick60_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC60, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC60, data_orders)

            if message_channel == "chart.trades.ETH-PERPETUAL.1D":

                last_tick1D_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc1D
                )

                if last_tick1D_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC1D,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick1D_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC1D, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC1D, data_orders)

    instrument_ticker = (message_channel)[19:]
    if message_channel == f"incremental_ticker.{instrument_ticker}":
        log.warning(message_channel)
        my_path_futures_analysis = system_tools.provide_path_for_file(
            "futures_analysis", currency
        )

        my_path_ticker = system_tools.provide_path_for_file("ticker", instrument_ticker)

        try:

            if "PERPETUAL" in data_orders["instrument_name"]:
                log.info(data_orders)

                if "open_interest" in data_orders:

                    open_interest = data_orders["open_interest"]

                    await sqlite_management.replace_row(
                        open_interest,
                        "open_interest",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

            await distribute_ticker_result_as_per_data_type(
                my_path_ticker, data_orders, instrument_ticker
            )

            symbol_index: str = f"{currency}_usd"
            my_path_index: str = system_tools.provide_path_for_file(
                "index", symbol_index
            )
            index_price: list = pickling.read_data(my_path_index)
            ticker_instrument: list = pickling.read_data(my_path_ticker)
            if ticker_instrument != []:
                # log.error(ticker_instrument)
                instrument_name = ticker_instrument[0]["instrument_name"]
                instrument: list = [
                    o
                    for o in instruments_kind
                    if o["instrument_name"] == instrument_name
                ][0]

                # combine analysis of each instrument futures result
                tickers = futures_analysis.combining_individual_futures_analysis(
                    index_price[0]["price"], instrument, ticker_instrument[0],
                )
                ticker_all: list = pickling.read_data(my_path_futures_analysis)

                if ticker_all == None:
                    pickling.replace_data(my_path_futures_analysis, ticker_all)
                else:
                    ticker_all: list = [
                        o
                        for o in ticker_all
                        if o["instrument_name"] != instrument_ticker
                    ]

                    #! double file operation. could be further improved
                    pickling.replace_data(my_path_futures_analysis, ticker_all)

                    pickling.append_and_replace_items_based_on_qty(
                        my_path_futures_analysis, tickers, 100
                    )

        except Exception as error:
            log.error(error)
            await system_tools.raise_error_message(
                "WebSocket management - failed to process data"
            )


async def last_open_interest_fr_sqlite(last_tick_query_ohlc1) -> float:
    """ """
    try:
        last_open_interest = await sqlite_management.executing_query_with_return(
            last_tick_query_ohlc1
        )

    except Exception as error:
        await system_tools.raise_error_message(
            error, "Capture market data - failed to fetch last open_interest",
        )
    return last_open_interest[0]["open_interest"]


async def last_tick_fr_sqlite(last_tick_query_ohlc1) -> int:
    """ """
    try:
        last_tick1_fr_sqlite = await sqlite_management.executing_query_with_return(
            last_tick_query_ohlc1
        )

    except Exception as error:
        await system_tools.raise_error_message(
            error, "Capture market data - failed to fetch last_tick_fr_sqlite",
        )
    return last_tick1_fr_sqlite[0]["MAX (tick)"]


async def distribute_ticker_result_as_per_data_type(
    my_path_ticker, data_orders, instrument
) -> None:
    """ """

    try:
        # ticker: list = pickling.read_data(my_path_ticker)

        if data_orders["type"] == "snapshot":
            pickling.replace_data(my_path_ticker, data_orders)

            # ticker_fr_snapshot: list = pickling.read_data(my_path_ticker)

        else:
            ticker_change: list = pickling.read_data(my_path_ticker)
            if ticker_change != []:
                # log.debug (ticker_change)

                for item in data_orders:
                    ticker_change[0][item] = data_orders[item]
                    pickling.replace_data(my_path_ticker, ticker_change)

    except Exception as error:
        await system_tools.raise_error_message(
            error,
            "WebSocket management - failed to distribute_incremental_ticker_result_as_per_data_type",
        )
