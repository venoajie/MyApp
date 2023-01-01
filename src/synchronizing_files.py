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
        
async def check_open_orders_consistency (currency, open_orders_from_exchange: list, label: str) -> list:
    """
    db vs exchange
    """
    from loguru import logger as log
    
    my_path_orders_open: str = system_tools.provide_path_for_file ('orders', currency, 'open')
    fetch_open_orders_from_db = pickling.read_data(my_path_orders_open)
    log.error (fetch_open_orders_from_db)
    len_open_orders_from_db = []
    len_open_orders_from_exchange_with_label = []
    if fetch_open_orders_from_db:
        open_orders_from_db = fetch_open_orders_from_db ['open_orders_open_byAPI']
        len_open_orders_from_db = len(open_orders_from_db)
        log.error (open_orders_from_db)
    
    #check item qty
    open_orders_from_exchange_with_label = open_orders_from_exchange.my_orders_api_basedOn_label (label)
    log.error (open_orders_from_exchange_with_label)
    if open_orders_from_exchange_with_label:
        len_open_orders_from_exchange_with_label = len(open_orders_from_exchange_with_label)
    
    log.debug (f'{len_open_orders_from_exchange_with_label=} {len_open_orders_from_db=} {len_open_orders_from_exchange_with_label != len_open_orders_from_db=}')
    
    if len_open_orders_from_exchange_with_label != len_open_orders_from_db and False:  
        
        if len_open_orders_from_db >   len_open_orders_from_exchange_with_label:
            pass
    
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', self.currency, 'open')
        
        # cancel related open orders
        id_open_orders_from_exchange_with_label =         [o['order_id'] for o in open_orders_from_exchange_with_label ]
        for open_order_id in id_open_orders_from_exchange_with_label:              
            
            my_path_orders_else = system_tools.provide_path_for_file ('orders', self.currency, order_state)
            
            item_in_open_orders_open_with_same_id =  [o for o in open_orders_from_db if o['order_id'] == open_order_id ] 
            order_state = item_in_open_orders_open_with_same_id ['order_state']
            
            item_in_open_orders_open_with_diff_id =  [o for o in open_orders_from_db if o['order_id'] != open_order_id ] 
            #log.info (f'{item_in_open_orde

            pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id, True)
            pickling.check_duplicate_elements (my_path_orders_open)

            if item_in_open_orders_open_with_same_id != []:
                #log.critical ('item_in_open_orders_open_with_same_id')
                pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id, 100000, True)
                pickling.check_duplicate_elements (my_path_orders_else)
    
def main () -> None:
    """
    """    
            
    my_path_myTrades_open: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'open')        
    my_path_orders_open: str = system_tools.provide_path_for_file ('orders', 'eth', 'open')
    my_path_orders_cancelled: str = system_tools.provide_path_for_file ('orders', 'eth', 'cancelled')
    my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', 'eth', 'closed')
    my_path_orders_filled: str = system_tools.provide_path_for_file ('orders', 'eth', 'filled')
    my_path_myTrades_closed: str = system_tools.provide_path_for_file ('myTrades', 'eth', 'closed')        
    
    paths = [my_path_myTrades_open, 
                my_path_orders_open, 
                my_path_orders_cancelled, 
                my_path_orders_closed, 
                my_path_orders_filled, 
                my_path_myTrades_closed
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
