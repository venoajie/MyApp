# -*- coding: utf-8 -*-

from strategies.basic_strategy import (
    positions_and_orders_add,
    proforma_size_add,
    are_size_and_order_appropriate_to_add_position)


def test_positions_and_orders_add():
    
    #with notional
    current_size_or_open_position = -100
    current_orders_size = 10

    result = positions_and_orders_add(current_size_or_open_position, 
                                      current_orders_size,)

    assert result == False


def test_proforma_size_add():
    
    #with notional
    current_size_or_open_position = -100
    current_orders_size = 10
    next_orders_size = 10 

    result = proforma_size_add(current_size_or_open_position, 
                                      current_orders_size,)

    assert result == False

def test_proforma_size_add():
    
    #with notional
    current_size_or_open_position = -100
    current_orders_size = 10
    next_orders_size = 10 
    notional = 100
    next_orders_size = 10 

    result = are_size_and_order_appropriate_to_add_position(current_size_or_open_position, 
                                                            current_orders_size, 
                                                            next_orders_size)

    assert result == False
