# -*- coding: utf-8 -*-
"""_summary_

Source data:
    _type_: fresh data, rerun. why? 
            1. rare event
            2. reduce overhead for main program
"""
# built ins
import asyncio

# installed
from loguru import logger as log

from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy,
    insert_tables,
    deleting_row,
    executing_query_with_return,
    querying_arithmetic_operator,
    querying_duplicated_transactions,
)

from strategies.config_strategies import paramaters_to_balancing_transactions
# user defined formula

from utilities.system_tools import (
    sleep_and_restart,)
from utilities.string_modification import get_unique_elements
from strategies.basic_strategy import (
    get_additional_params_for_open_label,
    summing_transactions_under_label_int,
    get_transaction_label,
    get_label_integer
)
from strategies.config_strategies import max_rows

from websocket_management.ws_management import (is_size_consistent)

async def get_unrecorded_trade_and_order_id(instrument_name,from_exchange
) -> dict:
    """ """
    
    #log.critical (f"{instrument_name}")

    balancing_params=paramaters_to_balancing_transactions()
        
    max_closed_transactions_downloaded_from_sqlite=balancing_params["max_closed_transactions_downloaded_from_sqlite"]   
    
    column_list: str="order_id", "trade_id"
    
    from_sqlite_open= await executing_query_based_on_currency_or_instrument_and_strategy("my_trades_all_json", 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column_list)                                       

    from_sqlite_closed = await executing_query_based_on_currency_or_instrument_and_strategy("my_trades_closed_json", 
                                                                                            instrument_name, 
                                                                                            "all", 
                                                                                            "all", 
                                                                                            column_list,
                                                                                            max_closed_transactions_downloaded_from_sqlite, 
                                                                                            "id")    
    from_sqlite_closed_order_id = [o["order_id"] for o in from_sqlite_closed]
    from_sqlite_closed_trade_id = [o["trade_id"] for o in from_sqlite_closed]
    #log.info (f"from_sqlite_closed_order_id {from_sqlite_closed_order_id}")
    #log.warning (f"from_sqlite_closed_trade_id {from_sqlite_closed_trade_id}")

    from_sqlite_open_order_id = [o["order_id"] for o in from_sqlite_open]  
    from_sqlite_open_trade_id = [o["trade_id"] for o in from_sqlite_open]  
    #log.info (f"from_sqlite_open_order_id {from_sqlite_open_order_id}")
    #log.warning (f"from_sqlite_open_trade_id {from_sqlite_open_trade_id}")

    from_exchange_with_labels= [o for o in from_exchange if "label" in o]
    
    from_exchange_instrument: int = ([] if from_exchange_with_labels == [] else ([o for o in from_exchange_with_labels if o["instrument_name"]==instrument_name])
                                            )
    #log.info (f"from_exchange_instrument {from_exchange_instrument}")
    from_exchange_order_id = [o["order_id"] for o in from_exchange_instrument]
    from_exchange_trade_id = [o["trade_id"] for o in from_exchange_instrument]
    log.warning (f"from_exchange_order_id {from_exchange_order_id}")
    log.warning (f"from_exchange_trade_id {from_exchange_trade_id}")
    
    combined_order_closed_open = from_sqlite_open_order_id + from_sqlite_closed_order_id
    combined_trade_closed_open = from_sqlite_open_trade_id + from_sqlite_closed_trade_id
    log.warning (f"combined_order_closed_open {combined_order_closed_open}")

    unrecorded_order_id = get_unique_elements(from_exchange_order_id, combined_order_closed_open)
    unrecorded_trade_id = get_unique_elements(from_exchange_trade_id, combined_trade_closed_open)
    
    log.debug (f"unrecorded_order_id {unrecorded_order_id}")
    log.error (f"unrecorded_trade_id {unrecorded_trade_id}")

    return dict(unrecorded_order_id=unrecorded_order_id,
                unrecorded_trade_id=unrecorded_trade_id)


def get_label_from_respected_id (trades_from_exchange, unrecorded_id, marker) -> str:
    #log.info (f"trades_from_exchange {trades_from_exchange}")
    #log.info (f"unrecorded_id {unrecorded_id} marker {marker}")
    
    label= [o["label"] for o in trades_from_exchange if o[marker] == unrecorded_id][0]
    
    #log.info (f"label {label}")
    return label

async def update_db_with_unrecorded_data (trades_from_exchange, unrecorded_id, id_desc) -> None:

    unrecorded_id.sort(reverse=True)
    #print(f"unrecorded_order_id {unrecorded_order_id}")
    #print(f"trades_from_exchange {trades_from_exchange}")
    table= "my_trades_all_json"
    if id_desc== "trade_id":
        marker="trade_id"
    
    if id_desc== "order_id":
        marker="order_id"
    
    marker_plus=marker,"label"

    for tran_id in unrecorded_id:

        transaction = [o for o in trades_from_exchange if o[marker] == tran_id]
        instrument_name= transaction[0] ["instrument_name"]
        #column_list: str="order_id", "trade_id"
        from_sqlite_open= await executing_query_based_on_currency_or_instrument_and_strategy(table, 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         marker_plus)
        id_has_registered_before= [o for o in from_sqlite_open if o[marker] == tran_id]      
        
        #log.error (f"transaction {instrument_name} {transaction} {tran_id}")
        #log.warning (f"id_has_registered_before {id_has_registered_before} {id_has_registered_before==[]}")
        
        if transaction !=[] and id_has_registered_before==[]:

            label = get_label_from_respected_id (trades_from_exchange, tran_id, marker)

            if "open" in label:
                await get_additional_params_for_open_label(transaction[0], label)

            await insert_tables(table, transaction)
            await sleep_and_restart()


async def remove_duplicated_elements () -> None:
    """ 
    
        # label/order id may be duplicated (consider an order id/label was 
        # executed couple of times due to lack of liquidity)
        # There is only one trade_id
       
    """
    
    label_checked=["my_trades_all_json", "my_trades_closed_json"]
    
    where_filter = f"trade_id"
    
    for label in label_checked:
        duplicated_elements_all = await querying_duplicated_transactions(label,where_filter)

        duplicated_elements = 0 if duplicated_elements_all == 0 else [o[where_filter] for o in duplicated_elements_all]
        
        log.info (f"duplicated_elements {duplicated_elements}")

        if duplicated_elements != 0:
            #log. warning (f" duplicated_elements {duplicated_elements} duplicated_elements != [] {duplicated_elements != []} duplicated_elements == 0 {duplicated_elements == 0}"
            #)#

            for trade_id in duplicated_elements:
                
                await deleting_row(
                    label,
                    "databases/trading.sqlite3",
                    where_filter,
                    "=",
                    trade_id,
                )
                await sleep_and_restart()

async def reconciling_between_db_and_exchg_data(instrument_name,
                                                trades_from_exchange: list, positions_from_sub_accounts: list) -> None:
    """ """
    
    unrecorded_transactions= await get_unrecorded_trade_and_order_id(instrument_name,
                                  trades_from_exchange)
    
    unrecorded_order_id= unrecorded_transactions["unrecorded_order_id"]
    unrecorded_trade_id= unrecorded_transactions["unrecorded_trade_id"]
    #log.debug (f"unrecorded_order_id {unrecorded_order_id}")
    #log.warning (f"unrecorded_trade_id {unrecorded_trade_id}")
           
    if unrecorded_order_id != None:
        await update_db_with_unrecorded_data (trades_from_exchange, unrecorded_order_id, "order_id")

    if unrecorded_trade_id != None:
        await update_db_with_unrecorded_data (trades_from_exchange, unrecorded_trade_id, "trade_id")
    
    await remove_duplicated_elements ()
        
    column_list: str= "instrument_name","label", "amount", "price","trade_id"
    
    my_trades_instrument: list= await executing_query_based_on_currency_or_instrument_and_strategy(
                                                "my_trades_all_json", instrument_name, "all", "all", column_list)
    
    sum_my_trades_instrument = sum([o["amount"] for o in my_trades_instrument])
        
    size_from_position: int = (0 if positions_from_sub_accounts == [] else sum([o["size"] for o in positions_from_sub_accounts if o["instrument_name"]==instrument_name])
                                            )
    
    await recheck_result_after_cleaning (instrument_name,
                                         trades_from_exchange,
                                         my_trades_instrument,
                                         sum_my_trades_instrument,
                                         size_from_position)
    
async def recheck_result_after_cleaning  (instrument_name: str,
                                          trades_from_exchange: list,
                                          my_trades_instrument: list,
                                          sum_my_trades_instrument: float,
                                          size_from_position: float) -> list:
    """ """
    
    size_is_consistent: bool = await is_size_consistent(
                                                sum_my_trades_instrument, size_from_position,
                                                instrument_name
                                                )
    if not size_is_consistent:

        unrecorded_transactions= await get_unrecorded_trade_and_order_id(instrument_name,
                                    trades_from_exchange)
        
        unrecorded_trade_id= unrecorded_transactions["unrecorded_trade_id"]
        
        log.error (f"unrecorded_trade_id {unrecorded_trade_id}")
        
        if unrecorded_trade_id==[] and abs(sum_my_trades_instrument) > abs(size_from_position):
            difference= abs(sum_my_trades_instrument) - abs(size_from_position)
            log.error (f"difference {difference}")
            try:
                where_filter = f"trade_id"
                log.error (f"my_trades_instrument {my_trades_instrument}")
                get_transactions_with_the_same_amount_of_difference= ([o[where_filter] for o in my_trades_instrument if \
                    abs(o["amount"])==difference and "hedgingSpot-open" in o["label"]]) #"hedgingSpot-open": ensure sign consistency
                
                log.error (f"get_transactions_with_the_same_difference {get_transactions_with_the_same_amount_of_difference}")
                order_id= min(get_transactions_with_the_same_amount_of_difference)
                log.error (f"order_id {order_id}")
                
                await deleting_row(
                        "my_trades_all_json",
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        order_id,
                    )
            except:
                log.critical ("need manual intervention")

    
def get_transactions_with_closed_label(transactions_all: list) -> list:
    """ """

    #log.error (f"transactions_all {transactions_all}")
    return [] if(transactions_all == None or transactions_all == []) \
        else [o for o in transactions_all if "closed" in o["label"]]

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

    where_filter = f"order_id"
    column_list: str= "instrument_name","label", "amount", where_filter, "trade_id"
    tabel= "my_trades_all_json"
    transactions_all: list = await executing_query_based_on_currency_or_instrument_and_strategy(tabel, 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column_list)                                       

    transaction_with_closed_labels = get_transactions_with_closed_label(
        transactions_all
    )
    
    log.error (f"transaction_with_closed_labels {transaction_with_closed_labels}")

    for transaction in transaction_with_closed_labels:
        

        size_to_close = await summing_transactions_under_label_int(
            transaction, transactions_all
        )
        log.error (f"size_to_close {size_to_close}")

        if size_to_close == 0:

            label = get_transaction_label(transaction)

            label_integer = get_label_integer(label)["int"]
            
            transactions_with_zero_sum = [
                o for o in transactions_all if label_integer in o["label"]
            ]
            
            log.error (f"""transactions_with_zero_sum {transactions_with_zero_sum}""")
            
            for transaction in transactions_with_zero_sum:
        
                order_id = transaction[where_filter]
                
                closed_table="my_trades_closed_json"      
                
                from_sqlite_closed= await executing_query_based_on_currency_or_instrument_and_strategy(closed_table, 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column_list)   
                id_has_registered_before= [o for o in from_sqlite_closed if o[where_filter] == order_id]      
                
                log.warning (f"""transactions_with_zero_sum {transaction["label"]} {order_id}""")
                log.warning (f"""id_has_registered_before {id_has_registered_before} {id_has_registered_before==[]}""")

                if id_has_registered_before==[]:
                    await insert_tables(closed_table, transaction)
                    
                    await deleting_row(
                        tabel,
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
