#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# import datetime

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

# user defined formula
from strategies.config_strategies import (strategies, preferred_spot_currencies) 
from utilities.pickling import replace_data

from utilities.string_modification import (remove_redundant_elements, 
                                           parsing_label,
                                           get_duplicated_elements)
from utilities.system_tools import (catch_error_message, 
                                    provide_path_for_file)
from deribit_get import (get_instruments, 
                         get_currencies, 
                         get_server_time)
from db_management.sqlite_management import (
    querying_table,
    executing_closed_transactions,
)
from strategies.basic_strategy import querying_label_and_size
from market_understanding.technical_analysis import (
    get_market_condition,
    insert_market_condition_result,
)
from websocket_management.ws_management import (
    opening_transactions,
    reading_from_pkl_database,
    closing_transactions,
    get_my_trades_from_exchange,
    is_size_consistent,
    balancing_the_imbalance,
)
from websocket_management.cleaning_up_transactions import (
    get_unrecorded_order_id,
    clean_up_closed_transactions,
    clean_up_duplicate_elements,
)

# stop_time = datetime.datetime.now() + datetime.timedelta(hours=1/60)


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


async def run_every_3_seconds() -> None:
    """ """

    await future_spreads("ETH")
    
    market_condition_all = await querying_table("market_analytics_json-last")

    market_condition = market_condition_all["list_data_only"][0]
    my_trades_open_sqlite: dict = await querying_table("my_trades_all_json")

    my_trades_open_list_data_only: list = my_trades_open_sqlite["list_data_only"]

    # remove transactions without label
    my_trades_open = [o for o in my_trades_open_list_data_only if "label" in o]
    my_trades_open_remove_closed_labels = (
        []
        if my_trades_open == []
        else [o for o in my_trades_open if "closed" not in o["label"]]
    )

    label_transaction_net = get_label_transaction_net(
        my_trades_open_remove_closed_labels
    )
    await closing_transactions(
        label_transaction_net,
        strategies,
        my_trades_open_sqlite,
        my_trades_open,
        market_condition,
    )


async def run_every_5_seconds() -> None:
    """ """

    QTY = 20
    ONE_PCT = 1 / 100
    TAKE_PROFIT_PCT_DAILY = ONE_PCT * 1
    
    currencies=  preferred_spot_currencies()
    
    for currency in currencies:

        # gathering basic data
        reading_from_database: dict = await reading_from_pkl_database(currency)

        # get portfolio data
        portfolio: list = reading_from_database["portfolio"]

        # fetch positions for all instruments
        positions_all: list = reading_from_database["positions_from_sub_account"]
        #log.info(f"positions_all-recurring {positions_all} ")
        size_from_positions: int = (
            0 if positions_all == [] else sum([o["size"] for o in positions_all if ["kind"]=="future"])
        )
        
        equity= portfolio[0]["equity"]
        log.critical (f" currency {currency}")
        #log.warning (f" portfolio {portfolio} equity {equity >0}")

        #log.warning (f" positions_all {positions_all}")
        
        if equity >0:

            # fetch strategies attributes
            market_condition_all = await querying_table("market_analytics_json-last")
            market_condition = market_condition_all["list_data_only"][0]

            my_trades_open_sqlite: dict = await querying_table("my_trades_all_json")
            instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
            server_time = await current_server_time()
            instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
            server_time = await current_server_time()

            trades_from_sqlite_open = await querying_label_and_size("my_trades_all_json")
            trades_from_sqlite_closed = await executing_closed_transactions()
            balancing_trades = await get_my_trades_from_exchange(QTY, currency)
            active_instruments_name= get_duplicated_elements([ o["instrument_name"] for o in trades_from_sqlite_open])

            for instrument in active_instruments_name:
                log.warning (f"instrument {instrument}")
                trades_from_sqlite_closed = await executing_general_query_with_single_filter(
                                                    "my_trades_closed_json", instrument, max_closed_transactions_downloaded_from_sqlite, "id"
                                                    )
                
                trades_from_exchange_instrument= ([ o for o in trades_from_sqlite_open if o["instrument_name"]==instrument])
                size_from_position: int = (
            0 if positions_all == [] else sum([o["size"] for o in positions_all if o["instrument_name"]==instrument])
        )                    
                size_from_my_trades = sum([o["amount"] for o in trades_from_exchange_instrument])
         
                size_is_consistent: bool = await is_size_consistent(
                    size_from_my_trades, size_from_position
                )

                unrecorded_order_id = await get_unrecorded_order_id(
                    trades_from_sqlite_open, trades_from_sqlite_closed, balancing_trades
                )
                
                #log.debug (f"size_is_consistent {size_is_consistent} size_from_my_trades {size_from_my_trades} size_from_position {size_from_position}")
                
                if not size_is_consistent:
                    await balancing_the_imbalance(
                trades_from_exchange_instrument,
                unrecorded_order_id,
                size_from_my_trades,
                size_from_position,
            )



                await clean_up_closed_transactions(instrument)

            transactions_all_summarized: list = await querying_label_and_size(
                "my_trades_all_json"
            )
            # print (f"transactions_all_summarized {transactions_all_summarized}")
            sum_my_trades_sqlite = sum([o["amount"] for o in transactions_all_summarized])
            total_difference_and_solution_is_zero = abs(
                sum_my_trades_sqlite - size_from_positions
            )

            size_is_consistent: bool = await is_size_consistent(
                sum_my_trades_sqlite, size_from_positions
            )

                #await clean_up_duplicate_elements()
                #trades_from_exchange = await get_my_trades_from_exchange(QTY, currency)
                #await balancing_the_imbalance(trades_from_exchange)

            #await clean_up_closed_transactions()

            # print (f"stop_time {stop_time} datetime.datetime.now() {datetime.datetime.now()} {datetime.datetime.now() > stop_time}")

            # in relevant function ...
            # if datetime.datetime.now() > stop_time:
            #    import subprocess

            #    await cancel_the_cancellables()
            #    print (f"test")
            #    subprocess.call(["shutdown", "-r", "-t", "0"])


async def run_every_60_seconds() -> None:
    """ """

    from websocket_management.cleaning_up_transactions import count_and_delete_ohlc_rows

    await count_and_delete_ohlc_rows()


async def run_every_15_seconds() -> None:
    """ """

    ONE_PCT = 1 / 100
    WINDOW = 9
    RATIO = 0.9
    THRESHOLD = 0.01 * ONE_PCT
    
    
    currencies=  preferred_spot_currencies()
    
    for currency in currencies:

        await insert_market_condition_result(f"{currency}-PERPETUAL", WINDOW, RATIO)


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


async def get_open_interest_history() -> None:
    headers = {
        "accept": "application/json",
        "coinglassSecret": "877ad9af931048aab7e468bda134942e",
    }
    session = aiohttp.ClientSession()
    time_frame = "m5"
    symbol = "BTC"
    currency = "USD"
    url = f"https://open-api.coinglass.com/public/v2/?symbol={symbol}&time_type=all&currency={currency}"

    async with session.get(url, headers=headers) as resp:
        print(await resp.text())


if __name__ == "__main__":

    try:
        # asyncio.get_event_loop().run_until_complete(check_and_save_every_60_minutes())
        schedule.every().hour.do(check_and_save_every_60_minutes)

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
