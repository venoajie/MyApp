# # -*- coding: utf-8 -*-

def get_basic_opening_paramaters(notional: float, strategy_attributes_for_hedging: list) -> dict:
    """

    Args:

    Returns:
        float

    """
    from configuration import label_numbering
    print(f' strategy_attributes_for_hedging AAAAAAAA {strategy_attributes_for_hedging}')
    
    label_main= strategy_attributes_for_hedging[0]['strategy']
    print(label_main)

    
    params= {}
    
    label_open = label_numbering.labelling("open", label_main)
    
    params.update({"side": 'sell'})
    params.update({"type": 'limit'})
    params.update({"label_numbered": 'limit'})
    params.update({"size": max(1, int(notional/10))})
    return params
