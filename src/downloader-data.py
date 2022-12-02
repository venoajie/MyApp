#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
from pathlib import Path
from datetime import datetime

# installed
from loguru import logger as log
from rocketry import Rocketry
from rocketry.conds import  every

# user defined formula
from utils import formula, pickling
from market_data import get_market_data

symbol = 'ETH-PERPETUAL'
currency = 'ETH'
market_data =  get_market_data.MarketData(currency, symbol)

app = Rocketry(config={'task_execution': 'async',
                       'restarting': 'relaunch',
                       'cycle_sleep': 1})

root = Path(".")

@app.task(every("300 seconds"))
def check_and_save_every_5_minutes ():
        
    try:
               
        open_interest_historical = market_data. open_interest_historical ()
        file_name =(f'{currency.lower()}-openInterestHistorical.pkl')
        my_path = root / "market_data" / file_name
        pickling.replace_data(my_path, open_interest_historical)
        
        open_interest_symbol = market_data. open_interest_symbol ()
        file_name =(f'{currency.lower()}-openInterestSymbol.pkl')
        my_path = root / "market_data" / file_name
        pickling.replace_data(my_path, open_interest_symbol)
        
        open_interest_aggregated_ohlc = market_data. open_interest_aggregated_ohlc ()
        file_name =(f'{currency.lower()}-openInterestAggregated.pkl')
        my_path = root / "market_data" / file_name
        pickling.replace_data(my_path, open_interest_aggregated_ohlc)
        
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())

if __name__ == "__main__":
    
    try:

        #check_and_save_every_1_minutes()
        app.run()
        #check_and_save_every_5_minutes()
        #formula.sleep_and_restart_program (600)
                
        #file_name = 'TRXBTC_1h.bin'
        #home_path = str(pathlib.Path.home())
        #data_path = os.path.join(home_path, file_name)
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        
        formula.log_error('open interest','open interest main', error, 10)
        
