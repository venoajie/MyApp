# -*- coding: utf-8 -*-
import pytest

from strategies.hedging_spot import (
    get_timing_factor,
    get_waiting_time_factor,
    )
from strategies.config_strategies import hedging_spot_attributes

hedging_attributes= hedging_spot_attributes()[0]
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

