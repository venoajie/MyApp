# -*- coding: utf-8 -*-

from portfolio.deribit import myTrades_management

my_trades_all = [
    {
        'trade_seq': 12003659, 'trade_id': 'ETH-16463419', 'timestamp': 1670371457386, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1270.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057910288', 'mmp': False, 'matching_id': None, 'mark_price': 1269.79, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.29, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
     }, 
    {
        'trade_seq': 12003660, 'trade_id': 'ETH-16463573', 'timestamp': 1670371527398, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1270.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057913498', 'mmp': False, 'matching_id': None, 'mark_price': 1270.08, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.41, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
        }, 
    {
        'trade_seq': 12003661, 'trade_id': 'ETH-16463629', 'timestamp': 1670371552397, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -2.94e-06, 'price': 1271.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057914610', 'mmp': False, 'matching_id': None, 'mark_price': 1270.72, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.09, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': False, 'amount': 1.0
        }, 
    {
        'trade_seq': 12003663, 'trade_id': 'ETH-16463891', 'timestamp': 1670371662431, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.68e-05, 'price': 1269.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057918998', 'mmp': False, 'matching_id': None, 'mark_price': 1269.5, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1269.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': False, 'amount': 196.0
        }, 
    {
        'trade_seq': 12003667, 'trade_id': 'ETH-16463984', 'timestamp': 1670371717436, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.9e-07, 'price': 1269.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057918874', 'mmp': False, 'matching_id': None, 'mark_price': 1269.49, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1269.27, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
     }, 
    {'trade_seq': 5552, 'trade_id': 'ETH-16468267', 'timestamp': 1670380638979, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256841', 'mmp': False, 'matching_id': None, 'mark_price': 1265.51, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-9DEC22', 'index_price': 1265.6, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
     }, 
    {'trade_seq': 6613, 'trade_id': 'ETH-16468711', 'timestamp': 1670380845716, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256847', 'mmp': False, 'matching_id': None, 'mark_price': 1265.25, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-16DEC22', 'index_price': 1265.84, 'fee_currency': 'ETH', 'fee': 
-8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
}
    ]
    
my_trades_with_api_true = [
    {
        'trade_seq': 5552, 'trade_id': 'ETH-16468267', 'timestamp': 1670380638979, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256841', 'mmp': False, 'matching_id': None, 'mark_price': 1265.51, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-9DEC22', 'index_price': 1265.6, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
     }, 
    {'trade_seq': 6613, 'trade_id': 'ETH-16468711', 'timestamp': 1670380845716, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256847', 'mmp': False, 'matching_id': None, 'mark_price': 1265.25, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-16DEC22', 'index_price': 1265.84, 'fee_currency': 'ETH', 'fee': 
-8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
}
    ]

my_trades_with_manual = [
    {
        'trade_seq': 12003659, 'trade_id': 'ETH-16463419', 'timestamp': 1670371457386, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1270.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057910288', 'mmp': False, 'matching_id': None, 'mark_price': 1269.79, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.29, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
     }, 
    {
        'trade_seq': 12003660, 'trade_id': 'ETH-16463573', 'timestamp': 1670371527398, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1270.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057913498', 'mmp': False, 'matching_id': None, 'mark_price': 1270.08, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.41, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
        }, 
    {
        'trade_seq': 12003661, 'trade_id': 'ETH-16463629', 'timestamp': 1670371552397, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -2.94e-06, 'price': 1271.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057914610', 'mmp': False, 'matching_id': None, 'mark_price': 1270.72, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1270.09, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': False, 'amount': 1.0
        }, 
    {
        'trade_seq': 12003663, 'trade_id': 'ETH-16463891', 'timestamp': 1670371662431, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.68e-05, 'price': 1269.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057918998', 'mmp': False, 'matching_id': None, 'mark_price': 1269.5, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1269.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': False, 'amount': 196.0
        }, 
    {
        'trade_seq': 12003667, 'trade_id': 'ETH-16463984', 'timestamp': 1670371717436, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.9e-07, 'price': 1269.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3057918874', 'mmp': False, 'matching_id': None, 'mark_price': 1269.49, 'liquidity': 'M', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1269.27, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 1.0
     }
    ]


my_trades = myTrades_management.MyTrades(my_trades_all)
    
def test_myTrades_api  ():
    assert my_trades.my_trades_api () == my_trades_with_api_true
    
def test_myTrades_manual  ():
    
    assert my_trades.my_trades_manual () == my_trades_with_manual
    