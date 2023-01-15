from utilities import number_modification , string_modification
digit_list = [
    {'trade_seq': 12078753, 'trade_id': 'ETH-17768060', 'timestamp': 1673696484215, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3250634643', 'mmp': False, 'matching_id': None, 'mark_price': 1528.16, 'liquidity': 'M', 'label': 'hedgingSpot-open-1673696320', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.15, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 53.0}, {'trade_seq': 12078756, 'trade_id': 'ETH-17768405', 'timestamp': 1673696634262, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1529.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3250651320', 'mmp': False, 'matching_id': None, 'mark_price': 1529.96, 'liquidity': 'M', 'label': 'hedgingSpot-open-1673696623', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1530.1, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 53.0}]
print(f'{digit_list}')
digit_set = set([digit_list])
number = 99
if number  in digit_list:
   print(f'{number} is in digit_list')
