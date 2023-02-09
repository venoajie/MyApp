from utilities import string_modification, number_modification
    #from loguru import logger as log
my_trades_open =   [{'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116295592, 'trade_id': 'ETH-158666464', 'timestamp': 1675218407734, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1582.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31482969205', 'mmp': False, 'matching_id': None, 'mark_price': 1583.14, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675218347', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1583.0, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116303913, 'trade_id': 'ETH-158676677', 'timestamp': 1675238339854, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1575.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31485281614', 'mmp': False, 'matching_id': None, 'mark_price': 1575.58, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675238303', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1575.76, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116465184, 'trade_id': 'ETH-158891580', 'timestamp': 1675379252622, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1655.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31520179892', 'mmp': False, 'matching_id': None, 'mark_price': 1656.09, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675379243', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1655.42, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}, {'trade_seq': 116586426, 'trade_id': 'ETH-159044582', 'timestamp': 1675581870717, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.45, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31554443951', 'mmp': False, 'matching_id': None, 'mark_price': 1666.14, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675581570', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.06, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116588607, 'trade_id': 'ETH-159047366', 'timestamp': 1675585799903, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1668.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31554705364', 'mmp': False, 'matching_id': None, 'mark_price': 1668.89, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675584995', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1667.93, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116472339, 'trade_id': 'ETH-158900963', 'timestamp': 1675391421593, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 2.587e-05, 'price': 1640.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31522727677', 'mmp': False, 'matching_id': None, 'mark_price': 1640.7, 'liquidity': 'M', 'label': 'hedgingSpot-closed-1675378289', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1640.26, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}, {'trade_seq': 116473961, 'trade_id': 'ETH-158903008', 'timestamp': 1675393566147, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 2.9e-05, 'price': 1637.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31523109496', 'mmp': False, 'matching_id': None, 'mark_price': 1637.95, 'liquidity': 'M', 'label': 'hedgingSpot-closed-1675378289', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1637.22, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}, {'trade_seq': 116815446, 'trade_id': 'ETH-159322072', 'timestamp': 1675821137153, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1684.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31602799753', 'mmp': False, 'matching_id': None, 'mark_price': 1684.92, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675821095', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1683.35, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 116815874, 'trade_id': 'ETH-159322550', 'timestamp': 1675821492004, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1683.45, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31602844385', 'mmp': False, 'matching_id': None, 'mark_price': 1683.37, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675821361', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1682.04, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}, {'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 'direction': 'buy', 'api': True, 'amount': 27.0}]

label = 151674134456
print ([o for o in my_trades_open if (label) == string_modification.extract_integers_from_text (o['label']) ])