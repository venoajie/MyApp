# -*- coding: utf-8 -*-

from loguru import logger as log
from functools import lru_cache
from unsync import unsync
from db_management import sqlite_operation

def create_table_strategy ():

    '''
    '''   
   
    with sqlite_operation.db_ops() as cur:
         
        # create table name: strategy_entries
        #cur.execute("DROP TABLE IF EXISTS strategy_entries")
        create_table_restricted = f'CREATE TABLE IF NOT EXISTS strategy_entries (subAccount TEXT, strategy TEXT, subStrategy TEXT,  strategyId TEXT, startDate TEXT, instrument TEXT, instrumentRole TEXT, side TEXT, size REAL, orderDate TEXT, orderId TEXT, orderPrice REAL, transactionDate TEXT, transactionId TEXT, transactionPrice REAL, strategyStatus TEXT)'           
        cur.execute (f'{create_table_restricted}') 

def insert_initial_data_to_table_strategy (subAccount,  strategy, sub_strategy, strId, startDate, instruments, instruments_role, side, size):

    '''
    '''   
    create_table_strategy()
   
    with sqlite_operation.db_ops() as cur:
        insert_table_ticker_futures  = f'INSERT INTO strategy_entries (subAccount,  strategy, subStrategy, strategyId, startDate, instrument, instrumentRole, side, size, orderDate, orderId, orderPrice, transactionDate, transactionId, transactionPrice, strategyStatus) VALUES (:subAccount,  :strategy, :subStrategy, :strategyId, :startDate, :instrument, :instrumentRole, :side, :size, :orderDate, :orderId, :orderPrice, :transactionDate, :transactionId, :transactionPrice, :strategyStatus);'  

        strategyStatus ='sent'
        strategy= [{'subAccount':subAccount, 
                    'strategy':strategy, 
                    'subStrategy': sub_strategy,
                    'strategyId':strId, 
                    'startDate':startDate,
                    'instrument':instruments, 
                    'instrumentRole':instruments_role, 
                    'side':side, 
                    'size':size, 
                    'orderDate':None, 
                    'orderId':None, 
                    'orderPrice':None, 
                    'transactionDate':None,
                    'transactionId':None,
                    'transactionPrice':None,
                    'strategyStatus':strategyStatus
                    }
                   ]
        
        cur.executemany (f'{insert_table_ticker_futures}', strategy)
        
if __name__ == "__main__":
        
    try:   
        
        insert_initial_data_to_table_strategy ()
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        from utils import formula
        formula.log_error('fetch_tickers_insert_to_db', 'main', error, 10)