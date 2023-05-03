# # -*- coding: utf-8 -*-

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

def get_label (status: str, label_main_or_label_transactions: str) -> str:
    """

    Args:
    status: open/close

    Returns:
        bool

    """
    from strategies import hedging_spot
    
    return hedging_spot.get_label(status, label_main_or_label_transactions)

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

    order_allowed= are_size_and_order_appropriate_for_ordering (current_size,
                                                                current_outstanding_order_len
                                                                )
    
    if order_allowed:
        
        params= get_basic_opening_paramaters(notional)
        
        label_main= strategy_attributes_for_hedging['strategy']

        label_open = get_label ('open', label_main) 

        params.update({"label": label_open})
        params.update({"side": strategy_attributes_for_hedging['side']})
        if params['side']=='sell':
            params.update({"entry_price": ask_price})
        if params['side']=='sell':
            params.update({"entry_price": bid_price})
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)