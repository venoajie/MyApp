#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
from pathlib import Path

# installed
from loguru import logger as log
from rocketry import Rocketry
from rocketry.conds import  every
from loguru import logger as log
import requests

# user defined formula
from utilities import pickling, formula, system_tools
from market_data import get_market_data

symbol = 'ETH-PERPETUAL'
currency = 'ETH'
market_data =  get_market_data.MarketData(currency, symbol)

app = Rocketry(config={'task_execution': 'async',
                       'restarting': 'relaunch',
                       'cycle_sleep': 1})

root = Path(".")


def get_currencies () -> float:
    """
    """

    endpoint=(f'https://test.deribit.com/api/v2/public/get_currencies?')
    return  requests.get(endpoint).json() ['result']

def get_instruments (currency) -> float:
    """
    """

    endpoint=(f'https://test.deribit.com/api/v2/public/get_instruments?currency={currency}')
    return  requests.get(endpoint).json() ['result']
    
    
@app.task(every("3600 seconds"))
def check_and_save_every_60_minutes ():
        
    try:
               
        currencies = get_currencies ()
        currencies = ['ETH', 'BTC']
        for currency in currencies:
            instruments = get_instruments (currency)
            my_path_instruments= system_tools.provide_path_for_file ('instruments',currency) 
            pickling.replace_data(my_path_instruments, instruments)
            
        my_path_cur = system_tools.provide_path_for_file ('currencies' ) 
        pickling.replace_data(my_path_cur, currencies)
        
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())
        
#@app.task(every("5 seconds"))
def check_and_save_every_30_seconds ():
        
    try:
        from synchronizing_files import main
        import asyncio
        
        print ('AAAAAAA')
        asyncio.get_event_loop().run_until_complete(main())
        print ('c')
        
                
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())

@app.task(every("300 seconds"))
def check_and_save_every_5_minutes ():
        
    try:
        # https://towardsdatascience.com/understand-async-await-with-asyncio-for-asynchronous-programming-in-python-e0bc4d25808e       
        open_interest_historical = market_data. open_interest_historical ()
        my_path = system_tools.provide_path_for_file ('openInterestHistorical', currency.lower()) 
        pickling.replace_data(my_path, open_interest_historical)
        
        open_interest_symbol = market_data. open_interest_symbol ()
        file_name =(f'{currency.lower()}-openInterestSymbol.pkl')
        my_path = system_tools.provide_path_for_file ('openInterestHistorical', currency.lower())
        pickling.replace_data(my_path, open_interest_symbol)
        
        open_interest_aggregated_ohlc = market_data. open_interest_aggregated_ohlc ()
        my_path = system_tools.provide_path_for_file ('openInterestAggregated', currency.lower())
        pickling.replace_data(my_path, open_interest_aggregated_ohlc)
        
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())

if __name__ == "__main__":
    
    try:

        app.run()
#        check_and_save_every_30_seconds ()
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        
        formula.log_error('open interest','open interest main', error, 10)
        
