from utilities import string_modification, number_modification, pickling, system_tools
from configuration import config

# from loguru import logger as log
my_trades_open =[{'trade_seq': 119459281, 'trade_id': 'ETH-162634254', 'timestamp': 1678610180143, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1473.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32205761779', 'mmp': False, 'matching_id': None, 'mark_price': 1472.79, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678610144572', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1474.68, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}, {'trade_seq': 119653801, 'trade_id': 'ETH-162909430', 'timestamp': 1678706775993, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1583.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32231983208', 'mmp': False, 'matching_id': None, 'mark_price': 1583.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678706775367', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1583.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 5.0}, {'trade_seq': 119665688, 'trade_id': 'ETH-162925875', 'timestamp': 1678713118256, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1598.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32234303212', 'mmp': False, 'matching_id': None, 'mark_price': 1597.73, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678713106585', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1597.86, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 119736857, 'trade_id': 'ETH-163020718', 'timestamp': 1678727097665, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915623', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089260', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 119736858, 'trade_id': 'ETH-163020719', 'timestamp': 1678727097665, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915636', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089307', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 119736859, 'trade_id': 'ETH-163020720', 'timestamp': 1678727097665, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915644', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089354', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 119768876, 'trade_id': 'ETH-163063379', 'timestamp': 1678752436502, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1675.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32250933239', 'mmp': False, 'matching_id': None, 'mark_price': 1675.63, 'liquidity': 'M', 'label': 'supplyDemandShort60-open-1678752418638', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1676.53, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}, {'trade_seq': 119770313, 'trade_id': 'ETH-163065243', 'timestamp': 1678753450450, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1682.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32251301873', 'mmp': False, 'matching_id': None, 'mark_price': 1681.94, 'liquidity': 'M', 'label': 'supplyDemandShort60-open-1678753445244', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1682.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}, {'trade_seq': 119773081, 'trade_id': 'ETH-163068627', 'timestamp': 1678755677524, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1671.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32252020677', 'mmp': False, 'matching_id': None, 'mark_price': 1671.66, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678755675478', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1673.29, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 68.0}]


my_trades_path = system_tools.provide_path_for_file("myTrades", "eth", "open")
pickling.replace_data(my_trades_path, my_trades_open, True)


my_trades_path_open_recovery = system_tools.provide_path_for_file(
    "myTrades", "eth", "open-recovery-point"
)
pickling.replace_data(my_trades_path_open_recovery, my_trades_open, True)

net = number_modification.net_position(my_trades_open)
print(f" ALL {net}")

