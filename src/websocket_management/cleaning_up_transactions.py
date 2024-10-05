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
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables,
    deleting_row,
    executing_query_with_return,
    querying_arithmetic_operator,
    querying_duplicated_transactions)

from strategies.config_strategies import paramaters_to_balancing_transactions
# user defined formula

from utilities.system_tools import (
    sleep_and_restart,)
from utilities.string_modification import (
    get_unique_elements, 
    remove_dict_elements,
    extract_integers_from_text)
from strategies.basic_strategy import (
    get_additional_params_for_open_label,
    get_additional_params_for_futureSpread_transactions,
    get_transaction_label,
    check_db_consistencies,
    get_label_integer,
    provide_side_to_close_transaction
)
from strategies.config_strategies import max_rows

async def get_unrecorded_trade_and_order_id(instrument_name: str, from_exchange: list) -> dict:
        
    balancing_params=paramaters_to_balancing_transactions()
        
    max_closed_transactions_downloaded_from_sqlite=balancing_params["max_closed_transactions_downloaded_from_sqlite"]   
    
    column_list: str="order_id", "trade_id"
    
    from_sqlite_open= await get_query("my_trades_all_json", 
                                      instrument_name, 
                                      "all", 
                                      "all", 
                                      column_list)                                       

    from_sqlite_closed = await get_query("my_trades_closed_json", 
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

    #from_exchange_with_labels= [o for o in from_exchange if "label" in o]
    
    from_exchange_instrument: int = ([] if from_exchange == [] else ([o for o in from_exchange \
        if o["instrument_name"]==instrument_name])
                                            )
    #log.info (f"from_exchange_instrument {from_exchange_instrument}")
    from_exchange_order_id = [o["order_id"] for o in from_exchange_instrument]
    from_exchange_trade_id = [o["trade_id"] for o in from_exchange_instrument]
    
    combined_order_closed_open = from_sqlite_open_order_id + from_sqlite_closed_order_id
    combined_trade_closed_open = from_sqlite_open_trade_id + from_sqlite_closed_trade_id
    #log.warning (f"combined_order_closed_open {combined_order_closed_open}")

    #if "ETH" in instrument_name:
    #    log.warning (f"from_exchange_order_id {from_exchange_order_id}")
        #log.warning (f"from_exchange_trade_id {from_exchange_trade_id}")
        
    #    log.debug (f"from_exchange {from_exchange}")
    
    unrecorded_order_id = get_unique_elements(from_exchange_order_id, combined_order_closed_open)
    unrecorded_trade_id = get_unique_elements(from_exchange_trade_id, combined_trade_closed_open)
    
    log.debug (f"unrecorded_order_id {unrecorded_order_id}")
    log.error (f"unrecorded_trade_id {unrecorded_trade_id}")

    return dict(unrecorded_order_id=unrecorded_order_id,
                unrecorded_trade_id=unrecorded_trade_id)


def check_if_label_open_still_in_active_transaction (from_sqlite_open: list, instrument_name: str, label: str) -> bool:
    """_summary_
    
    concern: there are highly possibities of one label for multiple instruments for transactions under future spread. 
    Hence, the testing should be specified for an instrument

    Args:
        from_sqlite_open (list): _description_
        instrument_name (str): _description_
        label (str): _description_

    Returns:
        bool: _description_
    """
    integer_label= extract_integers_from_text(label)
    
    log.warning (f"from_sqlite_open {from_sqlite_open}")
    log.info (f"integer_label {integer_label}")
    
    trades_from_sqlite_open = [o for o in from_sqlite_open \
        if integer_label == extract_integers_from_text(o["label"]) \
            and "open" in o["label"] \
                and instrument_name == o["instrument_name"] ] 
    
    log.debug (f"trades_from_sqlite_open {trades_from_sqlite_open}")
    
    if trades_from_sqlite_open !=[]:

        # get sum of open label only
        sum_from_open_label_only= sum([o["amount"] for o in trades_from_sqlite_open])
        log.warning (f"sum_from_open_label_only {sum_from_open_label_only}")
        
        # get net sum of label
        sum_net_trades_from_open_and_closed= sum([o["amount"] for o in from_sqlite_open\
            if integer_label == extract_integers_from_text(o["label"]) \
                and instrument_name == o["instrument_name"]])
        
        log.warning (f"sum_net_trades_from_open_and_closed {sum_net_trades_from_open_and_closed}")
        
        sum_label = sum_from_open_label_only >= sum_net_trades_from_open_and_closed
        log.warning (f"sum_label {sum_label}")
        
    return False if trades_from_sqlite_open==[] else sum_label


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
    
    marker_plus=marker,"label","amount","instrument_name"

    for tran_id in unrecorded_id:
        
        #log.info (f"trades_from_exchange {trades_from_exchange}")

        transaction = [o for o in trades_from_exchange if o[marker] == tran_id]
        instrument_name= transaction[0] ["instrument_name"]
        #column_list: str="order_id", "trade_id"
        from_sqlite_open= await get_query(table, 
                                          instrument_name, 
                                          "all",
                                          "all",
                                          marker_plus)
        id_has_registered_before= [o for o in from_sqlite_open if o[marker] == tran_id]      
        
        log.error (f"transaction {instrument_name} {transaction} {tran_id}")
        
        if transaction !=[] and id_has_registered_before==[]:
        
            #combo get priority to avoid only one instrument is recorded
            if "combo_id" in transaction[0]:
                combo_id = [o["combo_trade_id"] for o in trades_from_exchange if o[marker] == tran_id][0]
                log.error (f"combo_id {combo_id}")
                trades_from_exchange_with_futures_combo= [ o for o in trades_from_exchange if "combo_id"  in o]
                log.warning (f"trades_from_exchange_with_futures_combo {trades_from_exchange_with_futures_combo}")
                transactions = [o for o in trades_from_exchange_with_futures_combo if o["combo_trade_id"]  == combo_id]
                log.error (f"transactions {transactions}")
                
                for transaction in transactions:
                    await get_additional_params_for_futureSpread_transactions(transaction)
                    await insert_tables(table, transaction)
                
                await sleep_and_restart()

        
            label = get_label_from_respected_id (trades_from_exchange, tran_id, marker)
            log.warning (f""""label {label}""")
            
            if "closed" in label:
                label_open_still_in_active_transaction= check_if_label_open_still_in_active_transaction (from_sqlite_open, instrument_name, label)
                
                if label_open_still_in_active_transaction ==False:
                    log.critical ("need manual intervention")
                    await sleep_and_restart()
                        
            if "label" not in transaction[0]:
                
                if "combo_id" in transaction[0]:
                    await get_additional_params_for_futureSpread_transactions(transaction)
            
                else:
                    label=None
                    await get_additional_params_for_open_label(transaction, label)
            
            if "open" in label:
                await get_additional_params_for_open_label(transaction, label)
                
                
            await insert_tables(table, transaction)
            await sleep_and_restart()

async def clean_up_closed_futures_because_has_delivered (instrument_name, transaction, delivered_transaction):
    
    log.warning (f"instrument_name {instrument_name}")
    log.warning (f"transaction {transaction}")
    try:
        trade_id_sqlite= int(transaction["trade_id"])
    
    except:
        trade_id_sqlite= (transaction["trade_id"])
    
    timestamp= transaction["timestamp"]
    
    closed_label=f"futureSpread-closed-{timestamp}"
    
    transaction.update({"instrument_name":instrument_name})
    transaction.update({"timestamp":timestamp})
    transaction.update({"price":transaction["price"]})
    transaction.update({"amount":transaction["amount"]})
    transaction.update({"label":transaction["label"]})
    transaction.update({"trade_id":trade_id_sqlite})
    transaction.update({"order_id":transaction["order_id"]})

    #log.warning (f"transaction {transaction}")
    await insert_tables("my_trades_closed_json", transaction)
    
    await deleting_row("my_trades_all_json",
                    "databases/trading.sqlite3",
                    "trade_id",
                    "=",
                    trade_id_sqlite,
                )

    delivered_transaction= delivered_transaction[0]
    
    timestamp_from_transaction_log= delivered_transaction["timestamp"] 

    try:
        price_from_transaction_log= delivered_transaction["price"] 
    
    except:
        price_from_transaction_log= delivered_transaction["index_price"] 
        
    closing_transaction= transaction
    closing_transaction.update({"label":closed_label})
    closing_transaction.update({"amount":(closing_transaction["amount"])*-1})
    closing_transaction.update({"price":price_from_transaction_log})
    closing_transaction.update({"trade_id":None})
    closing_transaction.update({"order_id":None})
    closing_transaction.update({"timestamp":timestamp_from_transaction_log})

    await insert_tables("my_trades_closed_json", closing_transaction)


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
                                                trades_from_exchange: list, 
                                                positions_from_sub_accounts: list,
                                                order_from_sqlite_open,
                                                open_orders_from_sub_accounts) -> None:
    """ """
    
    unrecorded_transactions= await get_unrecorded_trade_and_order_id(instrument_name,
                                  trades_from_exchange)
    
    unrecorded_order_id= unrecorded_transactions["unrecorded_order_id"]
    unrecorded_trade_id= unrecorded_transactions["unrecorded_trade_id"]
           
    if unrecorded_order_id != None:
        await update_db_with_unrecorded_data (trades_from_exchange, unrecorded_order_id, "order_id")

    if unrecorded_trade_id != None:
        await update_db_with_unrecorded_data (trades_from_exchange, unrecorded_trade_id, "trade_id")
    
    await remove_duplicated_elements ()
        
    column_list: str= "instrument_name","label", "amount", "price","trade_id"
    
    my_trades_instrument: list= await get_query(
                                                "my_trades_all_json", instrument_name, "all", "all", column_list)
    
    sum_my_trades_instrument = sum([o["amount"] for o in my_trades_instrument])
    
    await recheck_result_after_cleaning (instrument_name,
                                         trades_from_exchange,
                                         my_trades_instrument,
                                         sum_my_trades_instrument,
                                         positions_from_sub_accounts,
                                         order_from_sqlite_open,
                                         open_orders_from_sub_accounts)
    
async def recheck_result_after_cleaning  (instrument_name: str,
                                          trades_from_exchange: list,
                                          my_trades_instrument: list,
                                          sum_my_trades_instrument: float,
                                          positions_from_sub_accounts: list,
                                          order_from_sqlite_open: list,
                                          open_orders_from_sub_accounts: list) -> list:
    """ """
    
    db_consistencies= check_db_consistencies (instrument_name, 
                                              my_trades_instrument, 
                                              positions_from_sub_accounts,
                                              order_from_sqlite_open,
                                              open_orders_from_sub_accounts)
     
    size_is_consistent= db_consistencies["trade_size_is_consistent"]
    
    if not size_is_consistent:

        unrecorded_transactions= await get_unrecorded_trade_and_order_id(instrument_name,
                                    trades_from_exchange)
        
        unrecorded_trade_id= unrecorded_transactions["unrecorded_trade_id"]
        
        log.error (f"unrecorded_trade_id {unrecorded_trade_id}")
        
        size_from_position: int = (0 if positions_from_sub_accounts == [] \
        else sum([o["size"] for o in positions_from_sub_accounts if o["instrument_name"]==instrument_name]))
        
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
    return [] if(transactions_all is None or transactions_all == []) \
        else [o for o in transactions_all if "closed" in o["label"]]

def transactions_under_label_int(label_integer: int, transactions_all: list) -> str:
    """ """
    
    transactions = [o for o in transactions_all if label_integer in o["label"]]
    
    return dict(closed_transactions= transactions,
                summing_closed_transaction= sum([ o["amount"] for o in transactions]))

def get_closed_open_transactions_under_same_label_int(
    transactions_all: list, label: str
) -> list:
    """ """
    label_integer = get_label_integer(label)

    return [o for o in transactions_all if label_integer in o["label"]]

async def clean_up_closed_transactions(instrument_name, trade_table) -> None:
    """
    closed transactions: buy and sell in the same label id = 0. When flagged:
    1. remove them from db for open transactions/my_trades_all_json
    2. delete them from active trade db
    """

    #prepare basic parameters for table query

    log.error (f" clean_up_closed_transactions {instrument_name} START")
    
    where_filter = f"trade_id"

    column_list: str= "instrument_name","label", "amount", where_filter
    
    #querying tables
    transactions_all: list = await get_query(trade_table, 
                                             instrument_name, 
                                             "all",     
                                             "all", 
                                             column_list,)                                       

    # filtered transactions with closing labels
    transaction_with_closed_labels = get_transactions_with_closed_label (transactions_all)

    log.error (f"closing transactions {transaction_with_closed_labels}")

    if transaction_with_closed_labels:

        for transaction in transaction_with_closed_labels:
            
            label = get_transaction_label(transaction)

            label_integer = get_label_integer(label)
            
            closed_transactions_all= transactions_under_label_int (label_integer, transactions_all)

            size_to_close = closed_transactions_all["summing_closed_transaction"]

            log.error (f"closed_transactions_all {closed_transactions_all}")

            if size_to_close == 0:
                
                transactions_with_zero_sum = closed_transactions_all["closed_transactions"]
                            
                for transaction in transactions_with_zero_sum:
            
                    trade_id = transaction[where_filter]

                    await deleting_row(
                        trade_table,
                        "databases/trading.sqlite3",
                        where_filter,
                        "=",
                        trade_id,
                    )
                    
    log.error (f" clean_up_closed_transactions {instrument_name} DONE")


async def count_and_delete_ohlc_rows():

    log.info("count_and_delete_ohlc_rows-START")
    tables = ["market_analytics_json", 
              "supporting_items_json",
              "ohlc1_eth_perp_json", 
              "ohlc1_btc_perp_json", 
              "ohlc15_eth_perp_json", 
              "ohlc15_btc_perp_json", 
              "ohlc30_eth_perp_json", 
              "ohlc60_eth_perp_json",
              "ohlc3_eth_perp_json", 
              "ohlc3_btc_perp_json", 
              "ohlc5_eth_perp_json", 
              "ohlc5_btc_perp_json",  
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
                first_tick = first_tick_fr_sqlite[0]["MIN (id)"]

            #log. error(f"table {table} where_filter {where_filter} first_tick_fr_sqlite {first_tick_fr_sqlite}")
            await deleting_row(table, database, where_filter, "=", first_tick)
            
    log.info("count_and_delete_ohlc_rows-DONE")
