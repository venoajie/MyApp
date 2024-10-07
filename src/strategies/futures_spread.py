# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass, fields
from loguru import logger as log

# user defined formula

from deribit_get import get_tickers
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables,
    deleting_row,)

from strategies.basic_strategy import (
    BasicStrategy,
    are_size_and_order_appropriate,
    delta_pct,
    ensure_sign_consistency,
    get_max_time_stamp,
    get_order_id_max_time_stamp,
    is_label_and_side_consistent,
    is_minimum_waiting_time_has_passed,
    size_rounding,)

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


@dataclass(unsafe_hash=True, slots=True)
class FutureSpreads(BasicStrategy):
    """ """
    sum_my_trades_currency_strategy: int
    notional: float
    ticker: list
    best_ask_price: float= fields 
    best_bid_price: float= fields 
    max_position: float= fields 
    over_hedged: bool= fields 

    def __post_init__(self):
        self.best_ask_price = self.ticker ["best_ask_price"]
        self.best_bid_price = self.ticker ["best_bid_price"]
        self.max_position = self.strategy_parameters["max_leverage"] * self.notional
        self.over_hedged = self.max_position > 0

    def get_basic_params(self) -> dict:
        """ """
        return BasicStrategy(self.strategy_label, 
                             self.strategy_parameters)

    async def is_send_and_cancel_open_order_allowed (self,
                                                     orders_currency_strategy: list,
    ) -> dict:
        """ """

        ONE_SECOND,  ONE_MINUTE = 1000, 60000
                
        order_allowed, cancel_allowed, cancel_id = False, False, None
        
        max_open_orders = self.strategy_parameters ["sub_account_max_open_orders"] ["per_instrument"]
        
        log.warning (f" max_open_orders {max_open_orders}")
        
        open_orders_label_strategy: list=  [o for o in orders_currency_strategy if "open" in o["label"]]
        
        params: dict = self.get_basic_params().get_basic_opening_parameters(self.best_ask_price)
        
        len_orders: int = get_transactions_len(open_orders_label_strategy)
        
        hedging_attributes= self.strategy_parameters
      
        waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"] * ONE_MINUTE

        over_hedged  =  self.over_hedged
        
        log.warning (f" {params}")
        log.warning (f"sum_my_trades_currency_strategy {self.sum_my_trades_currency_strategy} over_hedged {self.over_hedged} max_position {self.max_position}")
        
        if len_orders == 0:
                    
            if not over_hedged:
            
                max_position = self.max_position

        return dict(
            order_allowed=order_allowed and len_orders == 0,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id= None if not cancel_allowed \
            else get_order_id_max_time_stamp(open_orders_label_strategy)
        )
