# # -*- coding: utf-8 -*-

# built ins
import asyncio

# user defined formula
from strategies import hedging_spot
from db_management import sqlite_management
from loguru import logger as log

def get_basic_opening_paramaters() -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    #provide placeholder for params
    params= {}
    
    # default type: limit
    params.update({"type": 'limit'})
            
    return params

async def querying_label_and_size(table) -> dict:
    """ """
    
    NONE_DATA: None = [0, None, []]
    
    query =  sqlite_management.querying_label_and_size (table) 
    result = await sqlite_management.executing_query_with_return (query) 
    
    return  [] if result in NONE_DATA  else (result)

def filtering_transactions(transaction_summary_from_sqlite) -> dict:
    """ 
    3 types of transactions:
    - hedging
    - trading
    - balancing

    Args:

    Returns:
        dict
    
    
    """
    
    # get trading
    result = [] if transaction_summary_from_sqlite == [] \
        else [o for o in transaction_summary_from_sqlite if 'hedging' not in o['label_main']] 

    # get balancer
    result_balancer_only = [] if result == [] \
        else [o for o in result if 'balancing' in o['label_main']] 

    return  dict(
        all= [] if result in [] else (result),
        sum_non_hedging = 0 if result in  [] else sum([o['amount_dir'] for o in result]),
        balancing_only = result_balancer_only,
        len_balancing_only = 0 if result_balancer_only ==  [] else len([o  for o in result_balancer_only])
                )

def filter_filtering_transactions(label_and_size_open_trade) -> dict:
    """ """
    
    relevant_label= ['hedging' , 'basicGrid']

    return  [o for o in label_and_size_open_trade if ([r for r in relevant_label if r in o['label_main']])]

def get_size(sum_non_hedging_open_trade, 
             sum_non_hedging_open_order, 
             sum_next_open_order) -> dict:
    """ """
    
    return (sum_non_hedging_open_trade + sum_non_hedging_open_order + sum_next_open_order)

async def get_proforma_attributes (sum_next_open_order: int= 0) -> int:
    """ """

    # get current size
    label_and_size_open_trade= await querying_label_and_size('my_trades_all_json')
    non_hedging_open_trade= filtering_transactions(label_and_size_open_trade)
    sum_non_hedging_open_trade= non_hedging_open_trade['sum_non_hedging']
    
    # get open orders
    label_and_size_current_open_order= await querying_label_and_size('orders_all_json')
    non_hedging_open_orders= filtering_transactions(label_and_size_current_open_order) 
    
    proforma_size=   get_size (sum_non_hedging_open_trade, non_hedging_open_orders['sum_non_hedging'], sum_next_open_order)
    
    return dict(
        open_trade_attributes=  label_and_size_open_trade,
        len_balancing_only_open_trade=   non_hedging_open_trade['len_balancing_only'],
        len_balancing_only_open_order=   non_hedging_open_orders['len_balancing_only'],
        sum_non_hedging_open_trade=   sum_non_hedging_open_trade,
        order_size= max(1, int(proforma_size))
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
    
    proforma = await get_proforma_attributes(sum_next_open_order)

    order_allowed=  proforma['len_balancing_only_open_order']== 0
    
    if order_allowed:
        
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
    
    only_one_open_order= proforma['len_balancing_only_open_order']== 0
    there_was_open_trade_with_balancing_label= proforma['len_balancing_only_open_trade']!= 0
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
    
def send_order (ask_price, bid_price, sum_next_open_order):
    is_send_exit_order_allowed (ask_price, 
                                bid_price)
    
    is_send_exit_order_allowed (ask_price, 
                                bid_price, 
                                sum_next_open_order)
    