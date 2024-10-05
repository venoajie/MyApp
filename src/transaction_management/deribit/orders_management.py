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
    
def labelling_unlabelled_transaction(order: dict) -> None:

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
            
            trade_id= str(trade["trade_id"])
            
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
                    
            #get table names
            trade_table = self.trade_db_table
            archived_table =self.archive_db_table
            
            if not data_from_db_trade_open:
                
                trade_id_has_exist_before = False
                
            if  data_from_db_trade_open:

                trade_id_has_exist_before=  check_if_id_has_used_before (data_from_db_trade_open, 
                                                                        "trade_id", 
                                                                        trade_id)
            
            #processing clean result
            if not trade_id_has_exist_before:
                # check if transaction has additional attributes. If no, provide it with them
                if "open" in label:
                    await get_additional_params_for_open_label (trade, label)

                # insert clean trading transaction
                log.info (f"label {label}")
                log.info (f"trade {trade}")
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
            
            original=  {'jsonrpc': '2.0', 'id': 1002, 'result': {'trades': [], 'order': {'is_liquidation': False, 'risk_reducing': False, 'order_type': 'limit', 'creation_timestamp': 1728090482863, 'order_state': 'open', 'reject_post_only': False, 'contracts': 5.0, 'average_price': 0.0, 'reduce_only': False, 'last_update_timestamp': 1728090482863, 'filled_amount': 0.0, 'post_only': True, 'replaced': False, 'mmp': False, 'order_id': 'ETH-49960097702', 'web': False, 'api': True, 'instrument_name': 'ETH-PERPETUAL', 'max_show': 5.0, 'time_in_force': 'good_til_cancelled', 'direction': 'sell', 'amount': 5.0, 'price': 2424.05, 'label': 'hedgingSpot-open-1728090482812'}}, 'usIn': 1728090482862653, 'usOut': 1728090482864640, 'usDiff': 1987, 'testnet': False}
            cancelled=  {'jsonrpc': '2.0', 'id': 1002, 'result': {'is_liquidation': False, 'risk_reducing': False, 'order_type': 'limit', 'creation_timestamp': 1728090482863, 'order_state': 'cancelled', 'reject_post_only': False, 'contracts': 5.0, 'average_price': 0.0, 'reduce_only': False, 'last_update_timestamp': 1728090483773, 'filled_amount': 0.0, 'post_only': True, 'replaced': False, 'mmp': False, 'cancel_reason': 'user_request', 'order_id': 'ETH-49960097702', 'web': False, 'api': True, 'instrument_name': 'ETH-PERPETUAL', 'max_show': 5.0, 'time_in_force': 'good_til_cancelled', 'direction': 'sell', 'amount': 5.0, 'price': 2424.05, 'label': 'hedgingSpot-open-1728090482812'}, 'usIn': 1728090483773107, 'usOut': 1728090483774372, 'usDiff': 1265, 'testnet': False}
            
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