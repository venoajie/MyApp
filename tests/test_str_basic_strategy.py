# -*- coding: utf-8 -*-
import pytest


from strategies.basic_strategy import (
    check_if_next_closing_size_will_not_exceed_the_original,
    positions_and_orders,
    proforma_size,
    are_size_and_order_appropriate)


@pytest.mark.parametrize("basic_size, net_size, next_size, expected", [
    ( -10, 0, 10, True),
    ( 10, 0, -10, True),
    ( -10, 6, 4, True),
    ( -10, 4, 6, True),
    ( -10, 6, -1, False),
    ( -10, -6, -16, False),
    ( 10, 6, 16, False),
    ( -10, 11, 1, False),
    ( 10, -11,- 1, False),
    ])
def test_check_if_closing_size_will_not_exceed_the_original(basic_size, 
                                                        net_size,
                                                        next_size,
                                                        expected):

    result = check_if_next_closing_size_will_not_exceed_the_original(basic_size, 
                                                            net_size,
                                                            next_size,)

    assert result == expected


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
    ("reduce_position",-50, 0, -10, None, False),
    ("reduce_position",-50, 0, 10, None, True),
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

