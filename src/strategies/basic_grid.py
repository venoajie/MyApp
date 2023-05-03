# # -*- coding: utf-8 -*-
from strategies import hedging_spot

def get_basic_opening_paramaters(notional: float) -> dict:
    """

    Args:

    Returns:
        dict

    """
    PCT_SIZE_TO_NOTIONAL= .5
    
    #provide placeholder for params
    params= {}
    
    # default type: limit
    params.update({"type": 'limit'})
    
    # size=notional. ordered in several times (default 10x)
    params.update({"size": max(1, int(notional * PCT_SIZE_TO_NOTIONAL))})
        
    return params

def are_size_and_order_appropriate_for_ordering (current_size: float,
                                                 current_outstanding_order_len: int
                                                 )-> bool:
    """

    Args:

    Returns:
        bool

    """
    
    return abs(current_size) == 0 and current_outstanding_order_len== 0

def is_send_open_order_allowed (notional: float,
                            ask_price: float,
                            bid_price: float,
                            current_size: int, 
                            current_outstanding_order_len: int,
                            strategy_attributes_for_hedging
                            ) -> dict:
    """

    Args:

    Returns:
        dict

    """

    order_allowed= are_size_and_order_appropriate_for_ordering (current_size, current_outstanding_order_len)
    
    if order_allowed:
        
        # get transaction parameters
        params= get_basic_opening_paramaters(notional)
        
        # get transaction label and update the respective parameters
        label_main= strategy_attributes_for_hedging['strategy']
        label_open = hedging_spot.get_label ('open', label_main) 
        params.update({"label": label_open})
        
        params.update({"side": strategy_attributes_for_hedging['side']})
        if params['side']=='sell':
            params.update({"entry_price": ask_price})
        if params['side']=='buy':
            params.update({"entry_price": bid_price})
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
    
def is_send_exit_order_allowed (ask_price: float,
                                bid_price: float,
                                current_outstanding_order_len: int,
                                selected_transaction,
                                strategy_attributes_for_hedging,
                                ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    # transform to dict
    transaction= selected_transaction[0]
    
    # get price
    last_transaction_price= transaction['price']
    
    transaction_side= transaction['direction']

    # get take profit pct
    tp_pct= strategy_attributes_for_hedging["take_profit_pct"]

    # get transaction parameters
    params= hedging_spot.get_basic_closing_paramaters(selected_transaction)
    
    if transaction_side=='sell':
        tp_price_reached= hedging_spot.is_transaction_price_minus_below_threshold(last_transaction_price,
                                                                      bid_price,
                                                                      tp_pct
                                                                      )
        params.update({"entry_price": bid_price})
        
    if transaction_side=='buy':
        tp_price_reached= hedging_spot.is_transaction_price_plus_above_threshold(last_transaction_price,
                                                                      ask_price,
                                                                      tp_pct
                                                                      )
        params.update({"entry_price": ask_price})
        params['side']='sell'
    
    print(f'tp_price_reached {tp_price_reached}')
    no_outstanding_order= current_outstanding_order_len < 1

    order_allowed= tp_price_reached\
            and no_outstanding_order 
    
    if order_allowed:
        
        params.update({"instrument":  transaction['instrument_name']})
        
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)