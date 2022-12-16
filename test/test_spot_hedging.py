# -*- coding: utf-8 -*-

from risk_management import spot_hedging

open_orders = [
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3094422423', 'mmp': False, 'max_show': 107.0, 'last_update_timestamp': 1671058394609, 'label': 'hedging spot', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671058394609, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 107.0
        },
    {
        'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3094422424', 'mmp': False, 'max_show': 107.0, 'last_update_timestamp': 1671058394610, 'label': 'others', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671058394610, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 107.0
        }
    ]
    
def test_compute_minimum_hedging_size  ():
    notional = 107.38056472000001
    min_trade_amount = 1
    contract_size = 1
    assert spot_hedging.compute_minimum_hedging_size (notional, min_trade_amount, contract_size) == 108
    
def test_is_over_hedged  ():
    minimum_hedging_size = 108
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size) == False
    
    minimum_hedging_size = 107
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size) == False
    
    minimum_hedging_size = 106
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size) == True
    
def test_summing_size_open_orders_with_hedging_label  ():
    
    # default
    assert spot_hedging.summing_size_open_orders_basedOn_label (open_orders) == 107    
    # other label
    assert spot_hedging.summing_size_open_orders_basedOn_label (open_orders,'others') == 107