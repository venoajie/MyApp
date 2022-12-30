#!/usr/bin/python3

# installed
from loguru import logger as log
import asyncio
from utils import pickling, system_tools, string_modification
    
async def remove_redundant_data (data) -> list:
    """
    """
    
    if isinstance(data, list):

        return  string_modification.remove_redundant_elements (data)
         
async def returning_data_to_db (path) -> list:
    """
    """    
    data_from_db = pickling.read_data (path)
    free_from_duplicates_data = await  remove_redundant_data (data_from_db)
    pickling.replace_data (path, free_from_duplicates_data)
    
if __name__ == "__main__":
    
    try:
                    
        my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'open')
        my_trades_open: list = pickling.read_data(my_trades_path_open) 
        
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', 'eth', 'open')
        my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', 'eth', 'closed')
        
        paths = [my_trades_path_open, my_path_orders_closed, my_path_orders_open]

        for path in paths:
            loop = asyncio.get_event_loop()
            loop.run_until_complete (returning_data_to_db (path))
                    
        loop.close()

    except Exception as error:
        from utils import formula

        formula.log_error('app','name-try2', error, 10)
