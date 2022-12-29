from typing import Dict, List

data_from_db = [{'trade_seq': 432088, 'trade_id': 'ETH-16793984', 'timestamp': 1672278037399, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1191.65, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3178108975', 'mmp': False, 'matching_id': None, 'mark_price': 1191.73, 'liquidity': 'T', 'instrument_name': 'ETH-30DEC22', 'index_price': 1191.52, 'fee_currency': 'ETH', 'fee': 4.2e-07, 
'direction': 'sell', 'api': False, 'amount': 1.0}]
data = [{'trade_seq': 432089, 'trade_id': 'ETH-16793985', 'timestamp': 1672278041620, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.3e-07, 'price': 1191.8, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-3178109226', 'mmp': False, 'matching_id': None, 'mark_price': 1191.74, 'liquidity': 'T', 'instrument_name': 'ETH-30DEC22', 'index_price': 1191.55, 'fee_currency': 'ETH', 'fee': 4.2e-07, 'direction': 'buy', 'api': False, 'amount': 1.0}]

collected_data =    data_from_db.append(data[0])
print(f'{data_from_db=}')

