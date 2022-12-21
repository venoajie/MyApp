#!/usr/bin/python3


# installed
from dataclassy import dataclass
from portfolio.deribit import open_orders_management, myTrades_management
from utils import pickling, system_tools, telegram_app

from loguru import logger as log


@dataclass(unsafe_hash=True, slots=True)
class SynchronizingFiles ():

    
    '''
    '''       
    
    my_orders: list
    my_trades: list
            
    def my_orders_api (self)-> list:
        
        '''
        '''    
        return [] if self.my_orders == [] else [o for o in self.my_orders if o['api'] == True]    

def main    ():
    
    currencies =  ['ETH','BTC']
    
    for currency in currencies:

        file_name_orders = (f'{currency.lower()}-orders')    
                                
        my_path_orders = system_tools.provide_path_for_file (file_name_orders, "portfolio", "deribit")

        all_open_orders = pickling.read_data (my_path_orders)
        log.debug (my_path_orders)
        log.debug (all_open_orders)
        my_orders = open_orders_management.MyOrders(all_open_orders)
        log.info (my_orders)
        

        file_name_trades = (f'{currency.lower()}-myTrades-open') 
        my_trades_open_path = system_tools.provide_path_for_file (file_name_trades, "portfolio", "deribit")
        log.debug (my_trades_open_path)
        my_trades_open = pickling.read_data(my_trades_open_path)
        log.warning (my_trades_open)
        
        synchronizing = SynchronizingFiles (my_orders, my_trades_open)

if __name__ == "__main__":

    
    try:
        main()
        
    except Exception as error:
        message = f'SynchronizingFiles {error}'
        telegram_app.telegram_bot_sendtext(message, 10)

    
