#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp

# user defined formula
from strategies import entries_exits
from strategies.basic_strategy import get_additional_params_for_open_label
from websocket_management.cleaning_up_transactions import clean_up_closed_transactions
from utilities import pickling, system_tools, string_modification as str_mod
from deribit_get import (
    get_instruments,
    get_currencies,
    get_server_time
    )
from db_management.sqlite_management import (
    insert_tables,
    querying_table,
    executing_closed_transactions
    )
from strategies.basic_strategy import (
    querying_label_and_size,
    get_market_condition
    )
from websocket_management.ws_management import (
    opening_transactions,
    reading_from_pkl_database,
    closing_transactions,
    get_my_trades_from_exchange
    )

symbol = "ETH-PERPETUAL"
currency = "ETH"


def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)


async def get_instruments(connection_url, currency) -> float:
    """ """

    result = await get_instruments(connection_url, currency)

    return result


async def get_currencies(connection_url) -> float:
    """ """

    result = await get_currencies(connection_url)

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
        else str_mod.remove_redundant_elements(
            [
                str_mod.parsing_label(o["label"])["transaction_net"]
                for o in my_trades_open_remove_closed_labels
            ]
        )
    )

def is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_position):
    """ """
    return sum_my_trades_open_sqlite_all_strategy == size_from_position
    
async def get_unrecorded_order_id(from_sqlite_open, 
                                  from_sqlite_closed,
                                  from_exchange
                                  ) -> dict:
    """ """  
    
    from_sqlite_closed_order_id= [o["order_id"] for o in from_sqlite_closed]

    from_sqlite_open_order_id= [o["order_id"] for o in from_sqlite_open]

    from_exchange_order_id= [o["order_id"] for o in from_exchange]
    print (f"from_sqlite_closed_order_id {from_sqlite_closed_order_id}")
    print (f"from_sqlite_open_order_id {from_sqlite_open_order_id}")
    print (f"from_exchange_order_id {from_exchange_order_id}")

    combined_closed_open= from_sqlite_open_order_id+from_sqlite_closed_order_id

    unrecorded_order_id= str_mod.find_unique_elements(combined_closed_open, from_exchange_order_id) 

    unrecorded_order_id=set(from_exchange_order_id).difference(combined_closed_open)
    
    return unrecorded_order_id

async def run_every_5_seconds() -> None:
    """ """

    QTY= 10
    ONE_PCT = 1 / 100
    WINDOW = 9
    RATIO = 0.9
    THRESHOLD = 0.01 * ONE_PCT
    TAKE_PROFIT_PCT_DAILY = ONE_PCT

    # gathering basic data
    reading_from_database: dict = await reading_from_pkl_database(currency)

    # get portfolio data
    portfolio: list = reading_from_database["portfolio"]

    # fetch positions for all instruments
    positions_all: list = reading_from_database["positions_from_sub_account"]
    # print(f"positions_all-recurring {positions_all} ")
    size_from_positions: int = (
        0 if positions_all == [] else sum([o["size"] for o in positions_all])
    )

    # fetch strategies attributes
    strategies = entries_exits.strategies

    market_condition = await get_market_condition(
        THRESHOLD, WINDOW, RATIO
    )
    print(f"market_condition {market_condition}")

    my_trades_open_sqlite: dict = await querying_table(
        "my_trades_all_json"
    )
    my_trades_open_list_data_only: list = my_trades_open_sqlite["list_data_only"]

    instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
    server_time = await current_server_time()
    instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
    server_time = await current_server_time()

    # remove transactions without label
    my_trades_open = [o for o in my_trades_open_list_data_only if "label" in o]

    my_trades_open_remove_closed_labels = (
        []
        if my_trades_open == []
        else [o for o in my_trades_open if "closed" not in o["label"]]
    )

    label_transaction_net = get_label_transaction_net(my_trades_open_remove_closed_labels)

    trades_from_sqlite_open= await querying_label_and_size("my_trades_all_json")
    trades_from_sqlite_closed= await executing_closed_transactions()
    trades_from_exchange= await get_my_trades_from_exchange(QTY, currency)
    
    unrecorded_order_id= await get_unrecorded_order_id(trades_from_sqlite_open,trades_from_sqlite_closed,trades_from_exchange)
    
    await clean_up_closed_transactions()
    
    transactions_all_summarized: list = await querying_label_and_size("my_trades_all_json")
    #print (f"transactions_all_summarized {transactions_all_summarized}")
    sum_my_trades_sqlite= sum([o["amount"]
                for o in transactions_all_summarized
            ])
    total_difference_and_solution_is_zero=abs(sum_my_trades_sqlite-size_from_positions)
    size_is_consistent: bool =  is_size_consistent(
                    sum_my_trades_sqlite, size_from_positions
                )
    print (f"size_is_consistent {size_is_consistent} sum_my_trades_sqlite {sum_my_trades_sqlite} size_from_positions {size_from_positions} ")
    
    if size_is_consistent:

        await closing_transactions(
            label_transaction_net,
            portfolio,
            strategies,
            my_trades_open_sqlite,
            my_trades_open,
            market_condition,
            currency,
        )

        for instrument in instrument_transactions:
            await opening_transactions(
                instrument,
                portfolio,
                strategies,
                my_trades_open_sqlite,
                size_from_positions,
                server_time,
                market_condition,
                TAKE_PROFIT_PCT_DAILY,
            )

    if not size_is_consistent:
        print(f"unrecorded_order_id {unrecorded_order_id}")
        for order_id in unrecorded_order_id:

            transaction= [o for o in trades_from_exchange if o["order_id"] == order_id]

            print(f"transaction {transaction}")

            label= [o["label"] for o in trades_from_exchange if o["order_id"] == order_id][0]
            print(f"label  {label} order_id  {order_id}")
            if "open" in label:
                 await get_additional_params_for_open_label (transaction[0], label)

            await insert_tables("my_trades_all_json", transaction)
            print(f"transaction {transaction}")

    await clean_up_closed_transactions()


async def run_every_60_seconds() -> None:
    """ """

    from websocket_management.cleaning_up_transactions import count_and_delete_ohlc_rows

    rows_threshold = 1000000

    await count_and_delete_ohlc_rows(rows_threshold)


#


async def check_and_save_every_60_minutes():
    connection_url: str = "https://www.deribit.com/api/v2/"

    try:

        get_currencies_all = await get_currencies(connection_url)
        currencies = [o["currency"] for o in get_currencies_all["result"]]
        #        print(currencies)

        for currency in currencies:

            instruments = await get_instruments(connection_url, currency)
            # print (f'instruments {instruments}')

            my_path_instruments = system_tools.provide_path_for_file(
                "instruments", currency
            )

            pickling.replace_data(my_path_instruments, instruments)

        my_path_cur = system_tools.provide_path_for_file("currencies")

        pickling.replace_data(my_path_cur, currencies)
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

        schedule.every(5).seconds.do(run_every_5_seconds)
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
