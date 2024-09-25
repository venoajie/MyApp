# -*- coding: utf-8 -*-

# installed
from loguru import logger as log

# user defined formula
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy,
    insert_tables)
from websocket_management.ws_management import update_status_data
from utilities.string_modification import extract_currency_from_text

def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

async def updating_current_order (table_open_orders, data_column, filter, order_id, order_state, new_order) -> None:
    
    """_summary_
    
    order has existed before


    """

    if (
        order_state == "cancelled"
        or order_state == "filled"
        or order_state == "triggered"
    ):
        
        await update_status_data(table_open_orders, data_column, filter, order_id, order_state)
        
        if order_state == "filled":
            
            order_state == "trade_id"
            
            await update_status_data(table_open_orders, data_column, filter, order_id, order_state)
        

async def manage_orders(order: dict) -> None:

    columns= "order_id", "label"
    instrument_name = order["instrument_name"]
    currency=extract_currency_from_text(instrument_name).upper()

    # get the order state
    table_open_orders= "orders_all_json"
    order_state = order["order_state"]
    order_id = order["order_id"]
    data_column = "order_id"
    
    await updating_current_order(table_open_orders, data_column, filter, order_id, order_state, new_order)


    if (
        order_state == "open"
        or order_state == "untriggered"
        or order_state == "triggered"
    ):

        await insert_tables("orders_all_json", order)
        log.critical(f" save order to db")
        log.warning(f" {order}")
