#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from loguru import logger as log
from functools import lru_cache
from utils import formula
from dask import delayed, compute    
from unsync import unsync
from db_management import sqlite_operation

@unsync        
def query_ohlc_max_date_ (ohlc_table: str)-> object:

    '''
    # default = underlying/perpetual/spot
    
    '''        

    ohlc_table = ohlc_table.replace('-', '_')
    query_table = f'SELECT MAX ((date)) FROM {ohlc_table}' 
    
    with sqlite_operation.db_ops() as cur:
        try:
            result = (list(cur.execute((f'{query_table}'))))     [0][0]
        except:
            result = []
            
        return 0 if (result ==[] or  result == None ) else  int (result) # https://stackoverflow.com/questions/29311819/how-to-convert-tuple-type-to-int-on-python
    
def query_ohlc_max_date (ohlc_table: str)-> int:
    """
    """
    fetch_ohlc = query_ohlc_max_date_ (ohlc_table)
    return fetch_ohlc.result()
    
def fetch_ohlc (symbol: str, time_frame: int)-> list:

    '''
    
    '''        
    from market_data import fetch_ohlc
    
    # adjust symbol as per exchange standards
    symbol = symbol.replace('_', '-')

    # fetch ohlc data
    ohlc_ = fetch_ohlc.OHLC (symbol, time_frame)
    ohlc = ohlc_. ohlc()
    
    return ohlc.to_dict('records')
   
@unsync        
def check_and_fetch_ohlc_exceed_thresold_ (symbol: str, ohlc_max_date: int, time_frame: int):

    '''         
    '''    
            
    ohlc_df = fetch_ohlc (symbol, time_frame)
            
    return  [o for o in [ o for o in ohlc_df if o['date'] > ohlc_max_date ]]
    
def check_and_fetch_ohlc_exceed_thresold (symbol: str,  ohlc_max_date: int, time_frame: int):
    """
    """
    fetch_ohlc = check_and_fetch_ohlc_exceed_thresold_ (symbol, ohlc_max_date, time_frame)
    return fetch_ohlc.result()
    
@unsync        
def insert_ohlc_to_sqlite_ (symbol: list, ohlc_max_date, time_frame: int):

    '''
    symbol: symbols_underlying_futures
    '''        
    
    ohlc_table = f'{symbol}_{time_frame}'
    
    with sqlite_operation.db_ops() as cur:
        
        # symbol perpetual
        symbol = f'{symbol}'
        
        # no need to accumulate the following time frames
        if time_frame in [900,3600,86400]:
            drop_table =  f'DROP TABLE IF  EXISTS {ohlc_table}'
            cur.execute(f'{drop_table}')
        
        # create table name: ohlc 
        create_table = f'CREATE TABLE IF NOT EXISTS {ohlc_table} (date REAL, open REAL, high REAL, low REAL, close REAL, volume REAL)'    
        cur.execute (f'{create_table}')  
                
        if ohlc_max_date == None or ohlc_max_date ==[] or ohlc_max_date == 0:
            ohlc_df = fetch_ohlc (symbol, time_frame)

        else:
            ohlc_df = check_and_fetch_ohlc_exceed_thresold (symbol,  ohlc_max_date, time_frame)
        #log.error (ohlc_df)

        insert_table = f'INSERT INTO {ohlc_table} (date, open, high, low, close, volume) VALUES (:date, :open, :high, :low, :close, :volume);'     
        ((cur.executemany (f'{insert_table}', ohlc_df))) #https://stackoverflow.com/questions/53963028/how-to-insert-multiple-rows-from-a-python-nested-dictionary-to-a-sqlite-db
        
def insert_ohlc_to_sqlite (symbol: list, ohlc_max_date: int,
                            time_frame: int):

    '''
    '''    

    try:

        fetch_dask = []
               
        insert_ohlc = insert_ohlc_to_sqlite_ (symbol, ohlc_max_date, time_frame)
        insert_ohlc.result()
        
        results_dask = compute(*fetch_dask) 
        
    except  Exception as error:
        formula.log_error('database', 'load_data_to_db', error, 10)
        
def main (underlying: str, TIME_FRAME)-> None:

    '''
    # underlying = 'BTC'
            Return and rtype: None
    '''    

    try:   
            
        now_time = formula.convert_time_to_utc()['utc_now']
        now_time_unix = formula.convert_time_to_unix (now_time)
        #log.info(f'{now_time_unix}')

        time_frame_ms = TIME_FRAME * (60 * 1000)  #in milli seconds 
        ohlc_table = f'{underlying}_{TIME_FRAME}'
        ohlc_max_date = query_ohlc_max_date (ohlc_table)
            
        delta_now_transaction = now_time_unix - ohlc_max_date
        
        #log.info(f'{ohlc_max_date}')
        #log.info(f'{delta_now_transaction}')
        #log.info(f'{delta_now_transaction > time_frame_ms}')
        if delta_now_transaction > time_frame_ms:

            try:   
                
                insert_ohlc_to_sqlite (underlying, ohlc_max_date, TIME_FRAME)
                
            except Exception as error:
                formula.log_error('main', 'load_data_to_db', error, 10)
                
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('database', 'main', error, 10)
            
if __name__ == "__main__":
    
    import random
    
    try:   
        
        print('insert tickers')
        main ('BTC', 60)  

        message = ('penarikan ohlc & ticker selesai')
        
        idle = 2700
        formula.sleep_and_restart_program (idle)
        

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('database', 'load_data_to_db', error, 10)