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

def create_dataBase_sqlite(db_name: str = "src/databases/trading.sqlite3") -> None:
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
def db_ops(db_name: str = "src/databases/trading.sqlite3") -> None:
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
         
def create_table_mytrades ():

    '''
    '''   
    with db_ops() as cur:
        
        cur.execute("DROP TABLE IF EXISTS mytrades")
        
        # create table name: tickers_futures
        create_table_mytrades = f'CREATE TABLE IF NOT EXISTS mytrades (   instrument_name TEXT, \
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
                                                                            api BOOLEAN NOT NULL CHECK (api IN (0, 1)))'           
        try:
            cur.execute (f'{create_table_mytrades}') 
        except Exception as error:
            print(error)

def insert_table_mytrades (params):

    '''
    '''   
    instrument_name = params ['instrument_name']
    label = params ['label']
    direction = params ['direction']
    amount = params ['amount']
    price = params ['price']
    state = params ['state']
    order_type = params ['order_type']
    timestamp = params ['timestamp']
    trade_seq = params ['trade_seq']
    trade_id = params ['trade_id']
    tick_direction = params ['tick_direction']
    order_id = params ['order_id']
    api = params ['api']
    #print (params)
        
    with db_ops() as cur:
        
        insert_table_mytrades= f'INSERT INTO mytrades (instrument_name,  label, direction, amount, price, state, order_type, timestamp, trade_seq, trade_id, tick_direction, order_id, api) VALUES (:instrument_name,  :label, :direction, :amount, :price, :state, :order_type, :timestamp, :trade_seq, :trade_id, :tick_direction, :order_id, :api);'  

        
        cur.executemany (f'{insert_table_mytrades}', [params])
        
                  
def querying_table_mytrades (table: str = 'mytrades')->list:

    '''
            Reference
            # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    ''' 
    query_table = f'SELECT  * FROM {table}' 
    
    try:
        with db_ops() as cur:
            result = list(cur.execute((f'{query_table}')))
            headers = list(map(lambda attr : attr[0], cur.description))
                        
            combine_result = []
            for i in result:
                combine_result.append(dict(zip(headers,i)))
                
    except Exception as error:
        print (error)

