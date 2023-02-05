# -*- coding: utf-8 -*-
from src.risk_management import check_data_integrity
import asyncio
import pytest

currency = 'eth'
sub_account =  [
    {'uid': 148510, 
     'positions': [
        {
            'total_profit_loss': -0.002762959, 'size_currency': -0.047291778, 'size': -77.0, 
            'settlement_price': 1627.85, 'realized_profit_loss': 3.281e-06, 'realized_funding': 3e-06, 
            'open_orders_margin': 0.0, 'mark_price': 1628.19, 'maintenance_margin': 0.000472927, 
            'leverage': 50, 'kind': 'future', 'interest_value': 1.2362947991316013, 'instrument_name': 'ETH-PERPETUAL', 
            'initial_margin': 0.000945844, 'index_price': 1626.72, 'floating_profit_loss': -1.0519e-05, 
            'estimated_liquidation_price': 249665.11, 'direction': 'sell', 'delta': -0.047291778, 'average_price': 1538.32
            }
        ], 
     'open_orders': []
     }
    ]

positions_from_get = sub_account [0] ['positions']
my_trades_open_from_recov_db = [
    {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3,
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 
     'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 
     'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880',
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, 
    {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 
     'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 
     'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, 
    {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 
     'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0},
    {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 
     'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0},
    {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False,
     'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971',
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 115462030, 'trade_id': 'ETH-157558753', 'timestamp': 1674155737379, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1543.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31274547473', 'mmp': False, 
     'matching_id': None, 'mark_price': 1544.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674155736', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1543.3, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},
    {'trade_seq': 116295592, 'trade_id': 'ETH-158666464', 'timestamp': 1675218407734, 'tick_direction': 0, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1582.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31482969205', 'mmp': False, 
     'matching_id': None, 'mark_price': 1583.14, 'liquidity': 'M', 'label': 'hedgingSpot-open-1675218347', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1583.0, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 115446012, 'trade_id': 'ETH-157539722', 'timestamp': 1674139209708, 'tick_direction': 1, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269845803', 'mmp': False, 
     'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134451', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0}, 
    {'trade_seq': 115510211, 'trade_id': 'ETH-157618892', 'timestamp': 1674225740729, 'tick_direction': 1, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00024158, 'price': 1565.5, 'post_only': False, 'order_type': 'market', 'order_id': 'ETH-31284611840', 'mmp': False, 'matching_id': None, 'mark_price': 1562.91, 'liquidity': 'M', 'label': 'supplyDemandShort15-closed-1674134451', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1562.66, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 37.0}, 
    {'trade_seq': 115446013, 'trade_id': 'ETH-157539723', 'timestamp': 1674139209708, 'tick_direction': 1, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
     'price': 1538.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269847666', 'mmp': False, 
     'matching_id': None, 'mark_price': 1535.96, 'liquidity': 'M', 'label': 'supplyDemandShort15-open-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1535.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 37.0}, 
    {'trade_seq': 115457369, 'trade_id': 'ETH-157553296', 'timestamp': 1674150736302, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 1.92e-05,
     'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 
     'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'M', 'label': 'supplyDemandShort15-closed-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 10.0}, 
    {'trade_seq': 115457373, 'trade_id': 'ETH-157553300', 'timestamp': 1674150736302, 'tick_direction': 3, 
     'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': True, 'profit_loss': 5.185e-05, 
     'price': 1528.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31271624875', 'mmp': False, 
     'matching_id': None, 'mark_price': 1527.79, 'liquidity': 'T', 'label': 'supplyDemandShort15-closed-1674134456', 
     'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.41, 'fee_currency': 'ETH', 'fee': 8.83e-06, 'direction': 'buy', 'api': True, 'amount': 27.0}
    ]

my_selected_trades_open_from_system = []

trade_integrity =  check_data_integrity.CheckTradeIntegrity (currency,
                                                            positions_from_get,
                                                            my_trades_open_from_recov_db,
                                                            my_selected_trades_open_from_system
                                                                )

my_trades_open_from_recov_db_none = []
positions_from_get_none = []
trade_integrity_both_none =  check_data_integrity.CheckTradeIntegrity (currency,
                                                                        positions_from_get_none,
                                                                        my_trades_open_from_recov_db_none,
                                                                        my_selected_trades_open_from_system
                                                                        )
trade_integrity_recov_none =  check_data_integrity.CheckTradeIntegrity (currency,
                                                                        positions_from_get,
                                                                        my_trades_open_from_recov_db_none,
                                                                        my_selected_trades_open_from_system
                                                                        )
trade_integrity_pos_none =  check_data_integrity.CheckTradeIntegrity (currency,
                                                                        positions_from_get_none,
                                                                        my_trades_open_from_recov_db,
                                                                        my_selected_trades_open_from_system
                                                                        )

@pytest.mark.asyncio
async def test_compare_inventory_per_db_vs_get():
    
    assert await trade_integrity.compare_inventory_per_db_vs_get() == 0   
    assert await trade_integrity_both_none.compare_inventory_per_db_vs_get() == 0    
    assert await trade_integrity_pos_none.compare_inventory_per_db_vs_get() == -77    
    assert await trade_integrity_recov_none.compare_inventory_per_db_vs_get() == 77

@pytest.mark.asyncio    
async def test_time_stamp_to_recover():
    
    assert await check_data_integrity.time_stamp_to_recover(my_trades_open_from_recov_db) == 1674106201606   
    assert await check_data_integrity.time_stamp_to_recover(None) == []    
    assert await check_data_integrity.time_stamp_to_recover([]) == []