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
    
    currency: list
    my_orders: list
    my_trades: list
            
    def transfer_manual_orders (self)-> list:
        
        '''
        '''   
         
    def open_orders_exist_in_my_trades (self)-> list:
        
        '''
        '''   
         
        my_trade_order_id = [o['order_id'] for o in self.my_trades ] 

        return [] if self.my_orders == [] else [o for o in self.my_orders if o['order_id'] in my_trade_order_id]   
    
    def open_orders_outstanding (self)-> list:
        
        '''
        '''   
         
        open_orders_id_exist_in_my_trades = [] if self.my_orders == [] else [o['order_id'] for o in self.open_orders_exist_in_my_trades () ] 
        log.warning (f'{self.my_trades=}')
        log.warning (f'{self.open_orders_exist_in_my_trades()=}')
        
        return [] if self.my_orders == [] else [o for o in self.my_orders if o['order_id'] not in open_orders_id_exist_in_my_trades]   
    
    def update_open_orders_outstanding (self)-> list:
        
        '''
        '''   

        my_path_orders = system_tools.provide_path_for_file ('orders', self.currency) 
        log.error (f'{self.open_orders_outstanding()=}')

        pickling.replace_data(my_path_orders, self.open_orders_outstanding())
                             

def main    ():
    
    currencies =  ['ETH','BTC']
    
    for currency in currencies:
         
        my_trades_open_path = system_tools.provide_path_for_file ('myTrades', currency.lower())
        my_trades_open = pickling.read_data(my_trades_open_path)        
        
        my_path_orders = system_tools.provide_path_for_file ('orders', currency.lower())

        all_open_orders = pickling.read_data (my_path_orders)
        my_orders = open_orders_management.MyOrders(all_open_orders)
        my_orders_all = my_orders.my_orders_all()
        
        synchronizing = SynchronizingFiles (currency, my_orders_all, my_trades_open)
        synchronizing.update_open_orders_outstanding()


if __name__ == "__main__":

    
    try:
        main()
        
    except Exception as error:
        log.error (error)
        message = f'SynchronizingFiles {error}'
        telegram_app.telegram_bot_sendtext(message)

    
