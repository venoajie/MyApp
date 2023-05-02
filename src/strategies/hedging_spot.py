# # -*- coding: utf-8 -*-

def get_basic_opening_paramaters(notional: float, 
                                 ask_price: float
                                 ) -> dict:
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
    params.update({"size": max(1, int(notional/10))})
    
    # opening side for spot hedging is always sell 
    params.update({"side": 'sell'})
    params.update({"entry_price": ask_price})
    
    return params

def are_size_and_order_appropriate_for_ordering (notional: float,
                                                 current_size: float,
                                                 current_outstanding_order_len: int
                                                 )-> bool:
    """

    Args:

    Returns:
        bool

    """
    
    return current_size < notional and current_outstanding_order_len== 0
        
def get_label (status: str, label_main_or_label_transactions: str) -> str:
    """

    Args:
    status: open/close

    Returns:
        bool

    """
    
    from configuration import label_numbering
    
    if status=='open':
        # get open label
        label = label_numbering.labelling("open", label_main_or_label_transactions)
    
    if status=='closed':
        from utilities import string_modification as str_mod
        
        # parsing label id
        label_id= str_mod.parsing_label(label_main_or_label_transactions)['int']

        # parsing label strategy
        label_main= str_mod.parsing_label(label_main_or_label_transactions)['main']
        
        # combine id + label strategy
        label = f'''{label_main}-closed-{label_id}'''
        
    return label
        
def is_send_order_allowed (notional: float,
                            ask_price: float,
                            current_size: int, 
                            current_outstanding_order_len: int,
                            strategy_attributes_for_hedging
                            ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    order_allowed= are_size_and_order_appropriate_for_ordering (notional,
                                                                current_size,
                                                                current_outstanding_order_len
                                                                )
    
    if order_allowed:
        
        params= get_basic_opening_paramaters(notional, 
                                             ask_price
                                             )
        
        label_main= strategy_attributes_for_hedging['strategy']

        label_open = get_label ('open', label_main) 

        params.update({"label": label_open})
       
        params['size']= min(params['size'], 
                            int(notional-current_size)
                            )
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)

def is_last_transaction_price_plus_exceed_current_price(last_transaction_price: float,
                                                        current_price: float,
                                                        pct_threshold: float=3/100
                                                        )-> bool:
    last_price_plus= last_transaction_price + (last_transaction_price * pct_threshold)
    
    return last_price_plus > current_price

def is_minimum_waiting_time_has_exceeded(last_transaction_timestamp: int)-> bool:    
    return

def is_send_additional_order_allowed (notional: float, 
                                      last_transaction_price: float,
                                      ask_price: float,
                                      current_outstanding_order_len: int,
                                      strategy_attributes_for_hedging,
                                      time_threshold,
                                      threshold: float=3/100
                                      )-> bool:
    """

    Args:

    Returns:
        dict

    """
    
    order_allowed= is_last_transaction_price_plus_exceed_current_price (last_transaction_price,
                                                                        ask_price,
                                                                        threshold
                                                                        )
    
    if order_allowed:
        
        params= get_basic_opening_paramaters(notional, 
                                             ask_price
                                             )
        
        label_main= strategy_attributes_for_hedging['strategy']

        label_open = get_label ('open', label_main) 

        params.update({"label": label_open})
       
        params['size']= min(params['size'], 
                            int(notional-current_size)
                            )
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
