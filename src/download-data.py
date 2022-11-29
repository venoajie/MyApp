#!/usr/bin/env python
# -*- coding: utf-8 -*-

# installed
from loguru import logger as log
from rocketry import Rocketry
from rocketry.conds import scheduler_running, after_success, after_success,daily, every, minutely, hourly

# user defined formula
from utils import formula
from market_data import open_interests


app = Rocketry(config={'task_execution': 'async',
                       'restarting': 'relaunch',
                       'cycle_sleep': 1})
    
@app.task(every("300 seconds"))
def check_and_save_every_5_minutes ():
    from utils import pickling
        
    try:
        open_interest =  open_interests.OpenInterest('ETH')
        
        open_interest_historical = open_interest. open_interest_historical ()
        pickling.replace_data('open_interest_historical.pkl', open_interest_historical)
        
        open_interest_symbol = open_interest. open_interest_symbol ()
        pickling.replace_data('open_interest_symbol.pkl', open_interest_symbol)
        
        open_interest_aggregated_ohlc = open_interest. open_interest_aggregated_ohlc ()
        pickling.replace_data('open_interest_aggregated_ohlc.pkl', open_interest_aggregated_ohlc)
        
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())

if __name__ == "__main__":
    
    try:

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
        