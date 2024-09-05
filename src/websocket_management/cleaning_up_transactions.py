# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from loguru import logger as log

from db_management.sqlite_management import (
    executing_closed_transactions,
    executing_general_query_with_single_filter,
    querying_table,
    insert_tables,
    deleting_row,
    executing_query_with_return,
    querying_arithmetic_operator,
    querying_duplicated_transactions,
)

# user defined formula
from utilities.string_modification import find_unique_elements, get_duplicated_elements
from strategies.basic_strategy import (
    get_additional_params_for_open_label,
    summing_transactions_under_label_int,
    get_transaction_label,
    get_label_integer,
    querying_label_and_size,
    get_order_label,
)
from strategies.config_strategies import max_rows

async def get_unrecorded_order_id(
    from_sqlite_open, from_sqlite_closed, from_exchange
) -> list:
    """ """

    from_sqlite_closed_order_id = [o["order_id"] for o in from_sqlite_closed]

    from_sqlite_open_order_id = [o["order_id"] for o in from_sqlite_open]  

    from_exchange= [o for o in from_exchange if "label" in o]
    
    from_exchange_order_id = [o["order_id"] for o in from_exchange]
    
    combined_closed_open = from_sqlite_open_order_id + from_sqlite_closed_order_id

    unrecorded_order_id = find_unique_elements(
        combined_closed_open, from_exchange_order_id
    )

    unrecorded_order_id = list(
        set(from_exchange_order_id).difference(combined_closed_open)
    )

    return unrecorded_order_id

async def reconciling_between_db_and_exchg_data(
    trades_from_exchange: list, unrecorded_order_id: str
) -> None:
    """ """

    
    if unrecorded_order_id == []:

        trades_from_sqlite_open = await querying_label_and_size("my_trades_all_json")
        trades_from_sqlite_closed = await executing_closed_transactions()
        unrecorded_order_id = await get_unrecorded_order_id(
            trades_from_sqlite_open, trades_from_sqlite_closed, trades_from_exchange
        )

        if unrecorded_order_id == []:
            duplicated_elements = await querying_duplicated_transactions()

            if duplicated_elements != 0:
                print(
                    f" duplicated_elements {duplicated_elements} duplicated_elements != [] {duplicated_elements != []} duplicated_elements == 0 {duplicated_elements == 0}"
                )
                duplicated_labels = [o["label"] for o in duplicated_elements]

                my_trades_open_sqlite: dict = await querying_table("my_trades_all_json")
                my_trades_open_all: list = my_trades_open_sqlite["all"]

                for label in duplicated_labels:
                    id = max(
                        [
                            o["id"]
                            for o in my_trades_open_all
                            if o["label_main"] == label
                        ]
                    )
                    where_filter = f"id"
                    await deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        id,
                    )
    if unrecorded_order_id != None:
        unrecorded_order_id.sort(reverse=True)
        #print(f"unrecorded_order_id {unrecorded_order_id}")
        #print(f"trades_from_exchange {trades_from_exchange}")
        
        transaction_sum=0
        for order_id in unrecorded_order_id:

            transaction = [o for o in trades_from_exchange if o["order_id"] == order_id]
            
            #print(f"transaction {transaction} {order_id}")
            
            if transaction !=[]:

                label = [
                    o["label"] for o in trades_from_exchange if o["order_id"] == order_id
                ][0]

                if "open" in label:
                    await get_additional_params_for_open_label(transaction[0], label)

                await insert_tables("my_trades_all_json", transaction)


def get_transactions_with_closed_label(transactions_all: list) -> list:
    """ """

    return [o for o in transactions_all if "closed" in o["label"]]


async def clean_up_duplicate_elements() -> None:
    """ """

    data_from_db_closed = await querying_label_and_size("my_trades_closed_json")
    data_from_db_open = await querying_label_and_size("my_trades_all_json")
    label_from_db_open = get_order_label(data_from_db_open)
    label_from_db_closed = get_order_label(data_from_db_closed)

    # log.warning (f"order_id_from_db_open {label_from_db_open}")

    for label in label_from_db_open:
        log.warning(f"order_id {label}")
        log.debug(f"label_from_db_open {label in label_from_db_closed}")
        if label in label_from_db_closed:
            log.critical(f"del duplicate order id {label}")
            where_filter = f"label_main"
            await deleting_row(
                "my_trades_all_json",
                "databases/trading.sqlite3",
                where_filter,
                "=",
                label,
            )


def get_closed_open_transactions_under_same_label_int(
    transactions_all: list, label: str
) -> list:
    """ """
    label_integer = get_label_integer(label)["int"]

    return [o for o in transactions_all if label_integer in o["label"]]


def check_if_transaction_has_closed_label_before(
    transactions_all, label_integer
) -> bool:
    """ """
    has_closed_label = (
        [
            o["has_closed_label"]
            for o in transactions_all
            if label_integer in o["label"] and "open" in o["label"]
        ]
    )[0]

    if has_closed_label == 0:
        has_closed_label = False

    if has_closed_label == 1:
        has_closed_label = True

    return False if transactions_all == [] else has_closed_label


async def clean_up_closed_transactions(instrument_name) -> None:
    """
    closed transactions: buy and sell in the same label id = 0. When flagged:
    1. remove them from db for open transactions/my_trades_all_json
    2. move them to table for closed transactions/my_trades_closed_json
    """

    transactions_all: list = await executing_general_query_with_single_filter("my_trades_all_json", instrument_name)

    transaction_with_closed_labels = get_transactions_with_closed_label(
        transactions_all
    )

    for transaction in transaction_with_closed_labels:

        size_to_close = await summing_transactions_under_label_int(
            transaction, transactions_all
        )
        
        print (f"transaction {transaction} {size_to_close}")

        if size_to_close == 0:

            label = get_transaction_label(transaction)

            label_integer = get_label_integer(label)["int"]
            transactions_with_zero_sum = [
                o for o in transactions_all if label_integer in o["label"]
            ]
            where_filter = f"order_id"
            
            print (f"transactions_with_zero_sum {transactions_with_zero_sum}")

            for transaction in transactions_with_zero_sum:
                order_id = transaction["order_id"]

                await insert_tables("my_trades_closed_json", transaction)

                await deleting_row(
                    "my_trades_all_json",
                    "databases/trading.sqlite3",
                    where_filter,
                    "=",
                    order_id,
                )


async def count_and_delete_ohlc_rows():

    log.info("count_and_delete_ohlc_rows-START")
    tables = ["market_analytics_json", 
              "ohlc1_eth_perp_json", 
              "ohlc1_btc_perp_json", 
              "ohlc30_eth_perp_json", 
              "ohlc60_eth_perp_json", 
              "supporting_items_json"]
    
    database: str = "databases/trading.sqlite3"  

    for table in tables:
        rows_threshold= max_rows(table)
        
        if "supporting_items_json" in table:
            where_filter = f"id"
            
        else:
            where_filter = f"tick"
        
        count_rows_query = querying_arithmetic_operator(where_filter, "COUNT", table)

        rows = await executing_query_with_return(count_rows_query)
        
        rows = rows[0]["COUNT (tick)"] if where_filter=="tick" else rows[0]["COUNT (id)"]
            
        if rows > rows_threshold:
                  
            first_tick_query = querying_arithmetic_operator(where_filter, "MIN", table)
            
            first_tick_fr_sqlite = await executing_query_with_return(first_tick_query)
            
            if where_filter=="tick":
                first_tick = first_tick_fr_sqlite[0]["MIN (tick)"] 
            
            if where_filter=="id":
                first_tick_fr_sqlite[0]["MIN (id)"]

            await deleting_row(table, database, where_filter, "=", first_tick)
            
    log.info("count_and_delete_ohlc_rows-DONE")
