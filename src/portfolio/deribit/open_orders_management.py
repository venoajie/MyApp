# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass

@dataclass(unsafe_hash=True, slots=True)
class MyOrders ():

    
    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up open orders data 
    '''       
    
    my_orders: list
            
    def my_orders_all (self)-> list:
        
        '''
        '''    
        return [] if self.my_orders == [] else self.my_orders 
    
    def my_orders_api (self)-> list:
        
        '''
        '''    
        return [] if self.my_orders_all() == [] else [o for o in self.my_orders_all() if o['api'] == True]
    
    def my_orders_manual (self)->list:
        
        '''
        '''    
        return [] if self.my_orders_all() == [] else  [o for o in self.my_orders_all() if o['api'] == False]
    
    
    def my_orders_status (self, status)->list:
        
        '''
        '''    
        print (self.my_orders_all())
        none_data = [None, []]
        return [] if self.my_orders_all() in none_data else  [o for o in self.my_orders_all() if o['order_state'] == status]
    
    
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
    
    def my_orders_api_basedOn_label_last_update_timestamps_max (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.my_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  max (self.my_orders_api_basedOn_label_last_update_timestamps (label))
    
    def my_orders_api_basedOn_label_last_update_timestamps_min_id (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.my_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  ([o['order_id'] for o in self.my_orders_api_basedOn_label (label) \
                if o['last_update_timestamp'] == self.my_orders_api_basedOn_label_last_update_timestamps_min (label)])[0]
            
    def my_orders_api_basedOn_label_last_update_timestamps_max_id (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.my_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  ([o['order_id'] for o in self.my_orders_api_basedOn_label (label) \
                if o['last_update_timestamp'] == self.my_orders_api_basedOn_label_last_update_timestamps_max (label)])[0]
            
            
    def my_orders_api_basedOn_label_items_qty (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  len ([o for o in self.my_orders_api_basedOn_label (label)])
            
    def my_orders_api_basedOn_label_items_net (self, label: str)-> list:
        
        '''
        '''   
        from utils import number_modification 
        return 0 if self.my_orders_api_basedOn_label (label) == [] \
            else  number_modification.net_position ( ([o for o in self.my_orders_api_basedOn_label (label)]))
            
            
    def my_orders_api_basedOn_label_items_size (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  sum ([o['amount'] for o in self.my_orders_api_basedOn_label (label)])
            
    def check_whether_orders_have_excecuted (self)-> list:
        
        '''
        '''    
        pass