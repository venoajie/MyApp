#!/usr/bin/python3

import os
from os.path import join, dirname

# installed
from dataclassy import dataclass
from loguru import logger as log
import asyncio
from dotenv import load_dotenv
from os.path import join, dirname
import requests

from portfolio.deribit import open_orders_management, myTrades_management
from utils import pickling, system_tools, telegram_app, formula, string_modification
import deribit_get#,deribit_rest
from risk_management import spot_hedging
from configuration import  label_numbering

from utils import pickling, system_tools, telegram_app, formula, string_modification

    
@dataclass(unsafe_hash=True, slots=True)
class SynchronizingFiles ():

    
    '''
    '''       

    data: list
        
    async def remove_redundant_data (self) -> list:
        """
        """
        log.error (self.data)
        if isinstance(self.data, list):

            free_from_duplicates_data = string_modification.remove_redundant_elements (self.data)
            
            log.error (free_from_duplicates_data)
            
    async def save_data (self) -> list:
        """
        """
        cleaned_data = await self. remove_redundant_data()
        pickling.replace_data (cleaned_data)

    async def cleanUp_data (self) -> list:
        """
        """
            
        my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', self.currency, 'open')
        my_trades_open: list = pickling.read_data(my_trades_path_open) 
        
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', self.currency, 'open')
        my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', self.currency, 'closed')
        
        paths = [my_trades_open, my_path_orders_closed, my_path_orders_open]
        
        for path in paths:
            data_from_db = pickling.read_data (path)
            cleaned_data = await self. remove_redundant_data()
            pickling.replace_data (path, cleaned_data)
        
                
async def main (item):
    
    try:    
        syn = SynchronizingFiles (item)
        
        return syn
        
        

        #asyncio.gather(*[SynchronizingFiles (item).remove_redundant_data() for item in paths ])  
         
    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
    
if __name__ == "__main__":

    
    try:
        
            
        my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'open')
        my_trades_open: list = pickling.read_data(my_trades_path_open) 
        
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', 'eth', 'open')
        my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', 'eth', 'closed')
        
        paths = [my_trades_path_open, my_path_orders_closed, my_path_orders_open]
        log.error (paths)

        asyncio.gather(*[ SynchronizingFiles (item).remove_redundant_data() for item in paths ])  
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
