#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from loguru import logger as log
from functools import lru_cache
from utils import formula
from dask import delayed, compute    
from unsync import unsync
from db_management import sqlite_operation

def get_next_funding_rates (perpetuals: list)-> list:

    '''
    # get_next_funding_rates for each perpetual
            Return and rtype: selected data funding (list)
    ''' 
    from market_data import fetch_next_funding
    
    return fetch_next_funding.get_next_funding_rates (perpetuals)

def get_move_stats_from_ftx (coin: str)-> list:

    '''
    # get_move_stats/greeks
            Return and rtype: move greeks (list)
    ''' 
    
    from market_data import fetch_tickers
    market_data= fetch_tickers.FTX_Tickers('ftx')
    
    return market_data.fetch_individual_ticker_future_stats(coin)

@unsync
def insert_move_stats_to_sqlite (next_rates: list) -> None:

    '''
    # index
            Return and rtype: kredensial (str)
            #https://stackoverflow.com/questions/53963028/how-to-insert-multiple-rows-from-a-python-nested-dictionary-to-a-sqlite-db
    '''    
     
    with sqlite_operation.db_ops() as cur:

        cur.execute("DROP TABLE IF EXISTS greeks") #https://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
        cur.execute('CREATE TABLE IF NOT EXISTS fundingRAte (underlying TEXT, future TEXT, nextRate REAL, nextFundingTime DATE)')       
        log.warning(cur.executemany ("INSERT INTO fundingRAte (underlying, future, nextRate, nextFundingTime) VALUES (:underlying, :future, :nextRate, :nextFundingTime);", next_rates))
          
@unsync
def insert_next_funding_to_sqlite (next_rates: list)-> None:

    '''
    '''    
     
    with sqlite_operation.db_ops() as cur:

        cur.execute("DROP TABLE IF EXISTS fundingRAte") #https://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
        cur.execute('CREATE TABLE IF NOT EXISTS fundingRAte (underlying TEXT, future TEXT, nextRate REAL, nextFundingTime DATE)')       
        log.warning(cur.executemany ("INSERT INTO fundingRAte (underlying, future, nextRate, nextFundingTime) VALUES (:underlying, :future, :nextRate, :nextFundingTime);", next_rates))
          
@unsync        
def insert_correlation_result_to_sqlite (symbols_underlyings: list, main_underlying: str, time_frame: int, threshold: float)->None:

    '''
    # index
            Return and rtype: kredensial (str)
            
    '''    
    from market_analysis import market_analysis_general
    
    # fetch heatmap dan funding rate data
    heatmap_and_funding_rate = market_analysis_general.heatmap_and_funding_rate (symbols_underlyings, 
                                                                                 main_underlying,  
                                                                                 time_frame, threshold
                                                                                 ) ['all_result']
    # transform ohlc data in dataframe heatmap_and_funding_rate to dict
    heatmap_and_funding_rate =  heatmap_and_funding_rate.to_dict('records')

    with sqlite_operation.db_ops() as cur:
        cur.execute("DROP TABLE IF EXISTS correl_funding") #https://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
        
        #create table correl_funding
        create_table = f'CREATE TABLE IF NOT EXISTS correl_funding (future TEXT, correl REAL, nextFundingRate REAL)'           
        cur.execute (f'{create_table}')        
                    
        #insert heatmap_and_funding_rate data into table correl_funding
        insert_table = f'INSERT INTO correl_funding (future, correl, nextFundingRate) VALUES (:future, :correl, :nextFundingRate);'     
        (cur.executemany (f'{insert_table}', heatmap_and_funding_rate)) #https://stackoverflow.com/questions/53963028/how-to-insert-multiple-rows-from-a-python-nested-dictionary-to-a-sqlite-db

@lru_cache(maxsize=None)
def fetch_tickers_perpetual_from_sqlite ()->list:
    """
    # menarik tickers untuk seluruh koin
    """

    from market_data import fetch_tickers
     
    ticker_futures = fetch_tickers.FTX_Tickers('ftx')
    ticker_futures = ticker_futures.fetch_tickers_from_sqlite()

    if ticker_futures == []:
        ticker_futures = fetch_tickers_from_ftx()
        
    return ticker_futures ['tickers_perpetuals']

@lru_cache(maxsize=None)
def fetch_tickers_from_ftx ()-> dict:
    """
    # menarik tickers untuk seluruh koin
    """

    from market_data import fetch_tickers
     
    tickers = fetch_tickers.FTX_Tickers('ftx')
    
    # fetch both of all & futures tickers
    return {'tickers_futures': tickers.tarik_tickers('futures')['tickers_futures'],
            'tickers_all': tickers.tarik_tickers()['tickers_all'] }
        
def insert_next_funding_to_db (symbols_perpetuals: list)->None:

    '''
    '''    

    try:

        fetch_dask = []
        
        symbols_perpetuals = [o['name']  for o in [o for o in ticker_futures  if o['type_future'] == 'perpetual']] 
        next_rates = get_next_funding_rates (symbols_perpetuals)
        insert_next = insert_next_funding_to_sqlite (next_rates)
        insert_next.result()
        results_dask = compute(*fetch_dask) 
        
    except  Exception as error:
        formula.log_error('database', 'insert_next_funding_to_db', error, 10)
        
def insert_correl_to_sqlite (symbols_underlying_futures: list)->None:

    '''
    '''    

    try:

        fetch_dask = []
               
        insert_corr = insert_correlation_result_to_sqlite (symbols_underlying_futures, 'BTC', 3600, 0)
        insert_corr.result()
        
        results_dask = compute(*fetch_dask) 
        
    except  Exception as error:
        formula.log_error('database', 'insert_correl_to_sqlite', error, 10)
        
if __name__ == "__main__":
    
    try:   
        from time import sleep
        from app_db1H import main as update_ohlc_tickers
           
        sleep (1/100)
        
        print ('update ohlc')
        #update ohlc and tickers (data min from 1 hour ago)
        update_ohlc_tickers()
        
        ticker_futures =  fetch_tickers_perpetual_from_sqlite ()

        symbols_perpetuals = [o['name']   for o in [o for o in ticker_futures if o['type_future'] == 'perpetual']]

        print ('insert_next_funding_to_db')
        insert_next_funding_to_db (symbols_perpetuals)

        non_tradable_underlyings = ['1INCH']
        symbols_underlying_futures = [o['underlying']   for o in [o for o in ticker_futures ]]
        symbols_underlying_futures.remove ('1INCH')
        
        print ('insert_correl_to_sqlite')
        insert_correl_to_sqlite (symbols_underlying_futures)
        

        idle = 300
        log.info (f" sleep and restart after {idle} seconds")
        formula.sleep_and_restart_program (idle)
        
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('database', 'main', error, 10)