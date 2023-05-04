# # -*- coding: utf-8 -*-

def get_basic_opening_paramaters(notional: float,  ask_price: float) -> dict:
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

def get_basic_closing_paramaters(selected_transaction: list) -> dict:
    """

    Args:

    Returns:
        dict

    """
    transaction= selected_transaction[0]
    
    #provide placeholder for params
    params= {}
    
    # default type: limit
    params.update({"type": 'limit'})
    
    # size=exactly amount of transaction size
    params.update({"size": transaction['amount']})
    
    # closing side for spot hedging is always buy 
    params.update({"side": 'buy'})
    label_closed = get_label ('closed', transaction['label']) 
    params.update({"label": label_closed})
    
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
    return abs(current_size) < notional and current_outstanding_order_len== 0
        
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
        
def is_send_open_order_allowed (notional: float,
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

def pct_price_in_usd(price: float, pct_threshold: float)-> bool:    
    return price * pct_threshold

def price_plus_pct(price: float, pct_threshold: float)-> float:    
    return price + pct_price_in_usd (price, pct_threshold)

def price_minus_pct(price: float, pct_threshold: float)-> float:    
    return price - pct_price_in_usd (price, pct_threshold)

def is_transaction_price_minus_below_threshold(last_transaction_price: float,
                                                        current_price: float,
                                                        pct_threshold: float
                                                        )-> bool:    
    
    return price_minus_pct (last_transaction_price, pct_threshold) > current_price

def is_transaction_price_plus_above_threshold(last_transaction_price: float,
                                              current_price: float,
                                              pct_threshold: float
                                              )-> bool:  
    
    return price_plus_pct (last_transaction_price, pct_threshold) < current_price

def is_minimum_waiting_time_has_exceeded(last_transaction_timestamp: int)-> bool:    
    return

def hedged_value_to_notional (notional: float, hedged_value: float) -> float:
    """ 
    """        
    return abs(hedged_value/notional)
    
def is_hedged_value_to_notional_exceed_threshold (notional: float, 
                                                  hedged_value: float, 
                                                  threshold : float
                                                  ) -> float:
    """ 
    """        
    return hedged_value_to_notional (notional, hedged_value) > threshold
    
def is_send_exit_order_allowed (notional: float,
                                bid_price: float,
                                current_size: int, 
                                current_outstanding_order_len: int,
                                selected_transaction,
                                strategy_attributes_for_hedging,
                                ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    MIN_HEDGING_RATIO= .8
    
    # transform to dict
    transaction= selected_transaction[0]
    
     # get price
    last_transaction_price= transaction['price']
    
    # get take profit pct
    tp_pct= strategy_attributes_for_hedging["take_profit_pct"]
    
    tp_price_reached= is_transaction_price_minus_below_threshold(last_transaction_price,
                                                                      bid_price,
                                                                      tp_pct
                                                                      )
    
    hedged_value_is_still_safe= is_hedged_value_to_notional_exceed_threshold (notional,
                                                                              current_size,
                                                                              MIN_HEDGING_RATIO
                                                                              )
    no_outstanding_order= current_outstanding_order_len < 1

    order_allowed= tp_price_reached\
        and hedged_value_is_still_safe\
            and no_outstanding_order 
    
    if order_allowed:
        
        # get transaction parameters
        params= get_basic_closing_paramaters(selected_transaction)
        params.update({"entry_price": bid_price})
        params.update({"instrument":  transaction['instrument_name']})
        
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
    
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
    
    ONE_MINUTE= 60000
    WAITING_MINUTE= 15
    time_stamp= transaction['timestamp']
    exit_order_allowed["size"] = int(
                                        max(notional * 10 / 100, 2)
                                    )
    order_allowed= is_last_transaction_price_plus_exceed_current_price (last_transaction_price,
                                                                        ask_price,
                                                                        threshold
                                                                        )
    
    time_threshold: float = (strategy_attributes_for_hedging["halt_minute_before_reorder"] * ONE_MINUTE * WAITING_MINUTE)

    delta_time: int = server_time - time_stamp
    
    waiting_time_has_passed: int = delta_time > time_threshold
    
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
    
