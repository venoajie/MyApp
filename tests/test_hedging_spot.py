# -*- coding: utf-8 -*-
import strategies.hedging_spot as hedging
import strategies.entries_exits as entry

strategy_attributes = entry.strategies

strategy_attributes_for_hedging=  [o for o in strategy_attributes if 'hedgingSpot' in o ['strategy']  ]

notional = 100

ask_price= 1900

def test_get_basic_opening_paramaters():
        
    result =  hedging.get_basic_opening_paramaters(notional, ask_price)
    
    assert result   ==  {'type': 'limit', 'side': 'sell', 'size': 10, 'entry_price': 1900}

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

def test_get_open_interest_symbol():
    hedged_value = 10
    notional = 10
    threshold= .8
    
    result = hedging.hedged_value_to_notional(
                hedged_value, notional)
    assert result == 1
    
    result = hedging.is_hedged_value_to_notional_exceed_threshold(
                hedged_value, notional, threshold)
    assert result == True
    
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

def test_price_pct():
    price =  1800
    pct_threshold: float=3/100
    result =  hedging.price_plus_pct(price, pct_threshold)
    assert result   ==  1854.0
    result =  hedging.price_minus_pct(price, pct_threshold)
    assert result   ==   1746.0
    
def test_close_order():

    transaction= [{"trade_seq":124324604,"trade_id":"ETH-168837663","timestamp":1682657827181,
                  "tick_direction":1,"state":"filled","self_trade":False,"risk_reducing":False,
                  "reduce_only":False,"profit_loss":0.0,"price":1916.4,"post_only":True,
                  "order_type":"limit","order_id":"ETH-33127542643","mmp":False,"matching_id":None,
                  "mark_price":1916.47,"liquidity":"M","label":"hedgingSpot-open-1682657827125",
                  "instrument_name":"ETH-PERPETUAL","index_price":1915.34,"fee_currency":"ETH",
                  "fee":0.0,"direction":"sell","api":True,"amount":1.0}]
    
    bid_price =  1800
    pct_threshold: float=3/100
    last_transaction_price =  transaction [0]['price']
    result =  hedging.is_transaction_price_minus_below_threshold(last_transaction_price, bid_price, pct_threshold)
    assert result   ==  True
    bid_price2 =  1900
    result =  hedging.is_transaction_price_minus_below_threshold(last_transaction_price, bid_price2, pct_threshold)
    assert result   ==  False


    result =  hedging.get_basic_closing_paramaters(transaction)
    
    assert result   ==  {'type': 'limit', 
                         'side': 'buy', 
                         'size': 1, 
                         'label': 'hedgingSpot-closed-1682657827125'}

