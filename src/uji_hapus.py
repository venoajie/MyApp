from utilities import string_modification, number_modification, pickling, system_tools
from configuration import config
    #from loguru import logger as log
my_trades_open =    [{'trade_seq': 118020115, 'trade_id': 'ETH-160804604', 'timestamp': 1677059533908, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1640.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31873685113', 'mmp': False, 'matching_id': None, 'mark_price': 1640.88, 'liquidity': 'M', 'label': 'test-open-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.03, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}, {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118305997, 'trade_id': 'ETH-161151946', 'timestamp': 1677379636994, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1599.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31944078044', 'mmp': False, 'matching_id': None, 'mark_price': 1599.64, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677379624', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1599.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118327634, 'trade_id': 'ETH-161178533', 'timestamp': 1677436936464, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1622.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31951464881', 'mmp': False, 'matching_id': None, 'mark_price': 1621.27, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677436932', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1620.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118342537, 'trade_id': 'ETH-161197087', 'timestamp': 1677452774256, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1642.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31955055472', 'mmp': False, 'matching_id': None, 'mark_price': 1642.28, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677452758', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1642.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118355869, 'trade_id': 'ETH-161212758', 'timestamp': 1677474758759, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00011743, 'price': 1635.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514035', 'mmp': False, 'matching_id': None, 'mark_price': 1635.17, 'liquidity': 'M', 'label': 'supplyDemandLong60-open-1677473096934', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1635.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 9.0}]

my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                            'eth',
                                                                            'open'
                                                                            )
pickling.replace_data (my_trades_path_open_recovery, 
                                                my_trades_open, 
                                                True
                                                )
my_trades_open: str = pickling.read_data(my_trades_path_open_recovery)   
print (sum(([ o['amount'] for o in my_trades_open ])))


open_orders =    [{'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': True, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1475.5, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958754973', 'mmp': False, 'max_show': 24.0, 'last_update_timestamp': 1677500787119, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677474762554, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 24.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1675.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958514019', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096657, 'label': 'supplyDemandShort60-open-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1677473096657, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 8.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1490.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941729757', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361995418, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361995418, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1550.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941709815', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361867909, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361867909, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1535.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941707258', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361847107, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361847107, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1512.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941700022', 'mmp': False, 'max_show': 14.0, 'last_update_timestamp': 1677361811798, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361811798, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 14.0}, {'web': False, 'triggered': False, 'trigger_price': 1570.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1570.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5652932', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1677473096934, 'label': 'supplyDemandLong60-closed-1677473096934', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677473096934, 'api': True, 'amount': 9.0}, {'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0}]

path_orders_open: str = system_tools.provide_path_for_file ('orders', 
                                                                    'eth', 
                                                                    'open'
                                                                    )
pickling.replace_data (path_orders_open, 
                                                open_orders, 
                                                True
                                                )
my_orders_open: str = pickling.read_data(path_orders_open)   
file =  601677473096
print (str(file) [-10:])
print (sum(([ o['amount'] for o in my_orders_open ])))