#!/usr/bin/python3

# installed
import asyncio
from utils import pickling, system_tools, string_modification
         
async def read_data_from_db (path) -> list:
    """
    """    
    read = pickling.read_data (path)
    return read
 
async def remove_redundant_data (data) -> list:
    """
    """
    
    if isinstance(data, list):
        return  string_modification.remove_redundant_elements (data)
         
async def returning_data_to_db (path) -> list:
    """
    """    
    data_from_db =await read_data_from_db (path)
    free_from_duplicates_data = await  remove_redundant_data (data_from_db)
    pickling.replace_data (path, free_from_duplicates_data)

async def main (path) -> list:
    """
    """    
            
    my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'open')        
    my_path_orders_open: str = system_tools.provide_path_for_file ('orders', 'eth', 'open')
    my_path_orders_cancelled: str = system_tools.provide_path_for_file ('orders', 'eth', 'cancelled')
    my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', 'eth', 'closed')
    my_path_orders_filled: str = system_tools.provide_path_for_file ('orders', 'eth', 'filled')
    my_trades_path_closed: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'closed')        
    
    paths = [my_trades_path_open, 
                my_path_orders_open, 
                my_path_orders_cancelled, 
                my_path_orders_closed, 
                my_path_orders_filled, 
                my_trades_path_closed
                ]

    for path in paths:
        loop = asyncio.get_event_loop()
        
        loop.run_until_complete (returning_data_to_db (path))
                
    loop.close()


if __name__ == "__main__":
    
    from time import sleep
    
    sleep (0.1)
    
    try:
        main()
           
    except Exception as error:
        from utils import formula

        formula.log_error('syn file','syn file', error, 10)
