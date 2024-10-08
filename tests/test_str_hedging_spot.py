# -*- coding: utf-8 -*-
import pytest

from strategies.hedging_spot import (
    get_timing_factor,
    get_waiting_time_factor,
    max_order_stack_has_not_exceeded
    )

from strategies.config_strategies import hedging_spot_attributes

hedging_attributes= [{'strategy_label': 'hedgingSpot', 'is_active': True, 
                      'contribute_to_hedging': True, 'cancellable': True, 
                      'side': 'sell', 'take_profit_pct': 0, 'settlement_period': ['perpetual'], 
                      'weighted_factor': {'minimum': 1, 'medium': 5, 'extreme': 10, 'flash_crash': 20}, 
                      'waiting_minute_before_cancel': 3, 'halt_minute_before_reorder': 240, 
                      'max_leverage': 1, 'delta_price_pct': 0.005, 
                      'sub_account_max_open_orders': {'per_instrument': 50, 'total': 200}}]
weighted_factor= hedging_attributes["weighted_factor"]
waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"]


@pytest.mark.parametrize("strong_fluctuation, some_fluctuation, expected", [
    (True, True, 53999.99999999999),
    (True, False,53999.99999999999),
    (False, True,107999.99999999999 ),
    (False, False,180000)
    ])
def test_get_timing_factor (strong_fluctuation,
                            some_fluctuation,
                            expected):
    
    result = get_timing_factor(strong_fluctuation, 
                               some_fluctuation,
                               waiting_minute_before_cancel,)

    assert result == expected


@pytest.mark.parametrize("strong_fluctuation, some_fluctuation, expected", [
    (True, True,.1),
    (True, False,.1),
    (False, True,.05),
    (False, False,.010)
    ])
def test_get_waiting_time_factor (strong_fluctuation,
                                  some_fluctuation,
                                  expected):
    
    result = get_waiting_time_factor(weighted_factor, 
                                      strong_fluctuation,
                                      some_fluctuation,)

    assert result == expected


@pytest.mark.parametrize("len_orders, strong_market, expected", [
    (0, True,True),
    (0, False,True),
    (1, True,True),
    (1, False,False),
    (2, True,True),
    (100, True,True),
    ])
def test_max_order_stack_has_not_exceeded (len_orders, 
                                           strong_market,
                                           expected):
    
    result = max_order_stack_has_not_exceeded(len_orders, 
                                              strong_market)

    assert result == expected

