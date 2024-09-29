# -*- coding: utf-8 -*-
import pytest


from strategies.basic_strategy import (
    positions_and_orders,
    proforma_size,
    are_size_and_order_appropriate)


@pytest.mark.parametrize("current_size_or_open_position, current_orders_size, expected", [
    (-100, -10, -110),
    (100, -10, 90),])
def test_positions_and_orders(current_size_or_open_position, 
                                      current_orders_size,
                                      expected):
    
    result = positions_and_orders(current_size_or_open_position, 
                                      current_orders_size,)

    assert result == expected


@pytest.mark.parametrize("current_size_or_open_position, current_orders_size, next_orders_size, expected", [
    (-100, -10, -10, -120),
    (100, -10, 10, 100),])
def test_proforma_size_add(current_size_or_open_position, 
                           current_orders_size,
                           next_orders_size,
                           expected):

    result = proforma_size(current_size_or_open_position, 
                                      current_orders_size,
                                      next_orders_size,)

    assert result == expected

@pytest.mark.parametrize("purpose, current_size_or_open_position, current_orders_size, next_orders_size, max_position, expected", [
    ("add_position",-100, -10, -10, -100, False),
    ("add_position",0, 10, 10, 100, True),
    ("add_position",0, 0, -10, -100, True),
    ("reduce_position",0, -10, 10, 100, False),
    ("reduce_position",0, -10, 10, -100, False),
    ("reduce_position",-100, 0, 10, 100, True),])
def test_are_size_and_order_appropriate(purpose,
                                        current_size_or_open_position, 
                                        current_orders_size,
                                        next_orders_size,
                                        max_position,
                                        expected):

    result = are_size_and_order_appropriate(purpose,
                                             current_size_or_open_position, 
                                             current_orders_size, 
                                             next_orders_size,
                                             max_position)

    assert result == expected

