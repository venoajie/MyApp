from typing import Dict, List

my_trades_open = [{'trade_seq': 12031891, 'trade_id': 'ETH-16793185', 'timestamp': 1672222851131, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1196.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3174986056', 'mmp': False, 'matching_id': None, 'mark_price': 1196.8, 'liquidity': 'M', 'label': 'hedging spot-open-1672222839839', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1196.53, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 28.0}, {'trade_seq': 12031893, 'trade_id': 'ETH-16793195', 'timestamp': 1672223686264, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1195.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3175032592', 'mmp': False, 'matching_id': None, 'mark_price': 1195.44, 'liquidity': 'M', 'label': 'hedging spot-open-1672223656695', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1195.4, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 28.0}, {'trade_seq': 12031894, 'trade_id': 'ETH-16793203', 'timestamp': 1672224106415, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1194.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3175052850', 'mmp': False, 'matching_id': None, 'mark_price': 1194.95, 'liquidity': 'M', 'label': 'hedging spot-open-1672223980660', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1194.89, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}]

index = [{'timestamp': 1672226421451, 'price': 1195.52, 'index_name': 'eth_usd'}]
port = [{'total_pl': -3e-06, 'session_upl': -3e-06, 'session_rpl': -0.000185, 'projected_maintenance_margin': 0.003264, 'projected_initial_margin': 0.003917, 'projected_delta_total': -0.023408, 'portfolio_margining_enabled': True, 'options_vega': 0.0, 'options_value': 0.0, 'options_theta': 0.0, 'options_session_upl': 0.0, 'options_session_rpl': 0.0, 'options_pl': 0.0, 'options_gamma': 0.0, 'options_delta': 0.0, 'margin_balance': 0.078, 'maintenance_margin': 0.003264, 'initial_margin': 0.003917, 'futures_session_upl': -3e-06, 'futures_session_rpl': -0.000185, 'futures_pl': -3e-06, 'fee_balance': 0.0, 'equity': 0.078, 'delta_total_map': {'eth_usd': -0.023407848}, 'delta_total': -0.023408, 'currency': 'ETH', 'balance': 0.078187, 'available_withdrawal_funds': 0.074082, 'available_funds': 0.074083}]
trade = [{'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1196.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3175186057', 'mmp': False, 'max_show': 28.0, 'last_update_timestamp': 1672226215264, 'label': 'hedging spot-open-1672226215210', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1672226215264, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 28.0}]

print (isinstance(index, Dict))
print (isinstance(index, dict))
print (isinstance(port, Dict))
print (isinstance(port, dict))
print (isinstance(trade, Dict))
print (isinstance(index, List))
print (isinstance(port, List))
print (isinstance(trade, List))



sum_open_trading_after_new_closed_trading = sum([o['amount'] for o in my_trades_open  ])
print(sum_open_trading_after_new_closed_trading)
print(my_trades_open[0])
