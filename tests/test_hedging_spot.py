# -*- coding: utf-8 -*-
import strategies.hedging_spot as hedging
import strategies.entries_exits as entry

strategy_attributes = entry.strategies

def test_get_basic_opening_paramaters():
    
    notional = 100
    
    strategy_attributes_for_hedging=  [o for o in strategy_attributes if strategy_attributes['strategy']== 'hedgingSpot'  ]
    
    result =  hedging.get_basic_opening_paramaters(notional, strategy_attributes_for_hedging)
    
    assert result   ==  {'label_numbered': 'limit', 'side': 'sell', 'size': 10, 'type': 'limit'}
