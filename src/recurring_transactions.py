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
                                           )
from utilities.system_tools import (catch_error_message, 
                                    provide_path_for_file)
from deribit_get import (get_instruments, 
                         get_currencies, 
                         get_server_time)
from db_management.sqlite_management import (
    querying_table,
)
from market_understanding.technical_analysis import (
    insert_market_condition_result,
)
from websocket_management.ws_management import (
    closing_transactions
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


async def back_up_db():
    import sqlite3

    src = sqlite3.connect("databases/trading.sqlite3")
    dst = sqlite3.connect("databases/back_up/trading.bak")
    with src:
        src.backup(dst)
    dst.close()
    src.close()

    catch_error_message(
    "back up done")

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
    
    #await back_up_db()
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
