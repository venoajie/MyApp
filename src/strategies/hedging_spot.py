# # -*- coding: utf-8 -*-

def get_basic_opening_paramaters(notional: float, 
                                 ask_price: float
                                 ) -> dict:
    """

    Args:

    Returns:
        dict

    """
    
    params= {}
    
    params.update({"side": 'sell'})
    params.update({"type": 'limit'})
    params.update({"entry_price": ask_price})
    params.update({"size": max(1, int(notional/10))})
    return params

def are_size_and_order_appropriate_for_ordering (notional: float,
                                                 current_size: float,
                                                 current_outstanding_order_len: int
                                                 ) -> bool:
    """

    Args:

    Returns:
        bool

    """
    return current_size < notional\
        and current_outstanding_order_len== 0

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
        
        from configuration import label_numbering
        
        params= get_basic_opening_paramaters(notional, 
                                             ask_price
                                             )
        
        label_main= strategy_attributes_for_hedging[0]['strategy']
        print (f' strategy_attributes_for_hedging {strategy_attributes_for_hedging}')
        label_main= strategy_attributes_for_hedging[0]['strategy']

        label_open = label_numbering.labelling("open", label_main)

        params.update({"label_numbered": label_open})
       
        params['size']= min(params['size'], 
                            int(notional-current_size)
                            )
    
    return dict(order_allowed= order_allowed,
                order_parameters= [] if order_allowed== False else params)
