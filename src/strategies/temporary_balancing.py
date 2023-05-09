# # -*- coding: utf-8 -*-
from strategies import hedging_spot

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

def is_send_open_order_allowed (proforma_size: float,
                            ask_price: float,
                            bid_price: float,
                            current_outstanding_order_len: int,
                            ) -> dict:
    """

    Args:

    Returns:
        dict

    """

    order_allowed= current_outstanding_order_len== 0
    
    if order_allowed:
        
        
        params= get_basic_opening_paramaters(proforma_size)
        
        label_open = hedging_spot.get_label ('open', 'temporary') 
        params.update({"label": label_open})
        
        
        if params['side']=='sell':
            params.update({"side": })
            params.update({"entry_price": ask_price})
        if params['side']=='buy':
            params.update({"side": })
            params.update({"entry_price": bid_price})
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
    
def is_send_exit_order_allowed (ask_price: float,
                                bid_price: float,
                                current_outstanding_order_len: int,
                                selected_transaction: list,
                                strategy_attributes_for_hedging: list,
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
    