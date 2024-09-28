# -*- coding: utf-8 -*-
import pytest

from strategies.basic_strategy import (
    positions_and_orders_add,
    proforma_size_add,
    are_size_and_order_appropriate_to_add_position)

@pytest.mark.parametrize("current_size_or_open_position, current_orders_size, expected", [
    (-100, 10, 90),
    (100, 10, 110),])
def test_positions_and_orders_add(current_size_or_open_position, 
                                      current_orders_size,
                                      expected):
    
    result = positions_and_orders_add(current_size_or_open_position, 
                                      current_orders_size,)

    assert result == expected


def test_proforma_size_add():
    
    #with notional
    current_size_or_open_position = -100
    current_orders_size = 10
    next_orders_size = 10 

    result = proforma_size_add(current_size_or_open_position, 
                                      current_orders_size,
                                      next_orders_size,)

    assert result == 90

def test_proforma_size_add():
    
    #with notional
    positive_current_size_or_open_position = 100
    negative_current_size_or_open_position = -100
    current_orders_size = 0
    next_orders_size = 0
    notional = 100
    next_orders_size = 10 

    result = are_size_and_order_appropriate_to_add_position(positive_current_size_or_open_position, 
                                                            current_orders_size, 
                                                            next_orders_size)

    assert result == True

    result = are_size_and_order_appropriate_to_add_position(negative_current_size_or_open_position, 
                                                            current_orders_size, 
                                                            next_orders_size)

    assert result == False
