# -*- coding: utf-8 -*-
import strategies.basic_grid as grid
import strategies.entries_exits as entry

strategy_attributes = entry.strategies

strategy_attributes_for_hedging=  [o for o in strategy_attributes if 'hedgingSpot' in o ['strategy']  ]

notional = 100

ask_price= 1900

def test_get_basic_opening_paramaters():
    
    current_outstanding_order_len= 0
        
    result =  grid.size_adjustment(current_outstanding_order_len)
    
    assert result   ==  1
    
    current_outstanding_order_len= 2
        
    result =  grid.size_adjustment(current_outstanding_order_len)
    
    assert result   == 0.3333333333333333
    
    current_outstanding_order_len= 1
        
    result =  grid.size_adjustment(current_outstanding_order_len)
    
    current_outstanding_order_len= 3
        
    result =  grid.size_adjustment(current_outstanding_order_len)
    
    assert result   == 0
    
def test_is_send_additional_order_allowed():

    notional= 14.68
    ask_price= 1950
    bid_price= 1800
    
    selected_transaction= [{"trade_seq":124846096,"trade_id":"ETH-169499233","timestamp":1683196536143,"tick_direction":2,"state":"filled","self_trade":False,"risk_reducing":False,"reduce_only":False,"profit_loss":-2.08e-05,"price":1915.9,"post_only":True,"order_type":"limit","order_id":"ETH-33232149026","mmp":False,"matching_id":None,"mark_price":1916.65,"liquidity":"M","label":"basicGridLong-open-1683196535027","instrument_name":"ETH-PERPETUAL","index_price":1915.26,"fee_currency":"ETH","fee":0.0,"direction":"buy","api":True,"amount":7.0}]
        
    result =  grid.is_send_additional_order_allowed(notional,
                                                    ask_price,
                                                    bid_price,
                                                    selected_transaction,
                                                    strategy_attributes_for_hedging)
    
    assert result   ==  True
    
    selected_transaction= [{"trade_seq":124728213,"trade_id":"ETH-169356431","timestamp":1683115014598,"tick_direction":3,"state":"filled","self_trade":False,"risk_reducing":False,"reduce_only":False,"profit_loss":0.0,"price":1860.65,"post_only":True,"order_type":"limit","order_id":"ETH-33212664365","mmp":False,"matching_id":None,"mark_price":1860.87,"liquidity":"M","label":"basicGridShort-open-1683115008542","instrument_name":"ETH-PERPETUAL","index_price":1860.74,"fee_currency":"ETH","fee":0.0,"direction":"sell","api":True,"amount":7.0}]
        
    result =  grid.is_send_additional_order_allowed(notional,
                                                    ask_price,
                                                    bid_price,
                                                    selected_transaction,
                                                    strategy_attributes_for_hedging)
    
    assert result   ==  True
    