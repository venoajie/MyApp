# -*- coding: utf-8 -*-

# installed
from loguru import logger as log
from dataclassy import dataclass

# user defined formula
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    deleting_row,
    insert_tables)
from strategies.basic_strategy import (
    get_transaction_side,        
    get_additional_params_for_open_label,
    get_additional_params_for_futureSpread_transactions,
    check_if_id_has_used_before)
from websocket_management.cleaning_up_transactions import (
    clean_up_closed_transactions,)
from utilities.string_modification import (
    extract_currency_from_text)

def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)
    
    
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
            order_id= trade ["order_id"]
            amount= trade ["amount"]
            
            order_table = self.order_db_table
            order_trade= "order_id","id"
            data_from_db_order = await get_query(order_table, 
                                                instrument_name, 
                                                "all", 
                                                "all", 
                                                order_trade)
            order_id_has_exist_before=  [o["id"] for o in data_from_db_order if o["order_id"]== order_id \
                and ["amount"] == amount]
            
            if order_id_has_exist_before:
                id = order_id_has_exist_before[0]
                await deleting_row ("orders_all_json",
                                "databases/trading.sqlite3",
                                "id",
                                "=",
                                id,
                            )
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
            
            log.error (f"data_from_db_trade_open {data_from_db_trade_open}")
            log.error (f"trade {trade}")
                    
            #get table names
            trade_table = self.trade_db_table
            archived_table =self.archive_db_table
            
            if not data_from_db_trade_open:
                
                trade_id_has_exist_before = False
                
            if  data_from_db_trade_open:

                trade_id_has_exist_before=  check_if_id_has_used_before (data_from_db_trade_open, 
                                                                        "trade_id", 
                                                                        trade_id)
            
            log.error (f"trade_id_has_exist_before {trade_id_has_exist_before}")
            #processing clean result
            if not trade_id_has_exist_before:
                # check if transaction has additional attributes. If no, provide it with them
                if "open" in label:
                    await get_additional_params_for_open_label (trade, label)

                # insert clean trading transaction
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