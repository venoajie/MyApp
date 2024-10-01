# -*- coding: utf-8 -*-
import pytest

from strategies.hedging_spot import (
    max_order_stack_has_not_exceeded
    )

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

