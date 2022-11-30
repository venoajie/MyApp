# -*- coding: utf-8 -*-

from loguru import logger as log
from functools import lru_cache
from unsync import unsync

def telegram_bot_sendtext(bot_message, purpose) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

@lru_cache(maxsize=None)
def fetch_tickers_from_ftx ():
    """
    # fetch tickers for all instruments
    """

    from market_data import fetch_tickers
    telegram_bot_sendtext ('fetch_tickers_from_ftx', 'load_to_db')
     
    tickers = fetch_tickers.FTX_Tickers('ftx')

    # fetch both of all & futures tickers
    return {'tickers_futures': tickers.tarik_tickers('futures')['tickers_futures'],
            'tickers_all': tickers.tarik_tickers()['tickers_all'] }

@unsync        
def insert_ticker_futures ():

    '''
    '''   
    from db_management import sqlite_operation
   
    #prepare class ticker ftx attributes
    tickers = fetch_tickers_from_ftx()
    
    # fetch both of all & futures tickers
    tickers_futures = tickers ['tickers_futures'] 
    tickers_all = tickers ['tickers_all'] 
    restricted = [o  for o in [o for o in tickers_all if o['restricted'] == True ]]
    #tickers_all1 =  ( [o['name'] for o in [ o for o in tickers_all   ]]  )
    #log.warning (f'{tickers_all1=}')
    telegram_bot_sendtext ('insert_ticker_futures', 'load_to_db')

    with sqlite_operation.db_ops() as cur:
        
        cur.execute("DROP TABLE IF EXISTS tickers")
        cur.execute("DROP TABLE IF EXISTS tickers_spot")
        cur.execute("DROP TABLE IF EXISTS tickers_futures")
        cur.execute("DROP TABLE IF EXISTS restricted")
        cur.execute("DROP TABLE IF EXISTS tickers_all")
         
        # create table name: restricted
        create_table_restricted = f'CREATE TABLE IF NOT EXISTS restricted (name TEXT, underlying TEXT)'           
        cur.execute (f'{create_table_restricted}') 

        # create table name: tickers
        create_table_tickers = f'CREATE TABLE IF NOT EXISTS tickers (name TEXT, underlying TEXT, enabled TEXT, type TEXT, perpetual TEXT, baseCurrency TEXT, quoteCurrency TEXT, restricted TEXT, expiry TEXT, moveStart TEXT, priceIncrement REAL, sizeIncrement REAL, minProvideSize REAL)'           
        cur.execute (f'{create_table_tickers}') 
        
        # create table name: tickers_futures
        create_table_tickers_futures = f'CREATE TABLE IF NOT EXISTS tickers_futures (name TEXT, type TEXT, perpetual TEXT, expiry TEXT, moveStart TEXT)'           
        cur.execute (f'{create_table_tickers_futures}') 

        insert_table_ticker_futures  = f'INSERT INTO tickers_futures (name,  type, perpetual, expiry, moveStart) VALUES (:name, :type, :perpetual, :expiry, :moveStart);'  
        cur.executemany (f'{insert_table_ticker_futures}', tickers_futures)
        
        
        # create table name: tickers_all
        create_table_tickers_all = f'CREATE TABLE IF NOT EXISTS tickers_all (name TEXT, underlying TEXT, enabled TEXT, type TEXT, baseCurrency TEXT, quoteCurrency TEXT, restricted TEXT,  priceIncrement REAL, sizeIncrement REAL, minProvideSize REAL)'           
        cur.execute (f'{create_table_tickers_all}') 

        insert_table_ticker_all  = f'INSERT INTO tickers_all (name, underlying, enabled, type, baseCurrency, quoteCurrency, restricted, priceIncrement, sizeIncrement, minProvideSize) VALUES (:name, :underlying, :enabled, :type, :baseCurrency, :quoteCurrency, :restricted, :priceIncrement, :sizeIncrement, :minProvideSize);'  
        cur.executemany (f'{insert_table_ticker_all}', tickers_all)

        create_index = f'CREATE UNIQUE INDEX id_name ON tickers (name);'    # https://www.sqlitetutorial.net/sqlite-replace-statement/   
        cur.execute (f'{create_index}') 
                    
        insert_table_restricted  = f'INSERT INTO restricted (name, underlying) VALUES (:name, :underlying);'     
        
        insert_table_tickers  = f'INSERT INTO tickers (name, type, baseCurrency, quoteCurrency, restricted, priceIncrement, sizeIncrement, minProvideSize) VALUES (:name, :type, :baseCurrency, :quoteCurrency, :restricted, :priceIncrement, :sizeIncrement, :minProvideSize);'     
        cur.executemany (f'{insert_table_tickers}', tickers_all)
        cur.executemany (f'{insert_table_restricted}', restricted)

        replace_table_futuresData = f'REPLACE INTO tickers (name, underlying, enabled, type, perpetual, expiry, moveStart) VALUES (:name, :underlying, :enabled, :type, :perpetual, :expiry, :moveStart);'     
        cur.executemany (f'{replace_table_futuresData}', tickers_futures)
        
def insert_ticker_futures_to_sqlite ():

    '''
    '''    
    from dask import delayed, compute
    
    try:

        fetch_dask = []
               
        insert_ticker_futures_ = insert_ticker_futures ()
        insert_ticker_futures_.result()       
        results_dask = compute(*fetch_dask)
        
    except  Exception as error:
        from utils import formula
        formula.log_error('fetch_tickers_insert_to_db', 'insert_ticker_futures_to_sqlite', error, 10)
        
if __name__ == "__main__":
        
    try:   
        
        insert_ticker_futures_to_sqlite ()
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        from utils import formula
        formula.log_error('fetch_tickers_insert_to_db', 'main', error, 10)