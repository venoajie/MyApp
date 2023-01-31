
my_trades_open =   {'uid': 148510, 'positions': [
    {'total_profit_loss': -0.002756278, 'size_currency': -0.047298459, 'size': -77.0, 'settlement_price': 1627.85, 'realized_profit_loss': 3.151e-06, 'realized_funding': 3e-06, 'open_orders_margin': 0.0, 'mark_price': 1627.96, 'maintenance_margin': 0.000472994, 'leverage': 50, 'kind': 'future', 'interest_value': 1.1874580497134912, 'instrument_name': 'ETH-PERPETUAL', 'initial_margin': 0.000945978, 'index_price': 1626.3, 'floating_profit_loss': -3.838e-06, 'estimated_liquidation_price': 249558.85, 'direction': 'sell', 'delta': -0.047298459, 'average_price': 1538.32}, 
    {'total_profit_loss': 0.0, 'size_currency': 0.0, 'size': 0.0, 'settlement_price': 1627.47, 'realized_profit_loss': 0.0, 'open_orders_margin': 1.3333e-05, 'mark_price': 1627.03, 'maintenance_margin': 0.0, 'leverage': 50, 'kind': 'future', 'instrument_name': 'ETH-27JAN23', 'initial_margin': 0.0, 'index_price': 1626.3, 'floating_profit_loss': 0.0, 'estimated_liquidation_price': 249416.29, 'direction': 'zero', 'delta': 0.0, 'average_price': 0.0}], 
                    'open_orders': [
                        {'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1500.0, 'post_only': False, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31317764631', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1674385583444, 'label': '', 'is_liquidation': False, 'instrument_name': 'ETH-27JAN23', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1674385583444, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 1.0}
                        ]
perp = 1528.35
fut = 1545.58
delta = fut - perp
print ( ([o for o in my_trades_open if  str(1674134456)  in o['label'] ]))