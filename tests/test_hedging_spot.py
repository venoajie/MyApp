# -*- coding: utf-8 -*-
import strategies.hedging_spot as hedging
import strategies.entries_exits as entry

strategy_attributes = entry.strategies

strategy_attributes_for_hedging=  [o for o in strategy_attributes if 'hedgingSpot' in o ['strategy']  ]

notional = 100

ask_price= 1900

def test_get_basic_opening_paramaters():
        
    result =  hedging.get_basic_opening_paramaters(notional, ask_price)
    
    assert result   ==  {'type': 'limit', 'side': 'sell', 'size': 10, 'type': 'limit', 'entry_price': 1900}

def test_are_size_and_order_appropriate_for_ordering():
    
    current_size= 20
    current_outstanding_order_len= 0
    result =  hedging.are_size_and_order_appropriate_for_ordering(notional, 
                                                                  current_size, 
                                                                  current_outstanding_order_len)
    assert result   == True
    
    current_size= 101
    result =  hedging.are_size_and_order_appropriate_for_ordering(notional, 
                                                                  current_size, 
                                                                  current_outstanding_order_len)
    assert result   == False

    current_size= 99
    current_outstanding_order_len= 1
    result =  hedging.are_size_and_order_appropriate_for_ordering(notional, 
                                                                  current_size, 
                                                                  current_outstanding_order_len)    
    assert result   == False


def test_get_labels():

    from src.utilities import time_modification
    
    now_utc = time_modification.convert_time_to_utc()["utc_now"]
    now_unix = time_modification.convert_time_to_unix(now_utc)
    
    label_main_or_label_transactions= 'hedgingSpot'
        
    result =  hedging.get_label('open', label_main_or_label_transactions)[:25]
    
    assert result   ==  f"{label_main_or_label_transactions}-open-{now_unix}"[:25]

    label_main_or_label_transactions= 'hedgingSpot-open-1683065013136'
    
    result =  hedging.get_label('closed', label_main_or_label_transactions)
    
    assert result   ==  'hedgingSpot-closed-1683065013136'
