# -*- coding: utf-8 -*-

# built ins
import asyncio
import time

# installed
from loguru import logger as log

# user defined formula
from utilities import system_tools, string_modification as str_mod
from db_management import sqlite_management
from strategies.basic_strategy import summing_transactions_under_label_int, get_transaction_label,has_closed_label,get_label_integer

def get_transactions_with_closed_label (transactions_all: list) -> list:
    """ """

    return [
            o for o in transactions_all if "closed" in o["label"]
        ]


def get_closed_open_transactions_under_same_label_int (transactions_all: list, label: str) -> list:
    """ """
    label_integer=get_label_integer(label)["int"]

    return [
            o for o in transactions_all if label_integer in o["label"]
        ]

def check_if_transaction_has_closed_label_before (transactions_all, label_integer) -> bool:
    """ """
    has_closed_label = (
                    [
                        o['has_closed_label']
                        for o in transactions_all
                        if label_integer in o["label"] and "open" in o["label"]
                    ]
                )[0]
    
    if has_closed_label == 0:
        has_closed_label= False

    if has_closed_label == 1:
        has_closed_label= True

    return False if transactions_all==[] else has_closed_label


async def clean_up_closed_transactions(transactions_all: list = None) -> None:
    """
    closed transactions: buy and sell in the same label id = 0. When flagged:
    1. remove them from db for open transactions/my_trades_all_json
    2. move them to table for closed transactions/my_trades_closed_json
    """

    log.info("clean_up_closed_transactions-START")
    transaction_with_closed_labels = get_transactions_with_closed_label(transactions_all)
    log.error (f"transactions_all {transactions_all}")
    log.warning (f"transaction_with_closed_labels {transaction_with_closed_labels}")
    time.sleep(5)
    for transaction in transaction_with_closed_labels:

        size_to_close= await summing_transactions_under_label_int(transaction, transactions_all)
        log.debug (f"transaction {transaction} size_to_close {size_to_close}")
        time.sleep(5)

        if size_to_close==0 :
                    
            label= get_transaction_label(transaction)
            
            label_integer=get_label_integer(label)["int"]
            transactions_with_zero_sum = (
                    [
                        o for o in transactions_all
                        if label_integer in o["label"]
                    ]
                )
            where_filter = f"order_id"
            log.info (f"transactions_with_zero_sum {transactions_with_zero_sum} label {label}")
            for transaction in transactions_with_zero_sum:
                log.warning (f"transaction_with_zero_sum AAAAAAAAAAAAA {transaction}")
                time.sleep(5)
                order_id=transaction["order_id"]
                await sqlite_management.deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        order_id,
                    )
                await sqlite_management.insert_tables(
                        "my_trades_closed_json", transaction
                    )

async def clean_up_closed_transactions_(transactions_all: list = None) -> None:
    """
    closed transactions: buy and sell in the same label id = 0. When flagged:
    1. remove them from db for open transactions/my_trades_all_json
    2. move them to table for closed transactions/my_trades_closed_json
    """

    log.info("clean_up_closed_transactions-START")

    # clean up transactions all
    transactions_all = [o for o in transactions_all if o["label"] != None]

    if transactions_all != []:
        trades_with_closed_labels = get_transactions_with_closed_label(transactions_all)

        for transaction in trades_with_closed_labels:

            # get label net
            label_net = str_mod.remove_redundant_elements(
                [
                    str_mod.parsing_label(o["label"])["transaction_net"]
                    for o in [transaction]
                ]
            )[0]

            # get transactions net
            transactions_under_label_main = (
                0
                if transaction == []
                else (
                    [
                        o
                        for o in transactions_all
                        if str_mod.parsing_label(o["label"])["transaction_net"]
                        == label_net
                    ]
                )
            )

            net_sum = (
                []
                if transactions_under_label_main == []
                else sum([o["amount_dir"] for o in transactions_under_label_main])
            )

            if len(transactions_under_label_main) > 2:

                # get_closed_labels under_label_main
                transactions_closed = [
                    o
                    for o in transactions_under_label_main
                    if "closed" in o["label"]
                ]

                # get_closed_labels under_label_main
                transactions_open = [
                    o
                    for o in transactions_under_label_main
                    if "open" in o["label"]
                ]

                # get minimum trade seq from closed/open label main (to be paired vs open/closed label)
                min_closed = min([o["trade_seq"] for o in transactions_closed])
                min_open = min([o["trade_seq"] for o in transactions_open])

                # combining open vs closed transactions
                transactions_under_label_main = [
                    o
                    for o in transactions_under_label_main
                    if o["trade_seq"] == min_closed or "open" in o["label"]
                ]

                if len(transactions_open) > 1:
                    transactions_under_label_main = [
                        o
                        for o in transactions_under_label_main
                        if o["trade_seq"] == min_closed or o["trade_seq"] == min_open
                    ]

                # get net sum of the transactions open and closed
                net_sum = (
                    []
                    if transactions_under_label_main == []
                    else sum([o["amount_dir"] for o in transactions_under_label_main])
                )

                # excluded trades closed labels from above trade seq
                transactions_excess = [
                    o for o in transactions_closed if o["trade_seq"] != min_closed
                ]
                log.debug(transactions_closed)
                log.error(transactions_excess)
                # transactions_excess = str_mod.parsing_sqlite_json_output(
                #    [o["data"] for o in result_transactions_excess]
                # )

                for transaction in transactions_excess:
                    trade_seq = transaction["trade_seq"]
                    label = transaction["label"]
                    tstamp = transaction["timestamp"]
                    new_label = str_mod.parsing_label(label, tstamp)["flipping_closed"]
                    transaction["label"] = new_label

                    where_filter = f"trade_seq"
                    await sqlite_management.deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        trade_seq,
                    )
                    await sqlite_management.insert_tables(
                        "my_trades_all_json", transaction
                    )

                    # refreshing data
                    await system_tools.sleep_and_restart(1)

            if net_sum == 0:

                # get trade seq
                result = [o["trade_seq"] for o in transactions_under_label_main]
                # log.info(f' result {result}')

                for res in result:

                    my_trades_open_sqlite: list = (
                        await sqlite_management.querying_table("my_trades_all_json")
                    )
                    my_trades_open: list = (
                        await sqlite_management.executing_label_and_size_query(
                            "my_trades_all_json"
                        )
                    )

                    result_to_dict = (
                        [o for o in my_trades_open if o["trade_seq"] == res]
                    )[0]

                    where_filter = f"trade_seq"
                    await sqlite_management.deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        res,
                    )
                    await sqlite_management.insert_tables(
                        "my_trades_closed_json", result_to_dict
                    )

            if net_sum != 0:

                # get trade seq
                result = [o["trade_seq"] for o in transactions_under_label_main]

                for res in result:

                    my_trades_open_sqlite: list = (
                        await sqlite_management.querying_table("my_trades_all_json")
                    )
                    my_trades_open: list = my_trades_open_sqlite["list_data_only"]
                    result_to_dict = (
                        [o for o in my_trades_open if o["trade_seq"] == res]
                    )[0]
                    result_to_dict["label"] = str_mod.parsing_label(
                        result_to_dict["label"]
                    )["closed_to_open"]

                    where_filter = f"trade_seq"
                    await sqlite_management.deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        res,
                    )
                    await sqlite_management.insert_tables(
                        "my_trades_all_json", result_to_dict
                    )

    log.info("clean_up_closed_transactions-FINISH")


async def count_and_delete_ohlc_rows(rows_threshold: int = 1000000):

    log.info("count_and_delete_ohlc_rows-START")
    tables = ["ohlc1_eth_perp_json", "ohlc30_eth_perp_json"]
    database: str = "databases/trading.sqlite3"

    log.error(tables)

    for table in tables:

        count_rows_query = sqlite_management.querying_arithmetic_operator(
            "tick", "COUNT", table
        )
        rows = await sqlite_management.executing_query_with_return(count_rows_query)
        rows = rows[0]["COUNT (tick)"]

        if rows > rows_threshold:

            where_filter = f"tick"
            first_tick_query = sqlite_management.querying_arithmetic_operator(
                "tick", "MIN", table
            )
            first_tick_fr_sqlite = await sqlite_management.executing_query_with_return(
                first_tick_query
            )
            first_tick = first_tick_fr_sqlite[0]["MIN (tick)"]

            await sqlite_management.deleting_row(
                table, database, where_filter, "=", first_tick
            )
    log.info("count_and_delete_ohlc_rows-DONE")
