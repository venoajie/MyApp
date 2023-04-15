# -*- coding: utf-8 -*-
import strategies.grid_perpetual as grid
import asyncio
import pytest


my_trades_open = {
    'all': [
        {'id': 1, 'data': '{"trade_seq":122628217,"trade_id":"ETH-166736294","timestamp":1681359527286,"tick_direction":1,"state":"filled","self_trade":false,"risk_reducing":false,"reduce_only":false,"profit_loss":0.0,"price":1940.7,"post_only":true,"order_type":"limit","order_id":"ETH-32845591518","mmp":false,"matching_id":null,"mark_price":1940.67,"liquidity":"M","label":"hedgingSpot-open-1681359527286","instrument_name":"ETH-PERPETUAL","index_price":1940.06,"fee_currency":"ETH","fee":0.0,"direction":"sell","api":false,"amount":70.0}'},
        {'id': 60, 'data': '{"trade_seq":122793232,"trade_id":"ETH-166947107","timestamp":1681447691857,"tick_direction":2,"state":"filled","self_trade":false,"risk_reducing":false,"reduce_only":false,"profit_loss":-9.23e-05,"price":2116.85,"post_only":true,"order_type":"limit","order_id":"ETH-32867483737","mmp":false,"matching_id":null,"mark_price":2117.09,"liquidity":"M","label":"every4hoursLong-open-1681447421981","instrument_name":"ETH-PERPETUAL","index_price":2117.01,"fee_currency":"ETH","fee":0.0,"direction":"buy","api":true,"amount":3.0}', 'trade_seq': 122793232, 'order_id': 'ETH-32867483737', 'label_main': 'every4hoursLong-open-1681447421981', 'amount_dir': 3.0}
         ],
    'list_data_only': [
        {'trade_seq': 122628217, 'trade_id': 'ETH-166736294', 'timestamp': 1681359527286, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1940.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32845591518', 'mmp': False, 'matching_id': None, 'mark_price': 1940.67, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681359527286', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1940.06, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 70.0
         },
        {'trade_seq': 122793232, 'trade_id': 'ETH-166947107', 'timestamp': 1681447691857, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.23e-05, 'price': 2116.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32867483737', 'mmp': False, 'matching_id': None, 'mark_price': 2117.09, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681447421981', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2117.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}
        ]
    }
                           
                           
                           
orders_from_sqlite = []
notional= 78
active_trade_item = [{'trade_seq': 122793232, 'trade_id': 'ETH-166947107', 'timestamp': 1681447691857, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.23e-05, 'price': 2116.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32867483737', 'mmp': False, 'matching_id': None, 'mark_price': 2117.09, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681447421981', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2117.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}]
strategy_from_config = 'every4hoursLong'

grid = grid.GridPerpetual(
                          active_trade_item, 
                          strategy_from_config
                          )

@pytest.mark.asyncio
async def test_get_strategy_from_active_trade_item():
    result = await grid.get_strategy_from_active_trade_item()   
    assert result['main'] == 'every4hoursLong'    
    assert result['transaction_net'] == 'every4hoursLong-1681447421981'