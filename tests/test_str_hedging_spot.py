# -*- coding: utf-8 -*-
import pytest

from strategies.hedging_spot import (
    get_timing_factor,
    get_waiting_time_factor,
    max_order_stack_has_not_exceeded,
    net_size_of_label,
    net_size_not_over_bought
    )


my_trades_currency_strategy = [{'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-closed-1728806470451', 'amount': 3.0, 'price': 2466.25, 'side': 'buy'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-open-1728860066787', 'amount': -5.0, 'price': 2465.55, 'side': 'sell'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-closed-1728806470451', 'amount': 3.0, 'price': 2466.4, 'side': 'buy'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-open-1728859651166', 'amount': -5.0, 'price': 2465.65, 'side': 'sell'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-closed-1728806470451', 'amount': 3.0, 'price': 2466.45, 'side': 'buy'},{'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-closed-1728806470451', 'amount': 3.0, 'price': 2466.55, 'side': 'buy'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-open-1728806470451', 'amount': -2.0, 'price': 2466.6, 'side': 'sell'}, {'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-open-1728806470451', 'amount': -3.0, 'price': 2466.6, 'side': 'sell'}]

transaction = [{'instrument_name': 'ETH-PERPETUAL', 'label': 'hedgingSpot-open-1728806470451', 'amount': -3.0, 'price': 2466.6, 'side': 'sell'}][0]

@pytest.mark.parametrize("my_trades_currency_strategy, transaction, expected", [
    (my_trades_currency_strategy, transaction, 7),
    ])
def test_net_size_of_label (my_trades_currency_strategy,
                            transaction,
                            expected):
    
    result = net_size_of_label(my_trades_currency_strategy, 
                               transaction)

    assert result == expected

@pytest.mark.parametrize("my_trades_currency_strategy, transaction, expected", [
    (my_trades_currency_strategy, transaction, False),
    ])
def test_net_size_not_over_bought (my_trades_currency_strategy,
                            transaction,
                            expected):
    

    result = net_size_not_over_bought(my_trades_currency_strategy, 
                               transaction)

    assert result == expected

hedging_attributes= [{'strategy_label': 'hedgingSpot', 'is_active': True, 
                      'contribute_to_hedging': True, 'cancellable': True, 
                      'side': 'sell', 'take_profit_pct': 0, 'settlement_period': ['perpetual'], 
                      'weighted_factor': {'minimum': 1, 'medium': 5, 'extreme': 10, 'flash_crash': 20}, 
                      'waiting_minute_before_cancel': 3, 'halt_minute_before_reorder': 240, 
                      'max_leverage': 1, 'delta_price_pct': 0.005, 
                      'sub_account_max_open_orders': {'per_instrument': 50, 'total': 200}}]
weighted_factor= hedging_attributes[0]["weighted_factor"]
waiting_minute_before_cancel= hedging_attributes[0]["waiting_minute_before_cancel"]


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

