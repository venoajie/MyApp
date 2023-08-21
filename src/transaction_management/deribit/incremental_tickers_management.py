#!/usr/bin/python3
# -*- coding: utf-8 -*-

# installed
import asyncio
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools
from market_understanding import futures_analysis


async def instrument_ticker(currency, message_channel, instruments_kind) -> None:

    try:

        instrument_ticker = (message_channel)[19:]
        if message_channel == f"incremental_ticker.{instrument_ticker}":
            my_path_futures_analysis = system_tools.provide_path_for_file(
                "futures_analysis", currency
            )

            my_path_ticker = system_tools.provide_path_for_file(
                "ticker", instrument_ticker
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
        await system_tools.raise_error_message(
            error, 10, "instrument ticker - failed to process data",
        )


async def distribute_ticker_result_as_per_data_type(
    my_path_ticker, data_orders
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
            "instrument ticker - failed to distribute_incremental_ticker_result_as_per_data_type",
        )
