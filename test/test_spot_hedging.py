# -*- coding: utf-8 -*-

from risk_management import spot_hedging

open_orders = [
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3094422423', 'mmp': False, 'max_show': 107.0, 'last_update_timestamp': 1671058394609, 'label': 'hedging spot-open', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671058394609, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 107.0
        },
    {
        'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3094422424', 'mmp': False, 'max_show': 107.0, 'last_update_timestamp': 1671058394610, 'label': 'others', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671058394610, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 107.0
        }
    ]


myTrades =  [
    
    {
        'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }, 
    {
        'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }, 
    {
        'trade_seq': 1945, 'trade_id': 'ETH-16709992', 'timestamp': 1671200864490, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106695378', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671200747737', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.78, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }, 
    ]

label_hedging = 'hedging spot'
spot_hedging = spot_hedging.SpotHedging (label_hedging,
                                        myTrades)
                            
def test_compute_minimum_hedging_size  ():
    notional = 107.38056472000001
    min_trade_amount = 1
    contract_size = 1
    assert spot_hedging.compute_minimum_hedging_size (notional, min_trade_amount, contract_size) == 108
    
def test_compute_actual_hedging_size  ():
    
    assert spot_hedging.compute_actual_hedging_size () == 297 
    
def  is_over_hedged  ():
    minimum_hedging_size = 108
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size, 'hedging spot-open') == False
    
    minimum_hedging_size = 106
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size, 'hedging spot-open') == True
    
    minimum_hedging_size = 107
    assert spot_hedging.is_over_hedged (open_orders, minimum_hedging_size, 'hedging spot-open') == False
    
def test_compute_remain_unhedged ():
    notional = 107.38056472000001
    min_trade_amount = 1
    contract_size = 1
    
    assert spot_hedging.compute_remain_unhedged (notional, min_trade_amount, contract_size) == -189 
    
    
def test_myTrades_max_price_plus_threshold  ():
    
    threshold = 2/100
    assert spot_hedging.my_trades_max_price_plus_threshold (threshold, 1215)['index_price_higher_than_threshold'] == False      
    assert spot_hedging.my_trades_max_price_plus_threshold (threshold, 1250)['index_price_higher_than_threshold'] == True      
    assert spot_hedging.my_trades_max_price_plus_threshold (threshold, 1150)['index_price_lower_than_threshold'] == True      
    assert spot_hedging.my_trades_max_price_plus_threshold (threshold, 1209)['index_price_lower_than_threshold'] == False  
    
def separate_open_trades_which_have_closed  ():
    closed_label = 'close'
    all_trades = [
        {
            'trade_seq': 1815, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012392, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705293', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-closed-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 
            'direction': 'sell', 'api': True, 'amount': 99.0
            },
        {
            'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 
            'direction': 'sell', 'api': True, 'amount': 99.0
            },
        {
        'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
    {
        'trade_seq': 1945, 'trade_id': 'ETH-16709992', 'timestamp': 1671200864490, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106695378', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671200747737', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.78, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }
                  ]  
    closed_trades = [
        {
            'trade_seq': 1815, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012392, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705293', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-closed-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 
            'direction': 'sell', 'api': True, 'amount': 99.0
            },
        {
            'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 
            'direction': 'sell', 'api': True, 'amount': 99.0
            }] 
    open_trades = [
        {
        'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
    {
        'trade_seq': 1945, 'trade_id': 'ETH-16709992', 'timestamp': 1671200864490, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106695378', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671200747737', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.78, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }
    ]
    assert spot_hedging.separate_open_trades_pair_which_have_closed ('eth', 'hedging spot', closed_label, all_trades)['closed_trades'] ==  closed_trades    
    assert spot_hedging.separate_open_trades_pair_which_have_closed ('eth', 'hedging spot', closed_label, all_trades)['remaining_open_trades'] ==  open_trades