from portfolio.deribit import myTrades_management

result = [{'trade_seq': 12037982, 'trade_id': 'ETH-16849570', 'timestamp': 1672904588984, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1250.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3204889017', 'mmp': False, 'matching_id': None, 'mark_price': 1250.0, 'liquidity': 'M', 'label': 'hedging spot-open-1672904517021', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1249.64, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 36.0}, {'trade_seq': 12037996, 'trade_id': 'ETH-16850154', 'timestamp': 1672909685110, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 3.247e-05, 'price': 1248.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3205039987', 'mmp': False, 'matching_id': None, 'mark_price': 1248.49, 'liquidity': 'M', 'label': 'hedging spot-closed-1672904517021', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1248.73, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 36.0}]

label = 'label'
for key in result:
    if label not in key:
       key [label] = []
print (result)
mixed_trades_with_the_same_label = ([o for o in result if  str('1672904517021')  not in o['label']  ])
print (mixed_trades_with_the_same_label)