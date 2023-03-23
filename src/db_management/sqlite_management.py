# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)

def telegram_bot_sendtext(bot_message: str, purpose: str) -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

def create_dataBase_sqlite(db_name: str = "databases/trading.sqlite3") -> None:
    """
    """
    
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        conn.commit()
        conn.close()
    
    except Exception as error:
        print (error)

@contextmanager
def db_ops(db_name: str = "databases/trading.sqlite3") -> None:
    """
    # prepare sqlite initial connection + close
            Return and rtype: None
            #https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
            https://code-kamran.medium.com/python-convert-json-to-sqlite-d6fa8952a319
    """
    conn = sqlite3.connect(db_name, isolation_level=None)

    try:
        cur = conn.cursor()
        yield cur

    except Exception as e:
        telegram_bot_sendtext("sqlite operation", "failed_order")
        telegram_bot_sendtext(str(e), "failed_order")
        print(e)
        conn.rollback()
        raise e

    else:
        conn.commit()
        conn.close()
         
def create_tables ():

    '''
    '''   
    with db_ops() as cur:
        
        #cur.execute("DROP TABLE IF EXISTS mytrades")
        
        tables= ['myTradesOpen', 'myTradesClosed','ordersOpen', 'ordersClosed','ordersUntrig']
        
        try:           
            for table in tables:
                print (table)
                print ('myTrades' in table)
                #cur.execute(f"DROP TABLE IF EXISTS {table}")
                if 'myTrades' in table:
                    create_table = f'CREATE TABLE IF NOT EXISTS {table} (instrument_name TEXT, \
                                                                    label TEXT, \
                                                                    direction TEXT, \
                                                                    amount REAL, \
                                                                    price REAL, \
                                                                    state TEXT, \
                                                                    order_type TEXT, \
                                                                    timestamp REAL, \
                                                                    trade_seq REAL, \
                                                                    trade_id TEXT, \
                                                                    tick_direction REAL, \
                                                                    order_id TEXT, \
                                                                    api BOOLEAN NOT NULL CHECK (api IN (0, 1)),\
                                                                    fee REAL)'           
                if 'orders' in table:
                    create_table = f'CREATE TABLE IF NOT EXISTS {table} (instrument_name TEXT, \
                                                                    label TEXT, \
                                                                    direction TEXT, \
                                                                    amount REAL, \
                                                                    price REAL, \
                                                                    trigger_price REAL, \
                                                                    stop_price REAL, \
                                                                    order_state TEXT, \
                                                                    order_type TEXT, \
                                                                    last_update_timestamp REAL, \
                                                                    filled_amount REAL, \
                                                                    order_id TEXT, \
                                                                    is_liquidation BOOLEAN NOT NULL CHECK (api IN (0, 1)), \
                                                                    api BOOLEAN NOT NULL CHECK (api IN (0, 1)))'  
                print (create_table)

                cur.execute (f'{create_table}') 
            
        except Exception as error:
            print(error)

def insert_tables (table_name, params):

    '''
    '''   
        
    with db_ops() as cur:
        if 'orders' in table_name:
            insert_table= f'INSERT INTO {table_name} (instrument_name,  label, direction, amount, price, trigger_price, order_state, order_type, last_update_timestamp, filled_amount,  order_id, is_liquidation, api) VALUES (:instrument_name,  :label, :direction, :amount, :price, :trigger_price, :stop_price,:order_state, :order_type, :last_update_timestamp, :filled_amount, :order_id, :is_liquidation, :api);'  
            
        if 'myTrades' in table_name:
            insert_table= f'INSERT INTO {table_name} (instrument_name,  label, direction, amount, price, state, order_type, timestamp, trade_seq, trade_id, tick_direction, order_id, api, fee) VALUES (:instrument_name,  :label, :direction, :amount, :price, :state, :order_type, :timestamp, :trade_seq, :trade_id, :tick_direction, :order_id, :api, :fee);'   
        
        if isinstance(params, list):
            for param in params:
                cur.executemany (f'{insert_table}', [param])
        else:
            cur.executemany (f'{insert_table}', [params])
            
def querying_table (table: str = 'mytrades', filter: str = None, operator=None,  filter_value=None)->list:

    '''
            Reference
            # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    ''' 
    query_table = f'SELECT  * FROM {table} WHERE  {filter} {operator} ?' 
    if filter == None:
        query_table = f'SELECT  * FROM {table}'
    print(query_table)
    try:
        with db_ops() as cur:
            

            result = list(cur.execute((f'{query_table}')))
                
            headers = list(map(lambda attr : attr[0], cur.description))
                        
            combine_result = []
            for i in result:
                combine_result.append(dict(zip(headers,i)))
                
    except Exception as error:
        from utils import formula
        formula.log_error('app','name-try2', error, 10)
        combine_result = []
        
    return 0 if (combine_result ==[] or  combine_result == None ) else  (combine_result)



