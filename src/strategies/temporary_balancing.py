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

async def check_proforma_size(notional,
                              sum_next_open_order: int= 0) -> int:
    """ """

    label_and_size_open_trade= await querying_label_and_size('my_trades_all_json')
    label_and_size_current_open_order= await querying_label_and_size('orders_all_json')
    relevant_label= ['hedging' , 'basicGrid']
    relevant_open_trade= [o for o in label_and_size_open_trade if ([r for r in relevant_label if r in o['label_main']])]
    sum_relevant_open_trade= sum([o['amount_dir'] for o in relevant_open_trade])

    log.error(label_and_size_current_open_order)

    non_hedging_open_trade= [o for o in label_and_size_open_trade if 'hedging' not in o['label_main']]
    sum_non_hedging_open_trade= sum([o['amount_dir'] for o in non_hedging_open_trade])

    non_hedging_open_order= [o for o in label_and_size_current_open_order if 'hedging' not in o['label_main']]
    sum_non_hedging_open_order= sum([o['amount_dir'] for o in non_hedging_open_order])

    current_size= sum([o['amount_dir'] for o in label_and_size_open_trade])

    proforma_size=   (sum_non_hedging_open_trade + sum_non_hedging_open_order + sum_next_open_order)
    
    return dict(
        position=  proforma_size,
        proforma_size=   proforma_size,
        sum_non_hedging_open_trade=   sum_non_hedging_open_trade,
        additional_order= notional + proforma_size if proforma_size < 0 else notional - proforma_size)
    