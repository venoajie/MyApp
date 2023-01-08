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
        #print (f'my_orders_status {self.my_orders_all()}')
        none_data = [None, []]
        return [] if self.my_orders_all() in none_data else  [o for o in self.my_orders_all() if o['order_state'] == status]
    
    
    def my_orders_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        #print (f'my_orders_api_basedOn_label {self.my_orders_api()}')
        none_data = [None, []]
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
            
    def my_orders_api_basedOn_label_items_net (self, label: str)-> list: #! inconsistent output comparing to other funcs.
        
        '''
        '''   
        from utils import number_modification 
        return 0 if self.my_orders_api_basedOn_label (label) == [] \
            else  number_modification.net_position ( ([o for o in self.my_orders_api_basedOn_label (label)]))
            
    def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        from utils import number_modification
        return number_modification.net_position (selected_transactions)
    
    def my_orders_api_basedOn_label_items_size (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  self.net_position  (self.my_orders_api_basedOn_label (label))
            
    def distribute_order_transactions (self, currency) -> None:
        
        '''
        trade_sources: 'API'
        '''       
        from utils import pickling, system_tools
        from loguru import logger as log
        
        my_path_orders_open = system_tools.provide_path_for_file ('orders', currency, 'open')
        log.error (self.my_orders)
        
        if self.my_orders:
            

            for order in self.my_orders:
                
                log.warning (f'{self.my_orders=}')
                
                order_state = order ['order_state']
                order_id= order ['order_id']
                
                
                my_path_orders_else = system_tools.provide_path_for_file ('orders', currency, order_state)
                open_orders_open = pickling.read_data (my_path_orders_open) 
                log.debug (f'BEFORE {open_orders_open=}')
                #log.warning (f'{order_state=}')
                
                if order_state == 'open':
                    #log.error ('ORDER_STATE OPEN')
                    
                    pickling.append_and_replace_items_based_on_qty (my_path_orders_open, order, 1000, True)
                    pickling.check_duplicate_elements (my_path_orders_open)
                    
                else:
                    #log.error ('ORDER_STATE ELSE')
                    log.info (f'{order=}')
                    item_in_open_orders_open_with_same_id =  [o for o in open_orders_open if o['order_id'] == order_id ] 
                    item_in_open_orders_open_with_diff_id =  [o for o in open_orders_open if o['order_id'] != order_id ] 
                    #log.info (f'{item_in_open_orders_open_with_same_id=}')
                    #log.warning (f'{item_in_open_orders_open_with_diff_id=}')
                    
                    pickling.append_and_replace_items_based_on_qty (my_path_orders_else, order, 1000, True)
                    pickling.check_duplicate_elements (my_path_orders_else)
                    
                    if item_in_open_orders_open_with_same_id != []:
                        #log.critical ('item_in_open_orders_open_with_same_id')
                        pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id, 100000, True)
                        pickling.check_duplicate_elements (my_path_orders_else)
                        
                    pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id, True)
                    pickling.check_duplicate_elements (my_path_orders_open)
        else:
            pickling.replace_data (my_path_orders_open, [], True)
                    
    def check_whether_orders_have_excecuted (self)-> list:
        
        '''
        '''    
        pass
    
    