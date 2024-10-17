# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass, fields
from loguru import logger as log

# user defined formula


from transaction_management.deribit.api_requests import (
    get_tickers)
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    deleting_row,)
from utilities.pickling import (
    read_data,)
from utilities.system_tools import (
    provide_path_for_file,)
from strategies.basic_strategy import (
    BasicStrategy,
    are_size_and_order_appropriate,
    size_rounding,)


def reading_from_pkl_data(end_point, 
                          currency, 
                          status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, 
                                      currency, status)

    data = read_data(path)

    return data


def get_transactions_len(result_strategy_label) -> int:
    """ """
    return 0 if result_strategy_label == [] else len([o for o in result_strategy_label])

async def closing_unclosed_transactions_for_delivered_futures(instrument_name: str, 
                                                              trade_db_table,
                                                              my_trades_currency,
                                                              my_trades_instrument,
                                                              order_from_sqlite_open) -> list:
    """
    """

    if "PERPETUAL" not in instrument_name:
        time_stamp= [o["timestamp"] for o in my_trades_instrument]
        
        if time_stamp !=[]:
            
            last_time_stamp_sqlite= max(time_stamp)
            
            transaction_log_from_sqlite_open= await get_query("transaction_log_json", 
                                            instrument_name, 
                                            "all", 
                                            "all", 
                                            "standard")
            log.critical (f"transaction_log_from_sqlite_open {transaction_log_from_sqlite_open}")
            delivered_transaction= [o for o in transaction_log_from_sqlite_open if "delivery" in o["type"] ]
            delivery_timestamp= [o["timestamp"] for o in delivered_transaction ]
            delivery_timestamp= [] if delivery_timestamp==[] else max(delivery_timestamp)
            
            #log.warning (f"delivery_timestamp {delivery_timestamp} last_time_stamp_sqlite {last_time_stamp_sqlite} last_time_stamp_sqlite < delivery_timestamp {last_time_stamp_sqlite < delivery_timestamp}")
            
            if delivery_timestamp !=[] and last_time_stamp_sqlite < delivery_timestamp:
                    
                transactions_from_other_side= [ o for o in my_trades_currency \
                    if instrument_name not in o["instrument_name"]]
                                        
                column_data: str="trade_id","timestamp","amount","price","label","amount","order_id"
                
                my_trades_instrument_data: list= await get_query(trade_db_table, instrument_name, "all", "all", column_data)
                    
                for transaction in my_trades_instrument_data:
                    
                    label_int= parsing_label(transaction["label"])["int"]
                    #log.error (f"label_int {label_int}")
                    
                    transactions_from_other_side= [ o for o in my_trades_currency \
                    if instrument_name not in o["instrument_name"] and label_int in o["label"] ]
                    
                    orders_from_other_side= [ o["amount"] for o in order_from_sqlite_open \
                    if instrument_name not in o["instrument_name"] and label_int in o["label"] ]
                    
                    orders_from_other_side= 0 if orders_from_other_side == [] else sum(orders_from_other_side)
                    
                    sum_transactions_from_other_side= sum([o["amount"] for o in transactions_from_other_side])
                    
                    for transaction in transactions_from_other_side:
                        
                        log.debug (f"transaction {transaction}")                
                        
                        basic_closing_paramaters= BasicStrategy.get_basic_closing_paramaters (transaction)  
                        basic_closing_paramaters.update({"instrument":transaction["instrument_name"]})
                        tickers= await get_tickers (basic_closing_paramaters["instrument"])
                        
                        if basic_closing_paramaters["side"]=="sell":
                            entry_price=tickers["best_ask_price"]

                        if basic_closing_paramaters["side"]=="buy":
                            entry_price=tickers["best_bid_price"]
                            
                        basic_closing_paramaters.update({"entry_price":entry_price})
                        basic_closing_paramaters.update({"size":abs(basic_closing_paramaters["size"])})
                        
                        log.error (f"basic_closing_paramaters {basic_closing_paramaters}")
                        log.error (f"sum_transactions_from_other_side {sum_transactions_from_other_side}")
                        log.error (f"orders_from_other_side {orders_from_other_side}")
                        log.error (basic_closing_paramaters["size"])
                        size_and_order_appropriate = are_size_and_order_appropriate("reduce_position",
                                                                                    sum_transactions_from_other_side,
                                                                                    orders_from_other_side,
                                                                                    basic_closing_paramaters["size"])
                        
                        
                        log.error (f"size_and_order_appropriate {size_and_order_appropriate}")
                        if False and  size_and_order_appropriate:
                            await send_limit_order(basic_closing_paramaters)  
                        
                    #log.error (f"my_trades_instrument_data {transaction}")
                
                    
                    await delete_respective_closed_futures_from_trade_db (transaction, 
                                                                          trade_db_table)
        

async def delete_respective_closed_futures_from_trade_db (transaction, 
                                                         trade_db_table):
    
    try:
        trade_id_sqlite= int(transaction["trade_id"])
    
    except:
        trade_id_sqlite= (transaction["trade_id"])
    
    await deleting_row(trade_db_table,
                    "databases/trading.sqlite3",
                    "trade_id",
                    "=",
                    trade_id_sqlite,
                )
    
def determine_opening_size(instrument_name: str, 
                           active_combo_perp,
                           max_position: float,
                           max_open_orders: int,
                           ) -> int:
    """ """
    
    proposed_size= int(abs(max_position) )/max_open_orders
        
    return size_rounding(instrument_name, active_combo_perp, proposed_size) 


@dataclass(unsafe_hash=True, slots=True)
class FutureSpreads(BasicStrategy):
    """ """
    my_trades_currency_strategy: int

    #def __post_init__(self):
        
    def get_basic_params(self) -> dict:
        """ """
        return BasicStrategy(self.strategy_label, 
                             self.strategy_parameters)


    async def is_send_exit_order_allowed (self,
                                          ) -> dict:
        """
        Returns:
            dict: _description_
        """
        order_allowed, cancel_allowed, cancel_id = False, False, None
        my_trades_currency_strategy_open = [o for o in self.my_trades_currency_strategy if "open" in (o["label"])]
        my_trades_open_label = [o["label"] for o in my_trades_currency_strategy_open]
        log.warning (f"my_trades_currency_strategy_open {my_trades_currency_strategy_open}")
        log.info (f"my_trades_open_label {my_trades_open_label}")
        exit_params = {}
        for label in my_trades_open_label:
            
            log.info (f"label {label}")
            my_trades_label = [o for o in my_trades_currency_strategy_open if label in o["label"]]
            log.debug (f"my_trades_label {my_trades_label}")
            my_trades_label_sell_side = [o for o in my_trades_label if "sell" in o["side"]][0]
            my_trades_label_buy_side = [o for o in my_trades_label if "buy" in o["side"]][0]

            sell_side_instrument = my_trades_label_sell_side ["instrument_name"]
            buy_side_instrument = my_trades_label_buy_side ["instrument_name"]

            #get instrument traded price
            sell_side_trd_prc = my_trades_label_sell_side ["price"] * -1
            buy_side_trd_prc = my_trades_label_buy_side ["price"]   
            delta_price =  sell_side_trd_prc +   buy_side_trd_prc
            
            if delta_price < 0:
                #log.warning (f" sell_side_instrument {sell_side_instrument} buy_side_instrument {buy_side_instrument}")
                buy_side_ticker= reading_from_pkl_data("ticker",buy_side_instrument)[0]
                sell_side_ticker= reading_from_pkl_data("ticker",sell_side_instrument)[0]
                #log.warning (f" buy_side_ticker {buy_side_ticker} sell_side_ticker {sell_side_ticker}")
                
                sell_side_current_prc = sell_side_ticker["best_ask_price"] 
                buy_side_current_prc = buy_side_ticker["best_ask_price"] 

                #log.warning (f" sell_side_ticker {sell_side_ticker} sell_side_current_prc {sell_side_current_prc}")
                #log.error (f" buy_side_ticker {buy_side_ticker} buy_side_current_prc {buy_side_current_prc}")

        return dict(
            order_allowed= order_allowed,
            order_parameters=(
                [] if order_allowed == False else exit_params
            ),
            cancel_allowed=cancel_allowed,
            cancel_id=None if not cancel_allowed else cancel_id
        )