# -*- coding: utf-8 -*-
from src.utilities import time_modification
from src.market_understanding import futures_analysis

def  test_combining_individual_futures_analysis():
    index_price = 10.0
    expiration = '2023-02-01 00:00:00'
    expiration_timestamp = time_modification.convert_time_to_unix (expiration)
    future = {'maker_commission': -0.01, 
              'expiration_timestamp': expiration_timestamp
              }
    ticker = {'instrument_name': 'BTC-PERPETUAL', 
              'mark_price': 10.1
              }
    expected = [{'instrument_name': 'BTC-PERPETUAL', 
                 'with_rebates': True, 
                 'market_expectation': 'contango',
                 'mark_price': 10.1, 
                 'ratio_price_to_index': 0.009999999999999964,
                 'remaining_active_time_in_hours': -5.91 
                 }
                ] [0]
    fut_analysis = futures_analysis.combining_individual_futures_analysis (index_price, 
                                                                   future, 
                                                                   ticker
                                                                   ) [0]
    assert fut_analysis ['instrument_name'] == expected ['instrument_name']
    assert fut_analysis ['with_rebates'] == expected ['with_rebates']
    assert fut_analysis ['market_expectation'] == expected ['market_expectation']
    assert fut_analysis ['ratio_price_to_index'] == expected ['ratio_price_to_index']
