#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from loguru import logger as log
from functools import lru_cache
from utils import formula
from dask import delayed, compute    
from unsync import unsync
from time import sleep
from db_management import sqlite_operation

def telegram_bot_sendtext(bot_message, purpose) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

def query_ohlc_max_date (ohlc_table: str)-> int:
    """
    """
    from db_management import fetch_ohlc_insert_to_db
    return (fetch_ohlc_insert_to_db.query_ohlc_max_date (ohlc_table))

def query_move_stat_max_date (ohlc_table: str)-> int:

    query_table = f'SELECT MAX ((date)) FROM {ohlc_table}' 
    
    with sqlite_operation.db_ops() as cur:
        try:
            result = (list(cur.execute((f'{query_table}'))))     [0][0]
        except:
            result = []
            
        return 0 if (result ==[] or  result == None ) else  (result) # https://stackoverflow.com/questions/29311819/how-to-convert-tuple-type-to-int-on-python
    
@unsync
def get_move_stats_from_ftx_(coin: str)-> object:

    '''
    # get_move_stats/greeks
    ''' 
    
    from market_data import fetch_tickers
    
    market_data= fetch_tickers.FTX_Tickers('ftx')
    
    return market_data.fetch_individual_ticker_future_stats(coin)

def get_move_stats_from_ftx (coin: str)-> list:

    '''
    # transform get_move_stats_from_ftx_ unsync object into list
    '''    

    try:
               
        get_move_stats_ = get_move_stats_from_ftx_ (coin)
        return get_move_stats_.result()       
        
    except  Exception as error:
        formula.log_error('db_management', 'fetch_move_data-get_move_stats_from_ftx', error, 10)
        
@unsync
def insert_move_stats_to_sqlite_ (move: str, move_stats: list) -> object:

    '''
    # insert_move_stats_to_sqlite.  self explained
    '''    
        
    ohlc_table = f'{move}_300' 
    ohlc_max_date = query_ohlc_max_date (ohlc_table)
        
    move_stat_max_date = query_move_stat_max_date (ohlc_table)

    if move_stat_max_date == None or move_stat_max_date ==[] or move_stat_max_date == 0 or ohlc_max_date > move_stat_max_date :

        # parse data from ftx
        delta =  move_stats['greeks']['delta']
        gamma =  move_stats['greeks']['gamma'] 
        impliedVolatility =  move_stats['greeks']['impliedVolatility'] 
        
        try:
            strike_price = move_stats['strikePrice']
        except:
            strike_price = None
            
        try:
            predictedExpirationPrice = move_stats['predictedExpirationPrice']
        except:
            predictedExpirationPrice = None

        try:
            expirationPrice = move_stats['expirationPrice']
        except:
            expirationPrice = None

        #combine parsed move stats data
        move_stats = [{'date': ohlc_max_date,
                    'name': move, 
                    'volume': move_stats['volume'], 
                    'predictedExpirationPrice': predictedExpirationPrice,
                    'expirationPrice': expirationPrice,
                    'strikePrice':strike_price, 
                    'delta': delta, 
                    'gamma': gamma, 
                    'impliedVolatility': impliedVolatility, 
                    'openInterest': move_stats['openInterest']}]        

        # insert combined data into sqlite db
        with sqlite_operation.db_ops() as cur:
            info= (f'{move}  {move_stats}')
            
            #cur.execute("DROP TABLE IF EXISTS moveStats")
            #telegram_bot_sendtext(info,'success_order')

            cur.execute('CREATE TABLE IF NOT EXISTS moveStats (date REAL, name TEXT, volume REAL, predictedExpirationPrice REAL, expirationPrice REAL, strikePrice REAL, impliedVolatility REAL, delta REAL, gamma REAL, openInterest REAL)')       
            (cur.executemany ("INSERT INTO moveStats (date, name, volume, predictedExpirationPrice, expirationPrice, strikePrice, impliedVolatility, gamma, delta, openInterest) VALUES (:date, :name, :volume, :predictedExpirationPrice, :expirationPrice, :strikePrice, :impliedVolatility, :gamma, :delta, :openInterest);", move_stats))
        
def insert_move_stats_to_sqlite (move: str, move_stats: list) -> None:

    '''
    # transform insert_move_stats_to_sqlite unsync object 
    '''    

    try:
               
        insert_move_stats_ = insert_move_stats_to_sqlite_ (move, move_stats)
        insert_move_stats_.result()   
            
    except  Exception as error:
        formula.log_error('db_management', 'fetch_move_data-insert_move_stats_to_sqlite', error, 10)
        
@lru_cache(maxsize=None)
def fetch_move_tickers ():
    """
    # fetch_move_tickers, self explained
    """
    from market_data import fetch_tickers
     
    tickers = fetch_tickers.FTX_Tickers('ftx')
    ticker_futures = tickers.fetch_tickers_from_sqlite()  ['tickers_futures_all']
    #log.warning ([o['name'] for o in ticker_futures if o['type_future'] =='move' ])

    return [o['name'] for o in ticker_futures if o['type_future'] =='move' ]

#@lru_cache(maxsize=None)
def main ():

    try:           
        sleep (.001)

        fetch_dask = []
        
        # prepare MOVE name
        moves =  fetch_move_tickers ()
        #telegram_bot_sendtext('move_stats','success_order')
        
        # for every move name selected:
        for move in moves:    
            
            # fetch move stat
            move_stats = get_move_stats_from_ftx (move)
            
            # insert move stat to sqlite
            insert_move_stats_to_sqlite (move, move_stats)
            
        results_dask = compute(*fetch_dask)
        
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('db_management', 'fetch_move_data', error, 30)
    
if __name__ == "__main__":
    
    try:        

        sleep (.001)
        main ()
        
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('db_management', 'fetch_move_data', error, 30)