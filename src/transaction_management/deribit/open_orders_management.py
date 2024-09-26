# -*- coding: utf-8 -*-

# installed
from loguru import logger as log

# user defined formula
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables)
from websocket_management.ws_management import update_status_data
from utilities.string_modification import extract_currency_from_text

from strategies.basic_strategy import (
    is_everything_consistent,
    get_transaction_side,
    get_additional_params_for_futureSpread_transactions,
    check_if_id_has_used_before
)
from websocket_management.ws_management import (
    cancel_the_cancellables,
    procedures_for_unlabelled_orders,
    )

def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

def labelling_unlabelled_order(order) -> None:

    side= get_transaction_side(order)
    order.update({"everything_is_consistent": True})
    order.update({"order_allowed": True})
    order.update({"entry_price": order["price"]})
    order.update({"size": order["amount"]})
    order.update({"type": "limit"})
    order.update({"side": side})
    side_label= "Short" if side== "sell" else "Long"
    last_update=order["creation_timestamp"]
    
    if "combo_id" in order:
        get_additional_params_for_futureSpread_transactions(order)
    else:        
        label_open: str = (f"custom{side_label.title()}-open-{last_update}")
        order.update({"label": label_open})
    log.info (f"order {order}")
    
    return dict(order=order,
                label_open=label_open)

async def insert_new_order (instrument_name, table_open_orders, data_column, filter, order_id, order_state, new_order) -> None:
    
    """_summary_
    
    order has existed before


    """



    if (
        order_state == "open"
        or order_state == "untriggered"
        or order_state == "triggered"
    ):

        await insert_tables("orders_all_json", new_order)
        log.critical(f" save order to db")
        log.warning(f" {new_order}")


async def updating_current_order (instrument_name, from_sqlite_orders, data_column, filter, order_id, order_state, new_order) -> None:
    
    """_summary_
    
    order has existed before


    """

    if (
        order_state == "cancelled"
        or order_state == "filled"
        or order_state == "triggered"
    ):
        
        await update_status_data(from_sqlite_orders, data_column, filter, order_id, order_state)
        
        if order_state == "filled":
            
            column_list: str="label", "trade_id"
            
                                                   

            
            trade_id = new_order["trade_id"]
            
            order_id_has_recorded_before= [o for o in from_sqlite_orders if trade_id in o["trade_id"]]
            
            if order_id_has_recorded_before ==[]:
                
                if "label" not in new_order:
                    new_order.update({"label": label_log[0]})
            
            await update_status_data(table_open_orders, data_column, filter, order_id, order_state)
        

async def manage_orders(orders: list) -> None:


    log.error (f"orders {orders}")
    
    for order in orders:

        #label=order["label"]
                    
        instrument_name=order["instrument_name"]
        
        log.debug (order)
        log.error (order["label"]=="" )
        order_id=order["order_id"]
        label=order["label"]
        
        if  label =="" :                
            
            await procedures_for_unlabelled_orders(order, instrument_name)

        else:

            label_has_exist_before= await check_if_id_has_used_before (instrument_name,"order_id",order_id, 100)
            
            await manage_orders (order)            

            if label_has_exist_before:
                await cancel_the_cancellables()

        everything_consistent= is_everything_consistent(order)
        log.critical (f' ORDERS everything_consistent {everything_consistent} everything_NOT_consistent {not everything_consistent}')
        
        if  not everything_consistent:
            await cancel_the_cancellables()
            await telegram_bot_sendtext('size or open order is inconsistent', "general_error")

    column_list= "order_id", "label"
    instrument_name = order["instrument_name"]
    currency=extract_currency_from_text(instrument_name).upper()

    # get the order state
    table_open_orders= "orders_all_json"
    order_state = order["order_state"]
    order_id = order["order_id"]
    data_column = "order_id"
    
    from_sqlite_orders= await get_query (table_open_orders, 
                                         instrument_name, 
                                                    "all", 
                                                    "all", 
                                                    column_list)
    
    await updating_current_order(instrument_name, from_sqlite_orders, data_column, filter, order_id, order_state, new_order)
