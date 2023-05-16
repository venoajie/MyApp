# # -*- coding: utf-8 -*-

""" 
If market move violently to one side in a short time (say 5% under 5 minutes), 
    some strategies, especially those rely on "delta neutral position" (such as grid based trading), 
        could be severely impacted/adverse position for sometimes
This module is balancing the negative impact of the respective movement above until it corrected itself.

Why not use logic from hedging spot?
- hedging, although also rely on delta neutral/spot=short position, 
    but has different objectives: maintain value vs profit
- both strategies expected to be more complex in the future, an dthus, could be very different at the end
"""

# built ins
import asyncio

# user defined formula
from strategies import hedging_spot
from db_management import sqlite_management
from loguru import logger as log

def get_basic_opening_paramaters() -> dict:
    """
    Initiate basic/fixedparameters for opening order. 
    Will be combined further with more dynamic/market paramaters

    Args:
        None

    Returns:
        dict

    """
    
    #provide placeholder for params
    params= {}
    
    # default type: limit
    params.update({"type": 'limit'})
            
    return params

async def querying_label_and_size(table) -> dict:
    """
    Provide template for querying summary of trading results from sqlite.
    Consist of transaction label, size, and price only.
    """
    
    # get query
    query =  sqlite_management.querying_label_and_size (table) 
    
    # execute query
    result = await sqlite_management.executing_query_with_return (query) 
    
    # define none from queries result. If the result=None, return []
    NONE_DATA: None = [0, None, []]
    
    return  [] if result in NONE_DATA  else (result)

def get_balancing_transactions(transaction_summary_from_sqlite: list, relevant_label: list= ['basicGrid']) -> dict:
    """
    Get transactions with label that considered as part of delta neutral strategy
    - basicGrid
    """
    
    balancing_transactions=   [o for o in transaction_summary_from_sqlite if (
        [r for r in relevant_label if r in o['label_main']]
        )
                               ]
    
    return  dict(
        balancing_all = balancing_transactions,
        balancing_sum = 0 if balancing_transactions in  [] else sum([o['amount_dir'] for o in balancing_transactions]),
        balancing_len = 0 if balancing_transactions ==  [] else len([o  for o in balancing_transactions])
                )

def get_size(balancing_open_trade_sum, 
             balancing_sum_open_order, 
             sum_next_open_order) -> int:
    """ """
        
    return max(1, 
               int((balancing_open_trade_sum + balancing_sum_open_order + sum_next_open_order))
               )

async def get_proforma_attributes (sum_next_open_order: int= 0, relevant_label: list= ['basicGrid']) -> dict:
    """ """

    # get current size
    open_trade_label_and_size= await querying_label_and_size('my_trades_all_json')
    open_trade_balancing= get_balancing_transactions(open_trade_label_and_size, 
                                                     relevant_label
                                                     )
    
    balancing_open_trade_sum= open_trade_balancing['balancing_sum']
    
    # get open orders
    open_orders_label_and_size_current= await querying_label_and_size('orders_all_json')
    open_orders_balancing= get_balancing_transactions(open_orders_label_and_size_current, 
                                                      relevant_label
                                                      ) 
    return dict(
        open_trade_attributes=  open_trade_label_and_size,
        balancing_open_trade_len=   open_trade_balancing['balancing_len'],
        balancing_open_trade_sum=   balancing_open_trade_sum,
        balancing_open_order_len=   open_orders_balancing['balancing_len'],
        order_size= get_size (balancing_open_trade_sum,
                              open_orders_balancing['balancing_sum'], 
                              sum_next_open_order
                              )
    )
    
async def is_send_open_order_allowed (ask_price: float,
                                      bid_price: float,
                                      sum_next_open_order
                                      ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    # get proforma attributes (transactions, size, len, etc)
    proforma = await get_proforma_attributes(sum_next_open_order)

    # check conditions for sending order
    order_allowed=  proforma['balancing_open_order_len']== 0
    
    if order_allowed:
        
        # get basic order parameters
        params= get_basic_opening_paramaters()
        
        # get transaction label and update the respective parameters
        label_open = hedging_spot.get_label ('open', 'balancing') 
        params.update({"label": label_open})
        
        params.update({"size": abs(proforma['order_size'])})
        
        if proforma['order_size']>0:
            params.update({"entry_price": ask_price})
            params.update({"side": "sell"})
            
        if proforma['order_size']<0:
            params.update({"entry_price": bid_price})
            params.update({"side": "buy"})
        log.warning (params)
        
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
    
async def is_send_exit_order_allowed (ask_price: float,
                                      bid_price: float
                                      ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    proforma = await get_proforma_attributes()
    log.debug (proforma)
    
    only_one_open_order= proforma['balancing_open_order_len']== 0
    there_was_open_trade_with_balancing_label= proforma['balancing_open_trade_len']!= 0
    the_imbalance_before_has_neutralized= proforma['order_size'] !=0

    order_allowed=  only_one_open_order\
        and there_was_open_trade_with_balancing_label   \
            and the_imbalance_before_has_neutralized
        
    # transform to dict
    transaction= proforma['open_trade_attributes']
        
    if order_allowed:
        # get price
        last_transaction_price= transaction['price']
        
        transaction_side= transaction['direction']
        
        params.update({"instrument":  transaction['instrument_name']})

        # get transaction parameters
        params= hedging_spot.get_basic_closing_paramaters(transaction)
        
        if transaction_side=='sell':
            params.update({"entry_price": bid_price})
            if bid_price > last_transaction_price:
                order_allowed= False
            
        if transaction_side=='buy':
            params.update({"entry_price": ask_price})
            params['side']='sell'
            if ask_price < last_transaction_price:
                order_allowed= False
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
    
def reading_from_db(end_point, instrument: str = None, status: str = None
) -> float:
    """ """
    from utilities import pickling, system_tools
    return pickling.read_data(
        system_tools.provide_path_for_file(end_point, instrument, status)
    )
        
async def send_order (currency, sum_next_open_order):
    
    instrument = [f"{currency.upper()}-PERPETUAL"]
    ticker: list =  reading_from_db("ticker", instrument)

    if ticker !=[]:

        # get bid and ask price
        best_bid_prc: float = ticker[0]["best_bid_price"]
        best_ask_prc: float = ticker[0]["best_ask_price"]
        
        exit= await is_send_exit_order_allowed (best_ask_prc, 
                                    best_bid_prc)
        
        open= await is_send_open_order_allowed (best_ask_prc, 
                                                best_bid_prc, 
                                                sum_next_open_order)
        
    return dict(exit= exit,
                open= open)