# # -*- coding: utf-8 -*-

# built ins
import asyncio

# user defined formula
from strategies import hedging_spot
from db_management import sqlite_management
from loguru import logger as log

def get_basic_opening_paramaters(proforma_size: int) -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    #provide placeholder for params
    params= {}
    
    # default type: limit
    params.update({"type": 'limit'})
    
    # size=notional. ordered in several times (default 10x)
    params.update({"size": abs(proforma_size)})
        
    return params

async def querying_label_and_size(table) -> dict:
    """ """
    
    NONE_DATA: None = [0, None, []]
    
    query =  sqlite_management.querying_label_and_size (table) 
    result = await sqlite_management.executing_query_with_return (query) 
    
    return  [] if result in NONE_DATA  else (result)

def non_hedging_transactions(transaction_summary_from_sqlite) -> dict:
    """ """
    
    result = [] if transaction_summary_from_sqlite == [] \
        else [o for o in transaction_summary_from_sqlite if 'hedging' not in o['label_main']] 

    return  dict(
        all= [] if result in [] else (result),
        sum_non_hedging = 0 if result in  [] else sum([o['amount_dir'] for o in result]),
        len_non_hedging = 0 if result in  [] else len([o  for o in result])
                )

def filter_non_hedging_transactions(label_and_size_open_trade) -> dict:
    """ """
    
    relevant_label= ['hedging' , 'basicGrid']

    return  [o for o in label_and_size_open_trade if ([r for r in relevant_label if r in o['label_main']])]

def get_size(sum_non_hedging_open_trade, sum_non_hedging_open_order, sum_next_open_order) -> dict:
    """ """
    
    return (sum_non_hedging_open_trade + sum_non_hedging_open_order + sum_next_open_order)

async def get_proforma_attributes (sum_next_open_order: int= 0) -> int:
    """ """

    label_and_size_open_trade= await querying_label_and_size('my_trades_all_json')
    
    label_and_size_current_open_order= await querying_label_and_size('orders_all_json')
    
    sum_non_hedging_open_trade= non_hedging_transactions(label_and_size_open_trade)['sum_non_hedging']

    sum_non_hedging_open_order= non_hedging_transactions(label_and_size_current_open_order)['sum_non_hedging']
    len_non_hedging_open_order= non_hedging_transactions(label_and_size_current_open_order)['len_non_hedging']
    
    proforma_size=   get_size (sum_non_hedging_open_trade + sum_non_hedging_open_order + sum_next_open_order)
    
    return dict(
        position=  proforma_size,
        len_non_hedging_open_order=   len_non_hedging_open_order,
        sum_non_hedging_open_trade=   sum_non_hedging_open_trade,
        order_size= max(1, abs(proforma_size * 50/100))
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

    order_allowed=  proforma['len_non_hedging_open_order']== 0
    
    if order_allowed:
        
        params= get_basic_opening_paramaters(proforma)
        
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
    print (params)
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)