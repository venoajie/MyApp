# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager
import asyncio
import aiosqlite
from loguru import logger as log

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

async def create_dataBase_sqlite(db_name: str = "databases/trading.sqlite3") -> None:
    """
    https://stackoverflow.com/questions/71729956/aiosqlite-result-object-has-no-attribue-execute
    """
    
    try:
        conn = await aiosqlite.connect(db_name)
        cur = await conn.cursor()
        await conn.commit()
        await conn.close()
    
    except Exception as error:
        print (error)

@contextmanager
async def db_ops(db_name: str = "databases/trading.sqlite3") -> None:
    """
    # prepare sqlite initial connection + close
            Return and rtype: None
            #https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
            https://code-kamran.medium.com/python-convert-json-to-sqlite-d6fa8952a319
    """
    conn = await aiosqlite.connect(db_name, isolation_level=None)

    try:
        cur = await conn.cursor()
        yield cur

    except Exception as e:
        telegram_bot_sendtext("sqlite operation", "failed_order")
        telegram_bot_sendtext(str(e), "failed_order")
        print(e)
        await conn.rollback()
        raise e

    else:
        await conn.commit()
        await conn.close()
         
async def create_tables ():

    '''
    '''   
    async with  aiosqlite.connect("databases/trading.sqlite3", isolation_level=None) as cur:
        
        await cur.execute("DROP TABLE IF EXISTS mytrades")
        
        tables= ['myTradesOpen', 'myTradesClosed','ordersOpen', 'ordersClosed','ordersUntrig']
        
        try:           
            for table in tables:
                
                await cur.execute(f"DROP TABLE IF EXISTS {table}")
                if 'myTrades' in table:
                    create_table = f'CREATE TABLE IF NOT EXISTS {table} (instrument_name TEXT, \
                                                                    label TEXT, \
                                                                    direction TEXT, \
                                                                    amount REAL, \
                                                                    price REAL, \
                                                                    state TEXT, \
                                                                    order_type TEXT, \
                                                                    timestamp INTEGER, \
                                                                    trade_seq INTEGER, \
                                                                    trade_id TEXT, \
                                                                    tick_direction INTEGER, \
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
                                                                    last_update_timestamp INTEGER, \
                                                                    order_id TEXT, \
                                                                    is_liquidation BOOLEAN NOT NULL CHECK (is_liquidation IN (0, 1)), \
                                                                    api BOOLEAN NOT NULL CHECK (api IN (0, 1)))'  
                
                await cur.execute (f'{create_table}') 
            
        except Exception as error:
            print(error)
            await telegram_bot_sendtext("sqlite operation", "failed_create_table")
            await telegram_bot_sendtext("sqlite operation", {create_table})

async def insert_tables (table_name, params):

    '''
    '''   
    try:
            
        async with  aiosqlite.connect("databases/trading.sqlite3", isolation_level=None) as cur:
            
            if 'orders' in table_name:
                
                insert_table= f'INSERT INTO {table_name} (instrument_name,  label, direction, amount, price, trigger_price, stop_price, order_state, order_type, last_update_timestamp,  order_id, is_liquidation, api) VALUES (:instrument_name,  :label, :direction, :amount, :price, :trigger_price, :stop_price,:order_state, :order_type, :last_update_timestamp, :order_id, :is_liquidation, :api);'  
                
            if 'myTrades' in table_name:
                insert_table= f'INSERT INTO {table_name} (instrument_name,  label, direction, amount, price, state, order_type, timestamp, trade_seq, trade_id, tick_direction, order_id, api, fee) VALUES (:instrument_name,  :label, :direction, :amount, :price, :state, :order_type, :timestamp, :trade_seq, :trade_id, :tick_direction, :order_id, :api, :fee);'   
            
            # input was in list format. Insert them to db one by one
            if isinstance(params, list):
                for param in params:
                    if 'trigger_price' not in list(param):
                        param['trigger_price']=None
                        param['stop_price']=None
                        
                    await cur.executemany (f'{insert_table}', [param])
                    
            # input is in dict format. Insert them to db directly
            else:
                log.warning (param)
                await cur.executemany (f'{insert_table}', [params])
            
    except Exception as error:
        print (error)
        await telegram_bot_sendtext("sqlite operation", "failed_insert_data_to_table")
        await telegram_bot_sendtext("sqlite operation", {param})
        
async def querying_table (table: str = 'mytrades', filter: str = None, operator=None,  filter_value=None)->list:

    '''
            Reference
            # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    ''' 
    query_table = f'SELECT  * FROM {table} WHERE  {filter} {operator} ?' 
    if filter == None:
        query_table = f'SELECT  * FROM {table}'
    
    #log.debug(query_table)
    
    combine_result = []
    
    try:
        async with  aiosqlite.connect("databases/trading.sqlite3", isolation_level=None) as db:
            async with db.execute(query_table) as cur:

                log.debug (cur)
                head = (map(lambda attr : attr[0], cur.description))
                headers = list(head)        
                log.debug (headers)
                log.debug (query_table)
                res = (await cur.execute((f'{query_table}'),()))
                log.debug (res)
                fetchall =  (await cur.fetchall())
                result = list(res)
                    
                
                for i in fetchall:
                    combine_result.append(dict(zip(headers,i)))
                
    except Exception as error:
        print (error)
        
        await telegram_bot_sendtext("sqlite operation", "failed_querying_data_from_table")
        await telegram_bot_sendtext("sqlite operation", {query_table})
        
    return 0 if (combine_result ==[] or  combine_result == None ) else  (combine_result)



