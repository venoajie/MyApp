# -*- coding: utf-8 -*-
from src.portfolio.deribit import myTrades_management

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
},
    {
        'trade_seq': 12025028, 'trade_id': 'ETH-16706999', 'timestamp': 1671162869512, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 9.069e-05, 'price': 1271.35, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3103266070', 'mmp': False, 'matching_id': None, 'mark_price': 1271.27, 'liquidity': 'T', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1271.0, 'fee_currency': 'ETH', 'fee': 3.93e-06, 'direction': 'buy', 'api': False, 'amount': 10.0
        }, 
    {
        'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        }, 
    {
        'trade_seq': 1815, 'trade_id': 'ETH-16709239', 'timestamp': 1671190148793, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': -0.00011443, 'price': 1213.6, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3105766726', 'mmp': False, 'matching_id': None, 'mark_price': 1213.35, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1213.6, 'fee_currency': 'ETH', 'fee': 4.079e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        },
    {
        'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
     {
        'trade_seq': 1944, 'trade_id': 'ETH-16709979', 'timestamp': 1671200743449, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 2.697e-05, 'price': 1211.5, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3106694831', 'mmp': False, 'matching_id': None, 'mark_price': 1211.39, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.23, 'fee_currency': 'ETH', 'fee': 4.086e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        },
     {
        'trade_seq': 1945, 'trade_id': 'ETH-16709992', 'timestamp': 1671200864490, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106695378', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671200747737', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.78, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
     {
        'trade_seq': 1946, 'trade_id': 'ETH-16710035', 'timestamp': 1671200895090, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': -0.00044914, 'price': 1218.6, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3106710323', 'mmp': False, 'matching_id': None, 'mark_price': 1216.14, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1216.5, 'fee_currency': 'ETH', 'fee': 4.062e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        }
    ]
    
my_trades_with_api_true = [
    {
        'trade_seq': 5552, 'trade_id': 'ETH-16468267', 'timestamp': 1670380638979, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256841', 'mmp': False, 'matching_id': None, 'mark_price': 1265.51, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-9DEC22', 'index_price': 1265.6, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
     }, 
    {'trade_seq': 6613, 'trade_id': 'ETH-16468711', 'timestamp': 1670380845716, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1265.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256847', 'mmp': False, 'matching_id': None, 'mark_price': 1265.25, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-16DEC22', 'index_price': 1265.84, 'fee_currency': 'ETH', 'fee': 
-8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
},
    {
        'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
    {
        'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
        },
    {
        'trade_seq': 1945, 'trade_id': 'ETH-16709992', 'timestamp': 1671200864490, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106695378', 'mmp': False, 'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671200747737', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.78, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
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
     },
    {
        'trade_seq': 12025028, 'trade_id': 'ETH-16706999', 'timestamp': 1671162869512, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 9.069e-05, 'price': 1271.35, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3103266070', 'mmp': False, 'matching_id': None, 'mark_price': 1271.27, 'liquidity': 'T', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1271.0, 'fee_currency': 'ETH', 'fee': 3.93e-06, 'direction': 'buy', 'api': False, 'amount': 10.0
        }, 
    {
        'trade_seq': 1815, 'trade_id': 'ETH-16709239', 'timestamp': 1671190148793, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': -0.00011443, 'price': 1213.6, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3105766726', 'mmp': False, 'matching_id': None, 'mark_price': 1213.35, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1213.6, 'fee_currency': 'ETH', 'fee': 4.079e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        },
     {
        'trade_seq': 1944, 'trade_id': 'ETH-16709979', 'timestamp': 1671200743449, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 2.697e-05, 'price': 1211.5, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3106694831', 'mmp': False, 'matching_id': None, 'mark_price': 1211.39, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1211.23, 'fee_currency': 'ETH', 'fee': 4.086e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        },
     {
        'trade_seq': 1946, 'trade_id': 'ETH-16710035', 'timestamp': 1671200895090, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': -0.00044914, 'price': 1218.6, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3106710323', 'mmp': False, 'matching_id': None, 'mark_price': 1216.14, 'liquidity': 'T', 'instrument_name': 'ETH-23DEC22', 'index_price': 1216.5, 'fee_currency': 'ETH', 'fee': 4.062e-05, 'direction': 'buy', 'api': False, 'amount': 99.0
        }
    ]

my_trades_open =   [
    {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, 
    {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, 
    {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, 
    {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},    
    {'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0},
    
    {'trade_seq': 115446013, 'trade_id': 'ETH-157539723', 'timestamp': 1674139209708, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269847666', 'mmp': False, 'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134456', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0},  
    {'trade_seq': 115457369, 'trade_id': 'ETH-157553296', 'timestamp': 1674150736302, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 1.92e-05, 'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'M', 'label': 'supplyDemandShort15-closed-1674134456', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 10.0}, 
    {'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 'direction': 'buy', 'api': True, 'amount': 27.0}
    ]

my_trades_open_has_closed = [
    {'trade_seq': 115446013, 'trade_id': 'ETH-157539723', 'timestamp': 1674139209708, 'tick_direction': 1,
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269847666', 'mmp': False, 
     'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 
     'api': True, 'amount': 37.0
     },  
    {'trade_seq': 115457369, 'trade_id': 'ETH-157553296', 'timestamp': 1674150736302, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 1.92e-05, 
     'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 
     'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'M', 'label': 'supplyDemandShort15-closed-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 
     'api': True, 'amount': 10.0
     }, 
    {'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 
     'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 
     'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 'direction': 'buy', 
     'api': True, 'amount': 27.0
     }
    ]

my_trades_open_still_open = [
    {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, 
    {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, 
    {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, 
    {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},    
    {'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0}
    ]

trade_order_filled = [{'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}
    ]
my_trades_blank = []

my_trades_blank = myTrades_management.MyTrades (my_trades_blank)
my_trades = myTrades_management.MyTrades(my_trades_all)

my_trades_open_cls = myTrades_management.MyTrades(my_trades_open)
closed_label_id_int = 151674134456 
    
def test_recognize_trade_transactions  ():
    
    assert my_trades_open_cls.recognize_trade_transactions (trade_order_filled) == {
        'liquidation_event': False,
        'label_id': 'hedgingSpot-open-1674155736',
        'closed_label_id_int': 1674155736,
        'opening_position': True,
        'closing_position': False
        }

    assert my_trades_open_cls.recognize_trade_transactions (
        [
        {'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 'direction': 'buy', 'api': True, 'amount': 27.0}
        ]
                                                            ) == {
        'liquidation_event': False,
        'label_id': 'supplyDemandShort15-closed-1674134456',
        'closed_label_id_int': 151674134456,
        'opening_position': False,
        'closing_position': True
        }

   
def test_gather_transactions_under_the_same_id_int  ():
    
    assert my_trades_open_cls.gather_transactions_under_the_same_id_int (
                                                                        closed_label_id_int, 
                                                                        my_trades_open
                                                                        ) == {
                                                                            'transactions_same_id': my_trades_open_has_closed,
                                                                            'transactions_same_id_contain_open_label': True,
                                                                            'transactions_same_id_net_qty': 0,
                                                                            'transactions_same_id_len': 3,
                                                                            'remaining_open_trades': my_trades_open_still_open
                                                                            }
    
def test_transactions_same_id  ():    
    case_1 = my_trades_open_cls.transactions_same_id (closed_label_id_int,
                                                    my_trades_open
                                                    )              
    assert case_1 ['transactions_same_id'] == my_trades_open_has_closed
    assert case_1 ['transactions_same_id_contain_open_label'] == True
                                           
    case_2 = my_trades_open_cls.transactions_same_id (151674134451,
                                           my_trades_open) 
                                           
    assert case_2  ['transactions_same_id'] == [
        {
            'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 
            'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 
            'reduce_only': False, 'profit_loss': 0.0, 'price': 1538.0, 'post_only': True,
            'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 'matching_id': None, 
            'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 
            'direction': 'sell', 'api': True, 'amount': 37.0
            }
                                                               ]
    assert case_2 ['transactions_same_id_contain_open_label'] == True
                                           
                         
def test_remaining_open_trades  ():
    assert my_trades.remaining_open_trades (151674134456,
                                           my_trades_open) == [
    {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, 
    {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, 
    {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, 
    {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},    
    {'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0}
    ]
    
def test_myTrades_api  ():
    assert my_trades.my_trades_api () == my_trades_with_api_true
    
def test_myTrades_manual  ():
    
    assert my_trades.my_trades_manual () == my_trades_with_manual
    
def test_my_trades_api_basedOn_label ():
    
    assert my_trades.my_trades_api_basedOn_label ("hedging spot") == my_trades_with_api_true
    assert my_trades_blank.my_trades_api_basedOn_label ("hedging spot") == []
    
def test_extracting_unique_label_id ():
    my_trades_open =  [
        {
            'trade_seq': 116815874, 'trade_id': 'ETH-159322550', 'timestamp': 1675821492004, 'tick_direction': 0,
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0,
            'price': 1683.45, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31602844385', 'mmp': False, 
            'matching_id': None, 'mark_price': 1683.37, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675821361', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1682.04, 'fee_currency': 'ETH', 'fee': 0.0, 
            'direction': 'sell', 'api': True, 'amount': 3.0
            }, 
        
        {
            'trade_seq': 116938792, 'trade_id': 'ETH-159466502', 'timestamp': 1675953434933, 'tick_direction': 3, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.292e-05, 
            'price': 1641.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31628976781', 'mmp': False, 
            'matching_id': None, 'mark_price': 1641.02, 'liquidity': 'M', 'label': 'hedgingSpot-closed-1675821361', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.0, 'fee_currency': 'ETH', 'fee': 0.0,
            'direction': 'buy', 'api': True, 'amount': 3.0
         }, 
        {
            'trade_seq': 116815446, 'trade_id': 'ETH-159322072', 'timestamp': 1675821137153, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1684.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31602799753', 'mmp': False, 
            'matching_id': None, 'mark_price': 1684.92, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675821095', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1683.35, 'fee_currency': 'ETH', 'fee': 0.0, 
            'direction': 'sell', 'api': True, 'amount': 1.0
            },
        {
            'trade_seq': 116933031, 'trade_id': 'ETH-159459836', 'timestamp': 1675947168096, 'tick_direction': 3, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -4.01e-06,
            'price': 1640.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31627609960', 'mmp': False, 
            'matching_id': None, 'mark_price': 1640.25, 'liquidity': 'M', 'label': 'hedgingSpot-closed-1675821095', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1640.11, 'fee_currency': 'ETH', 'fee': 0.0, 
            'direction': 'buy', 'api': True, 'amount': 1.0
            },
         {
             'trade_seq': 115446013, 'trade_id': 'ETH-157539723', 'timestamp': 1674139209708, 'tick_direction': 1, 
             'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0,
             'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269847666', 'mmp': False, 
             'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134456',
             'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 
             'direction': 'sell', 'api': True, 'amount': 37.0
             },  
         {
             'trade_seq': 115457369, 'trade_id': 'ETH-157553296', 'timestamp': 1674150736302, 'tick_direction': 3, 
             'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 1.92e-05,
             'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False,
             'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'M', 'label': 'supplyDemandShort15-closed-1674134456', 
             'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 0.0, 
             'direction': 'buy', 'api': True, 'amount': 10.0
             }, 
         {
             'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 
             'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 
             'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 
             'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 
             'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 
             'direction': 'buy', 'api': True, 'amount': 27.0
             },
          {
            'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 'tick_direction': 1,
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0,
            'price': 1538.0, 'post_only': True,'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 'matching_id': None, 
            'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 
            'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 
            'direction': 'sell', 'api': True, 'amount': 37.0
            }
       
        ]
    
    assert my_trades.extracting_unique_label_id (my_trades_open) ==  [1675821361, 1675821095, 151674134456]


def test_closed_open_order_label_in_my_trades_open ():
    from src.portfolio.deribit import open_orders_management
    
    my_trades_open =    [
        {'trade_seq': 118020115, 'trade_id': 'ETH-160804604', 'timestamp': 1677059533908, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1640.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31873685113', 'mmp': False, 'matching_id': None, 'mark_price': 1640.88, 'liquidity': 'M', 'label': 'test-open-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.03, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0},
        {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118305997, 'trade_id': 'ETH-161151946', 'timestamp': 1677379636994, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1599.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31944078044', 'mmp': False, 'matching_id': None, 'mark_price': 1599.64, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677379624', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1599.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118327634, 'trade_id': 'ETH-161178533', 'timestamp': 1677436936464, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1622.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31951464881', 'mmp': False, 'matching_id': None, 'mark_price': 1621.27, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677436932', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1620.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118342537, 'trade_id': 'ETH-161197087', 'timestamp': 1677452774256, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1642.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31955055472', 'mmp': False, 'matching_id': None, 'mark_price': 1642.28, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677452758', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1642.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118355869, 'trade_id': 'ETH-161212758', 'timestamp': 1677474758759, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00011743, 'price': 1635.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514035', 'mmp': False, 'matching_id': None, 'mark_price': 1635.17, 'liquidity': 'M', 'label': 'supplyDemandLong60-open-1677473096934', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1635.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 9.0}]
 
    # open order has executed
    assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open, 
                                                                1677059533
                                                                ) ==  True

    # open order has executed
    assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open,
                                                                601677473096934
                                                                ) ==  True
    
    assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open, 
                                                                601677473096745
                                                                ) ==  False 
    
    my_orders= [
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': True, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1475.5, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958754973', 'mmp': False, 'max_show': 24.0, 'last_update_timestamp': 1677500787119, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677474762554, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 24.0}, 
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1675.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958514019', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096657, 'label': 'supplyDemandShort60-open-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1677473096657, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 8.0}, 
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1490.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941729757', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361995418, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361995418, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, 
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1550.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941709815', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361867909, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361867909, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, 
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1535.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941707258', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361847107, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361847107, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0},
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1512.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941700022', 'mmp': False, 'max_show': 14.0, 'last_update_timestamp': 1677361811798, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361811798, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 14.0}, 
        {'web': False, 'triggered': False, 'trigger_price': 1570.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1570.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5652932', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1677473096934, 'label': 'supplyDemandLong60-closed-1677473096934', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677473096934, 'api': True, 'amount': 9.0}, 
        {'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0}
        ]
    
    open_orders = open_orders_management.MyOrders (my_orders)
    open_orderLabelCLosed =  open_orders.open_orderLabelCLosed(my_orders) 
    for label_closed in open_orderLabelCLosed:
        if label_closed == 1677059533:
            
            # open order has executed. 
            assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open, 
                                                                        1677059533
                                                                        ) ==  True
        # open order has executed
        if label_closed == 601677473096934:
            assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open, 
                                                                        601677473096934
                                                                        ) ==  True
        # open ordernot in open trade since has not executed yet
        if label_closed == 601677473096745:
            assert my_trades.closed_open_order_label_in_my_trades_open (my_trades_open, 
                                                                        601677473096745
                                                                        ) ==  False
    
        
