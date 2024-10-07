# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import *
from loguru import logger as log

# user defined formula

from deribit_get import get_tickers
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables,
    deleting_row,)
from strategies.basic_strategy import (
    BasicStrategy, 
    get_basic_closing_paramaters,
    are_size_and_order_appropriate)


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
                        
                        basic_closing_paramaters= get_basic_closing_paramaters (transaction)  
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
    ticker: list
    ask_price: float= fields (init=False)

    def __post_init__(self):
        self.ask_price = self.ticker ["best_ask_price"]
        print (f"self.ask_price {self.ask_price}")

    async def is_send_exit_order_allowed(
        self,
        TA_result_data,
        index_price: float,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
        server_time: int
    ) -> dict:
        """ """
        
        market_condition = await get_market_condition_hedging(currency,
            TA_result_data, index_price, threshold_market_condition
        )

        exit_params: dict = await self.get_basic_params().is_send_exit_order_allowed(
            market_condition, 
            ask_price, 
            bid_price, 
            selected_transaction,
        )
        
        cancel_allowed: bool = False
        cancel_id: str = None
        
        open_orders_label_strategy: list=  await get_query("orders_all_json", 
                                                           currency.upper(), 
                                                           self.strategy_label,
                                                           "closed")
        
        len_orders: int = get_transactions_len(open_orders_label_strategy)
        
        if len_orders != [] and len_orders > 0:
            
            log.error (f"order_parameters {exit_params}")
            log.debug (f"cancel_allowed {cancel_allowed}")
            
            #cancel_allowed: bool = True
            cancel_id= min ([o["order_id"] for o in open_orders_label_strategy])
            
            log.error (f"exit_params {exit_params}")
    
            waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"]

            cancel_allowed: bool = is_cancelling_order_allowed(
                strong_bullish,
                bearish,
                waiting_minute_before_cancel,
                len_orders,
                open_orders_label_strategy,
                server_time,
            )
            
        order_allowed = exit_params["order_allowed"]
        
        exit_allowed = False
        
        if order_allowed:
        
            my_trades_currency_strategy: list= await get_query("my_trades_all_json", currency.upper(), self.strategy_label)

            sum_my_trades: int = sum([o["amount"] for o in my_trades_currency_strategy ])    
            
            size = exit_params["size"] * ensure_sign_consistency (exit_params["side"])           
            
            sum_orders: int = get_transactions_sum(open_orders_label_strategy)
            
            size_and_order_appropriate_for_ordering: bool = (
                are_size_and_order_appropriate (
                    "reduce_position",
                    sum_my_trades, 
                    sum_orders, 
                    size, 
                )
            )
                
            #convert size to positive sign
            exit_params.update({"size": abs (size)})
            
            exit_allowed: bool = size_and_order_appropriate_for_ordering \
                 and (bullish or strong_bullish)

        return dict(
            order_allowed=exit_allowed,
            order_parameters=(
                [] if exit_allowed == False else exit_params["order_parameters"]
            ),
            cancel_allowed=cancel_allowed,
            cancel_id=cancel_id
        )
