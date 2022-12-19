# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log
@dataclass(unsafe_hash=True, slots=True)
class MyOrders ():

    
    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up open orders data 
    '''       
    
    my_orders: list
            
    def my_orders_api (self)-> list:
        
        '''
        '''    
        return [] if self.my_orders == [] else [o for o in self.my_orders if o['api'] == True]
    
    def my_orders_manual (self)->list:
        
        '''
        '''    
        return [] if self.my_orders == [] else  [o for o in self.my_orders if o['api'] == False]
    
    
    def my_orders_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api () == [] else  ([o for o in self.my_orders_api () if  label in o['label'] ])
    
    def my_orders_api_last_update_timestamps (self)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api () == [] else  ([o['last_update_timestamp'] for o in self.my_orders_api ()])
    
    def my_orders_api_basedOn_label_last_update_timestamps (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  ([o['last_update_timestamp'] for o in self.my_orders_api_basedOn_label (label) ])
    
    def my_orders_api_basedOn_label_last_update_timestamps_min (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.my_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  min (self.my_orders_api_basedOn_label_last_update_timestamps (label))
    
    def my_orders_api_basedOn_label_last_update_timestamps_min_id (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.my_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  ([o['order_id'] for o in self.my_orders_api_basedOn_label (label) \
                if o['last_update_timestamp'] == self.my_orders_api_basedOn_label_last_update_timestamps_min (label)])[0]
            
            
    def my_orders_api_basedOn_label_items_qty (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  len ([o for o in self.my_orders_api_basedOn_label (label)])