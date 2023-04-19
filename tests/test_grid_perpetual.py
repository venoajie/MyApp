# -*- coding: utf-8 -*-
import strategies.grid_perpetual as grid
import asyncio
import pytest


my_trades_open = {
    'all': [
        {'id': 1, 'data': '{"trade_seq":122628217,"trade_id":"ETH-166736294","timestamp":1681359527286,"tick_direction":1,"state":"filled","self_trade":false,"risk_reducing":false,"reduce_only":false,"profit_loss":0.0,"price":1940.7,"post_only":true,"order_type":"limit","order_id":"ETH-32845591518","mmp":false,"matching_id":null,"mark_price":1940.67,"liquidity":"M","label":"hedgingSpot-open-1681359527286","instrument_name":"ETH-PERPETUAL","index_price":1940.06,"fee_currency":"ETH","fee":0.0,"direction":"sell","api":false,"amount":70.0}',  'trade_seq': 122628217, 'order_id': 'ETH-32845591518', 'label_main': 'hedgingSpot-open-1681359527286', 'amount_dir': -70.0},
        {'id': 60, 'data': '{"trade_seq":122793232,"trade_id":"ETH-166947107","timestamp":1681447691857,"tick_direction":2,"state":"filled","self_trade":false,"risk_reducing":false,"reduce_only":false,"profit_loss":-9.23e-05,"price":2116.85,"post_only":true,"order_type":"limit","order_id":"ETH-32867483737","mmp":false,"matching_id":null,"mark_price":2117.09,"liquidity":"M","label":"every4hoursLong-open-1681447421981","instrument_name":"ETH-PERPETUAL","index_price":2117.01,"fee_currency":"ETH","fee":0.0,"direction":"buy","api":true,"amount":3.0}', 'trade_seq': 122793232, 'order_id': 'ETH-32867483737', 'label_main': 'every4hoursLong-open-1681447421981', 'amount_dir': 3.0}
         ],
    'list_data_only': [
        {'trade_seq': 122628217, 'trade_id': 'ETH-166736294', 'timestamp': 1681359527286, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1940.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32845591518', 'mmp': False, 'matching_id': None, 'mark_price': 1940.67, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681359527286', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1940.06, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 70.0
         },
        {'trade_seq': 122793232, 'trade_id': 'ETH-166947107', 'timestamp': 1681447691857, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.23e-05, 'price': 2116.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32867483737', 'mmp': False, 'matching_id': None, 'mark_price': 2117.09, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681447421981', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2117.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}
        ]
    }
                           
orders_from_sqlite = {
        'all': [
            {'id': 1, 'data': '{"web":false,"time_in_force":"good_til_cancelled","risk_reducing":false,"replaced":false,"reject_post_only":false,"reduce_only":false,"profit_loss":0.0,"price":2102.6,"post_only":true,"order_type":"limit","order_state":"open","order_id":"ETH-32892551162","mmp":false,"max_show":1.0,"last_update_timestamp":1681568392117,"label":"every5mtestLong-open-1681568392078","is_liquidation":false,"instrument_name":"ETH-PERPETUAL","filled_amount":0.0,"direction":"buy","creation_timestamp":1681568392117,"commission":0.0,"average_price":0.0,"api":true,"amount":1.0}', 'order_id': 'ETH-32892551162', 'label_main': 'every5mtestLong-open-1681568392078', 'amount_dir': 1.0}, 
            {'id': 2, 'data': '{"web":false,"time_in_force":"good_til_cancelled","risk_reducing":false,"replaced":false,"reject_post_only":false,"reduce_only":false,"profit_loss":0.0,"price":2102.6,"post_only":true,"order_type":"limit","order_state":"open","order_id":"ETH-32892551169","mmp":false,"max_show":1.0,"last_update_timestamp":1681568392163,"label":"every5mtestLong-open-1681568392126","is_liquidation":false,"instrument_name":"ETH-PERPETUAL","filled_amount":0.0,"direction":"buy","creation_timestamp":1681568392163,"commission":0.0,"average_price":0.0,"api":true,"amount":1.0}', 'order_id': 'ETH-32892551169', 'label_main': 'every5mtestLong-open-1681568392126', 'amount_dir': 1.0}], 
        'list_data_only': [
            {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2102.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-32892551162', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1681568392117, 'label': 'every5mtestLong-open-1681568392078', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1681568392117, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2102.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-32892551169', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1681568392163, 'label': 'every5mtestLong-open-1681568392126', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1681568392163, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}]}
notional= 78
active_trade_item = [{'trade_seq': 122793232, 'trade_id': 'ETH-166947107', 'timestamp': 1681447691857, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.23e-05, 'price': 2116.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32867483737', 'mmp': False, 'matching_id': None, 'mark_price': 2117.09, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681447421981', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2117.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}]

strategy_from_config = 'every4hoursLong'

grids = grid.GridPerpetual(my_trades_open,
                           orders_from_sqlite
                           )
strategy_from_config_none = None

grid_str_none = grid.GridPerpetual(my_trades_open,
                                   orders_from_sqlite
                                   )
#active_trade_item_none = None
grid_act_trd_none = grid.GridPerpetual(my_trades_open,
                                       orders_from_sqlite
                                       )
@pytest.mark.asyncio
async def test_get_params_orders_closed():
    best_bid_prc= 2095
    best_ask_prc= 2140
    active_trade_item = [{'trade_seq': 122793232, 'trade_id': 'ETH-166947107', 'timestamp': 1681447691857, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.23e-05, 'price': 2116.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32867483737', 'mmp': False, 'matching_id': None, 'mark_price': 2117.09, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681447421981', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2117.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 3.0}]
    
    result = await grids.get_params_orders_closed(active_trade_item, best_bid_prc, best_ask_prc)   
    assert result  ==  {'instrument': 'ETH-PERPETUAL', 'label': 'every4hoursLong-closed-1681447421981', 'side': 'sell', 'size': 3.0, 'type': 'limit', 'price_threshold': 2138.0185, 'len_order_limit': 0, 'entry_price': 2140, 'order_buy': False, 'order_sell': True}
    
    best_ask_prc= 2138
    result = await grids.get_params_orders_closed(active_trade_item, best_bid_prc, best_ask_prc)   
    assert result  ==  {'instrument': 'ETH-PERPETUAL', 'label': 'every4hoursLong-closed-1681447421981', 'side': 'sell', 'size': 3.0, 'type': 'limit', 'price_threshold': 2138.0185, 'len_order_limit': 0, 'entry_price': 2138, 'order_buy': False, 'order_sell': False}
    
    active_trade_item = [{'trade_seq': 122993401, 'trade_id': 'ETH-167190562', 'timestamp': 1681598206591, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2095.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32897249916', 'mmp': False, 'matching_id': None, 'mark_price': 2095.88, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681598206591', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2095.65, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}]
    result = await grids.get_params_orders_closed(active_trade_item, best_bid_prc, best_ask_prc)   

    best_bid_prc= 2095
    best_ask_prc= 2140
    active_trade_item = [{'trade_seq': 122993401, 'trade_id': 'ETH-167190562', 'timestamp': 1681598206591, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2095.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32897249916', 'mmp': False, 'matching_id': None, 'mark_price': 2095.88, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681598206591', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2095.65, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}]
    
    result = await grids.get_params_orders_closed(active_trade_item, best_bid_prc, best_ask_prc)    
    assert result  ==  {'instrument': 'ETH-PERPETUAL', 'label': 'every4hoursShort-closed-1681598206591', 'side': 'buy', 'size': 3.0, 'type': 'limit', 'price_threshold': 2074.9410000000003, 'len_order_limit': 0, 'entry_price': 2095, 'order_buy': False, 'order_sell': False}
    
    best_bid_prc= 2074
    result = await grids.get_params_orders_closed(active_trade_item, best_bid_prc, best_ask_prc)    
    assert result  ==  {'instrument': 'ETH-PERPETUAL', 'label': 'every4hoursShort-closed-1681598206591', 'side': 'buy', 'size': 3.0, 'type': 'limit', 'price_threshold': 2074.9410000000003, 'len_order_limit': 0, 'entry_price': 2074, 'order_buy': True, 'order_sell': False}
        
@pytest.mark.asyncio
async def test_open_orders_as_per_main_label():
    label_main = 'every5mtestLong-open-1681568392078'
    result = await grids.open_orders_as_per_main_label(label_main)   
    assert result['len_result']  ==  2
    label_main = 'every1hoursLong-open-1681568392126'
    result = await grids.open_orders_as_per_main_label(label_main)   
    assert result['len_result']  ==  0
        
@pytest.mark.asyncio
async def test_get_closed_label():
    label_main = 'every5mtestLong-open-1681568392078'
    result = await grids.get_closed_label(label_main)
    assert result   ==  'every5mtestLong-closed-1681568392078'
    
@pytest.mark.asyncio
async def test_adjusting_size_open_order():
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -18
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  4
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -14
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  3
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -11
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  2
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -9
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  2
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -7
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  2
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -5
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  2
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -3
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  2
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -1
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  1
    
    current_side= 'buy'
    current_proposed_size= 1
    current_net_position_size= -2
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   ==  1
    
    current_side= 'sell'
    current_proposed_size= 1
    current_net_position_size= 18
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   == 4
    
    current_side= 'sell'
    current_proposed_size= 1
    current_net_position_size= 1
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   == 1
    
    current_side= 'sell'
    current_proposed_size= 1
    current_net_position_size= 3
    result = await grids.adjusting_size_open_order(current_side, current_proposed_size, current_net_position_size)
    assert result   == 2
    