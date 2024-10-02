# -*- coding: utf-8 -*-

# installed
from loguru import logger as log
from dataclassy import dataclass

# user defined formula
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    deleting_row,
    update_status_data,
    insert_tables)
from strategies.basic_strategy import (
    get_transaction_side,        
    get_additional_params_for_open_label,
    get_additional_params_for_futureSpread_transactions,
    check_if_id_has_used_before)
from websocket_management.cleaning_up_transactions import (
    clean_up_closed_transactions,
    check_if_transaction_has_closed_label_before)
from utilities.string_modification import (
    extract_currency_from_text)

def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

async def convert_status_has_closed_label_from_no_to_yes (instrument_name, 
                                                          trade_table, 
                                                          filter_trade, 
                                                          trade_id) -> None:

    column_list= "trade_id","has_closed_label"
    
    transactions_all: list = await get_query(trade_table, instrument_name, "all", "all", column_list)
    
    has_closed_label = check_if_transaction_has_closed_label_before (transactions_all, trade_id)
    
    if not has_closed_label or has_closed_label==0:
        
        new_value=True
        data_column= "has_closed_label"
        table= trade_table
        await update_status_data(table, 
                                 data_column, 
                                 filter_trade, 
                                 trade_id, 
                                 new_value)

    
def get_custom_label(transaction: list) -> str:

    side= transaction["direction"]
    side_label= "Short" if side== "sell" else "Long"
    
    try:
        last_update= transaction["timestamp"]
    except:
        last_update= transaction["timestamp"]
    
    return (f"custom{side_label.title()}-open-{last_update}")
    
def labelling_unlabelled_transaction(order) -> None:

    side= get_transaction_side(order)
    order.update({"everything_is_consistent": True})
    order.update({"order_allowed": True})
    order.update({"entry_price": order["price"]})
    order.update({"size": order["amount"]})
    order.update({"type": "limit"})
    order.update({"side": side})
    
    if "combo_id" in order:
        get_additional_params_for_futureSpread_transactions(order)
    else:        
        label_open: str = get_custom_label(order)
        order.update({"label": label_open})
    log.info (f"labelling_unlabelled_transaction {order}")
    
    return dict(order=order,
                label_open=label_open)

@dataclass(unsafe_hash=True, slots=True)
class OrderManagement:
    """ 

    there are 2 db's: all & currency
    all: record all active transaction
    currency: record all  transaction (especially used for integrity check) 
        
    """

    order_db_table: str
    trade_db_table: str
    archive_db_table: str

    async def saving_traded_orders (self, 
                                    trades) -> None:
        """_summary_

        Args:
            trades (_type_): _description_
            orders (_type_): _description_
        """
        
        for trade in trades:    
            instrument_name= trade ["instrument_name"]
            
            currency=extract_currency_from_text(instrument_name)
            
            trade_id= trade["trade_id"]
            
            try:
                label= trade["label"]
            except:
                label= get_custom_label(trade)
                trade.update({"label": label})
            
            if "combo_id" in trade:
                get_additional_params_for_futureSpread_transactions(trade)
                
            label=trade["label"]
            
            column_trade= "trade_id","label"
            
            data_from_db_trade_open = await get_query(f"my_trades_all_{currency}_json", 
                                                instrument_name, 
                                                "all", 
                                                "all", 
                                                column_trade)

            trade_id_has_exist_before=  check_if_id_has_used_before (data_from_db_trade_open, 
                                                                     "trade_id", 
                                                                     trade_id)
            #processing clean result
            if not trade_id_has_exist_before:
                    
                #get table names
                order_table = self.order_db_table
                trade_table = self.trade_db_table
                archived_table =self.archive_db_table
            
                # check if transaction has additional attributes. If no, provide it with them
                if "open" in label:
                    await get_additional_params_for_open_label (trade, label)

                # convert status parameter so transaction colud be further closed
                if "closed" in label:
                    
                    filter_trade="trade_id"
                    
                    await convert_status_has_closed_label_from_no_to_yes (instrument_name, 
                                                                          trade_table, 
                                                                          filter_trade,
                                                                          trade_id)
                    await convert_status_has_closed_label_from_no_to_yes (instrument_name, 
                                                                          archived_table, 
                                                                          filter_trade, 
                                                                          trade_id)

                # insert clean trading transaction
                await insert_tables(order_table, trade)
                await insert_tables(trade_table, trade)
                await insert_tables(archived_table, trade)
                
                # remove closed transaction from active db
                if "closed" in label:
                    await clean_up_closed_transactions (instrument_name, trade_table)


    async def saving_orders (self, 
                             order_table,
                             order,
                             order_state) -> None:
        """_summary_

        Args:
            trades (_type_): _description_
            orders (_type_): _description_
        """

        filter_trade="order_id"

        order_id = order["order_id"]
        
        if order_state == "cancelled":

            await deleting_row ("orders_all_json",
                                "databases/trading.sqlite3",
                                filter_trade,
                                "=",
                                order_id,
                            )
            #await update_status_data(order_table, 
            #                     "order_state", 
            #                     filter_trade, 
            #                     order_id, 
            #                     "cancelled")

        if order_state == "open":
            await insert_tables(order_table, order)