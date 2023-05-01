import asyncio

from market_understanding.MP import MpFunctions
import requests
import pandas as pd
import datetime as dt
import numpy as np
from loguru import logger as log
from db_management import sqlite_management

async def querying_all(table: list, 
                        database: str = "databases/trading.sqlite3") -> dict:
    """ """
    from utilities import string_modification as str_mod
    result =  await sqlite_management.querying_table (table,  database ) 
    return   str_mod.parsing_sqlite_json_output([o['data'] for o in result])  
                
def transform_result_to_data_frame (data: object):
    
    #log.debug (data)
    df = pd.DataFrame(data)
    
    return df   

loop = asyncio.get_event_loop()
df= loop.run_until_complete(querying_all("ohlc1_eth_perp_json"))
df= transform_result_to_data_frame (df)

if __name__ == '__main__':
    log.warning ('START')
    #market_profile= get_market_profile()
    print (df)
    log.warning ('DONE')
