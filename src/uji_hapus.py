

my_orders_status=  [
    {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1412.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'filled', 'order_id': 'ETH-3244292314', 'mmp': False, 'max_show': 17.0, 'last_update_timestamp': 1673581879756, 'label': 'hedgingSpot-open-1673581794', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 17.0, 'direction': 'sell', 'creation_timestamp': 1673581795330, 'commission': 0.0, 'average_price': 1412.55, 'api': True, 'amount': 17.0}, 
    {'trade_seq': 12069054, 'trade_id': 'ETH-17583474', 'timestamp': 1673625135822, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 8.68e-06, 'price': 1421.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3246703485', 'mmp': False, 'matching_id': None, 'mark_price': 1421.4, 'liquidity': 'M', 'label': 'hedgingSpot-open-1673625134', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1420.9, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}
    ]
for order in my_orders_status:

    try:
        trade_seq = order ['trade_seq']
        order_state = order ['state']
    except:
        order_state = order ['order_state']
    
print (order_state)    