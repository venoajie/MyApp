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
         
    def open_orders_state_cancelled (self)-> list:
        
        '''
        '''   

        return [] if self.my_orders == [] else [o for o in self.my_orders if o['order_state'] == 'cancelled' ]   
    
    def open_orders_state_filled (self)-> list:
        
        '''
        '''   

        return [] if self.my_orders == [] else [o for o in self.my_orders if o['order_state'] == 'filled' ]   
    
    def open_orders_exist_in_my_trades (self)-> list:
        
        '''
        '''   
         
        my_trade_order_id = [o['order_id'] for o in self.my_trades ] 

        return [] if self.my_orders == [] else [o for o in self.my_orders if o['order_id'] in my_trade_order_id]   
    
    def open_orders_outstanding (self)-> list:
        
        '''
        '''   
         
        open_orders_id_cancelled = [] if self.my_orders == [] else [o['order_id'] for o in self.open_orders_state_cancelled () ] 
        exclude_cancelled = [] if open_orders_id_cancelled == [] else [o for o in self.my_orders if o['order_id'] not in open_orders_id_cancelled]  
        open_orders_id_filled = [] if self.my_orders == [] else [o['order_id'] for o in self.open_orders_state_filled () ] 
        exclude_filled = [] if open_orders_id_filled == [] else [o for o in self.my_orders if o['order_id'] not in open_orders_id_filled]   
        open_orders_id_exist_in_my_trades = [] if self.my_orders == [] else [o['order_id'] for o in self.open_orders_exist_in_my_trades () ] 
        #log.warning (f'{self.my_trades=}')
        #log.warning (f'{self.open_orders_exist_in_my_trades()=}')
        
        return [] if self.my_orders == [] else [o for o in self.my_orders  if o['order_id'] not in [open_orders_id_cancelled, open_orders_id_filled, open_orders_id_exist_in_my_trades]]   
    
    def update_open_orders_outstanding (self)-> list:
        
        '''
        '''   

        my_path_orders = system_tools.provide_path_for_file ('orders', self.currency) 
        #log.error (f'{self.open_orders_outstanding()=}')

        pickling.replace_data(my_path_orders, self.open_orders_outstanding())
                             

def main    ():
    
    currencies =  ['ETH','BTC']
    open_orders_open=[{'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1214.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3143810085', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1671682086221, 'label': 'hedging spot-open-1671682086198', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671682086221, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 9.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1214.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3143811854', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1671682113389, 'label': 'hedging spot-open-1671682113369', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671682113389, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 9.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1214.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3143817575', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1671682201883, 'label': 'hedging spot-open-1671682201862', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671682201883, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 9.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1214.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3143841752', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1671682530322, 'label': 'hedging spot-open-1671682530301', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671682530322, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 9.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1214.55, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3143864609', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1671682839931, 'label': 'hedging spot-open-1671682839912', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671682839931, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 9.0}]
    log.debug ([o for o in open_orders_open if o['order_id'] == 'ETH-3143875168' ] )
    
    for currency in currencies:
         
        my_trades_open_path = system_tools.provide_path_for_file ('myTrades', currency.lower())
        my_trades_open = pickling.read_data(my_trades_open_path)        
        
        my_path_orders = system_tools.provide_path_for_file ('orders', currency.lower())

        all_open_orders = pickling.read_data (my_path_orders)
        my_orders = open_orders_management.MyOrders(all_open_orders)
        my_orders_all = my_orders.my_orders_all()
        
        synchronizing = SynchronizingFiles (currency, my_orders_all, my_trades_open)
        synchronizing.update_open_orders_outstanding()
        cancel =synchronizing.open_orders_state_cancelled ()
        print (cancel)


if __name__ == "__main__":

    
    try:
        main()
        
    except Exception as error:
        log.error (error)
        message = f'SynchronizingFiles {error}'
        telegram_app.telegram_bot_sendtext(message)

    
