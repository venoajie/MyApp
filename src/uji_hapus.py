from collections import OrderedDict
from utils import string_modification

data_from_db = [
    {'trade_seq': 12032431, 'trade_id': 'ETH-16795793', 'timestamp': 1672353414082, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1196.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3182524037', 'mmp': False, 'matching_id': None, 'mark_price': 1196.95, 'liquidity': 'M', 'label': 'hedging spot-open-1672353389358', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1196.23, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}, 
    {'trade_seq': 12032432, 'trade_id': 'ETH-16795793', 'timestamp': 1672353414082, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1196.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3182524037', 'mmp': False, 'matching_id': None, 'mark_price': 1196.95, 'liquidity': 'M', 'label': 'hedging spot-open-1672353389358', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1196.23, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}, 
    {'trade_seq': 12032451, 'trade_id': 'ETH-16795821', 'timestamp': 1672354669320, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -2.044e-05, 'price': 1198.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3182583884', 'mmp': False, 'matching_id': None, 'mark_price': 1198.76, 'liquidity': 'M', 'label': 'hedging spot-closed-1672353851674', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1198.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 10.0}, 
    ]

#sum_data_from_db =    sum( [o['amount'] for o in data_from_db  ] )
#print(f'{sum_data_from_db=}')

data_from_db =    list({frozenset(item.items()):item for item in data_from_db}.values())
print(data_from_db)
data_from_db =  string_modification.remove_redundant_elements (data_from_db)
print(data_from_db)

