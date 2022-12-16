# -*- coding: utf-8 -*-

none_data = [None, [], '0.0', 0]


def summing_size_open_orders_basedOn_label(
    open_orders_byBot: list,
    label: str 
    ) -> int:
    
    '''
    # sum current open orders with 'hedging spot' label
    open_orders_byBot =  open orders submitted by API/not manual (web = False)

    '''       

    try:
        open_orders_hedging = open_orders_byBot
    except:
        open_orders_hedging = open_orders_byBot ['result']

    return 0 if open_orders_hedging in none_data else sum ([o['amount']  for o in open_orders_hedging if label in o['label'] ])


def compute_minimum_hedging_size (
    notional: float,
    min_trade_amount: float,
    contract_size: int
    ) -> int:
    
    '''
    compute minimum hedging size

    '''       
    return  int ((notional / min_trade_amount * contract_size) + min_trade_amount)


def compute_actual_hedging_size (
    hedging_instruments: list,
    position: list,
    ) -> int:
    
    '''
    compute actual hedging size

    '''       
    return  sum([o['size'] for o in position if o['instrument_name'] in hedging_instruments ])

def is_spot_hedged_properly (
    hedging_instruments: list,
    position: list,
    open_orders_byBot: list,
    notional: float,
    min_trade_amount: float,
    contract_size: int) -> dict:

    '''
    # check whether spot has hedged properly
    notional =  index_price * equity

    '''       
    # compute minimum hedging size
    min_hedged_size: int = compute_minimum_hedging_size (notional, min_trade_amount, contract_size)
    
    # check whether current spot was hedged
    actual_hedging_size : int = compute_actual_hedging_size (hedging_instruments, position) #! how to distinguish multiple strategy? (need to check label)

    # check remaining hedging needed
    remain_unhedged: int = int(min_hedged_size if actual_hedging_size  == [] else min_hedged_size + actual_hedging_size )

    # check open orders related to hedging, to ensure previous open orders has completely consumed
    open_orders_hedging_size = summing_size_open_orders_basedOn_label (open_orders_byBot, 'hedging spot-open')
    
    size_pct_qty = int ((10/100 * remain_unhedged ))
        
    return {'spot_was_hedged_properly': open_orders_hedging_size in none_data and remain_unhedged > 0,
            'hedging_size': remain_unhedged}

def is_over_hedged (
    open_orders_byBot: list,
    minimum_hedging_size: int) -> bool:

    '''
    # check open orders related to hedging, should be less than required hedging size. If potentially over-hedged, call cancel open orders function
    '''       
    return summing_size_open_orders_basedOn_label (open_orders_byBot) > minimum_hedging_size    
        