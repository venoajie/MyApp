# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log

def catch_error (error, idle: int = None) -> list:
    """
    """
    from utilities import system_tools
    system_tools.catch_error_message(error, idle)

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
        none_data = [None, []]
        return [] if self.my_orders in none_data else self.my_orders 
    
    def my_orders_api (self)-> list:
        
        '''
        '''     
        log.warning (self.my_orders_all() )
        log.warning ([o for o in self.my_orders_all() if o['api'] == True])
        return [] if self.my_orders_all() == [] else [o for o in self.my_orders_all() if o['api'] == True]
    
    def my_orders_manual (self)->list:
        
        '''
        '''    
        return [] if self.my_orders_all() == [] else  [o for o in self.my_orders_all() if o['api'] == False]
    
    def my_orders_status (self, status)->list:
        
        '''
        '''    
        
        none_data = [None, []]
        
        try:
            trade_seq = [o ['trade_seq'] for o in self.my_orders_all()]
            orders_status = [o for o in self.my_orders_all() if o['state'] == status]
        except:
            orders_status = [o for o in self.my_orders_all() if o['order_state'] == status]
            
        return [] if self.my_orders_all() in none_data else  orders_status
    
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
            
    def my_orders_api_basedOn_label_items_net (self, label: str = None)-> list: #! inconsistent output comparing to other funcs.
        
        '''
        '''   
        from utilities import number_modification  
        
        if label == None:
            result =  0 if self.my_orders_api () == [] else  number_modification.net_position (self.my_orders_api ()) 
        
        else:
            result =  0 if self.my_orders_api_basedOn_label (label) == [] \
            else  number_modification.net_position (
                ([o for o in self.my_orders_api_basedOn_label (label)]))
                
        return result
            
    def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        from utilities import number_modification
        
        return number_modification.net_position (selected_transactions)
    
    def my_orders_api_basedOn_label_items_size (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_orders_api_basedOn_label (label) == [] \
            else  self.net_position  (self.my_orders_api_basedOn_label (label))
            
    def recognize_order_transactions (self, order) -> dict:
        
        '''
        '''       

        try:
            log.info (order)
                
            # filter out trading (somehow, they mixed into order transactions)
            if 'trade_seq' not in order:
                
                order_id= order ['order_id']
                order_state = order ['order_state']
                
            # filter out trading (somehow, they mixed into order transactions)
            if 'trade_seq' in order:
                                   
                order_id= order ['order_id']
                order_state = order ['state']
                
        except Exception as error:
            catch_error (error)

        return {'order_state_open': order_state == 'open' or order_state == 'triggered',
                'order_state_else': order_state != 'open',
                'order_id': order_id}
    
    def combine_open_orders_based_on_id (self, 
                                         open_orders_open, 
                                         order_id) -> dict:
        
        '''
        '''                   
        return {'item_in_open_orders_open_with_same_id': [o for o in open_orders_open if o['order_id'] == order_id ],
                'item_in_open_orders_open_with_diff_id': [o for o in open_orders_open if o['order_id'] != order_id ]
                }
                        
    def distribute_order_transactions (self, currency) -> None:
        
        '''
        '''       
        from utilities import pickling, system_tools
        from loguru import logger as log
        
        my_path_orders_open = system_tools.provide_path_for_file ('orders', currency, 'open')

        try:
            
            if self.my_orders:
                
                for order in self.my_orders:
                            
                    order_state = self.recognize_order_transactions (order)
            
                    if order_state ['order_state_open']:
                        log.error ('ORDER_STATE OPEN')
                        log.info (f'{order=}')
                        
                        pickling.append_and_replace_items_based_on_qty (my_path_orders_open, order, 1000, True)
                        
                    if order_state ['order_state_else']:
                        log.critical ('ORDER_STATE ELSE')
                        log.info (f'{order=}')
                        
                        order_id = order_state ['order_id']
                        
                        my_path_orders_else = system_tools.provide_path_for_file ('orders', currency, order_state)
                        open_orders_open = pickling.read_data (my_path_orders_open) 
                        
                        item_in_open_orders_open = self.combine_open_orders_based_on_id(open_orders_open, order_id)
                        log.info (f'{open_orders_open=}')
                        log.debug (f'{item_in_open_orders_open=}')
                        
                        item_in_open_orders_open_with_same_id = item_in_open_orders_open ['item_in_open_orders_open_with_same_id'] 
                        item_in_open_orders_open_with_diff_id = item_in_open_orders_open ['item_in_open_orders_open_with_diff_id'] 
                        
                        pickling.append_and_replace_items_based_on_qty (my_path_orders_else, order, 1000, True)
                        #result_example = [
                        #    {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, #'reduce_only': False, 'profit_loss': 0.0, 'price': 1547.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'filled', #'order_id': 'ETH-3249516850', 'mmp': False, 'max_show': 53.0, 'last_update_timestamp': 1673675558839, 'label': #'hedgingSpot-open-1673675540', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 53.0, 'direction': #'sell', 'creation_timestamp': 1673675541623, 'commission': 0.0, 'average_price': 1547.6, 'api': True, 'amount': 53.0}, 
                        #    {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, #'reduce_only': False, 'profit_loss': 0.0, 'price': 1547.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', #'order_id': 'ETH-3249516850', 'mmp': False, 'max_show': 53.0, 'last_update_timestamp': 1673675541623, 'label': #'hedgingSpot-open-1673675540', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', #'creation_timestamp': 1673675541623, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 53.0}
                        #    ]
                        
                        if item_in_open_orders_open_with_same_id != []:

                            pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id, 100000, True)
                            
                        pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id, True)
                        
            else:
                pickling.replace_data (my_path_orders_open, [], True)
                        
        except Exception as error:
            catch_error (error)
            
    #! will be deleted !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
    def distribute_order_transactions_ (self, currency) -> None:
        
        '''
        '''       
        from utilities import pickling, system_tools
        from loguru import logger as log
        
        my_path_orders_open = system_tools.provide_path_for_file ('orders', currency, 'open')
        #log.error (self.my_orders)
        try:
            order_state = self.recognize_order_transactions ()
                
            if self.my_orders:
                
                for order in self.my_orders:
                    log.warning ('trade_seq' not in order)
                    if 'trade_seq'not in order:
                        
                        #log.error (f'{self.my_orders=}')
                        log.warning (f'{order=}')
                            
                        order_id= order ['order_id']
                        order_state = order ['order_state']
                        
                        my_path_orders_else = system_tools.provide_path_for_file ('orders', currency, order_state)
                        open_orders_open = pickling.read_data (my_path_orders_open) 
                        
                        if order_state == 'open':
                            log.error ('ORDER_STATE OPEN')
                            log.info (f'{order=}')
                            
                            pickling.append_and_replace_items_based_on_qty (my_path_orders_open, order, 1000, True)
                            
                        else:
                            log.critical ('ORDER_STATE ELSE')
                            log.info (f'{order=}')
                            log.info (f'{open_orders_open=}')
                            item_in_open_orders_open_with_same_id =  [o for o in open_orders_open if o['order_id'] == order_id ] 
                            item_in_open_orders_open_with_diff_id =  [o for o in open_orders_open if o['order_id'] != order_id ] 
                            log.debug (f'{item_in_open_orders_open_with_same_id=}')
                            
                            pickling.append_and_replace_items_based_on_qty (my_path_orders_else, order, 1000, True)
                            #result_example = [
                            #    {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, #'reduce_only': False, 'profit_loss': 0.0, 'price': 1547.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'filled', #'order_id': 'ETH-3249516850', 'mmp': False, 'max_show': 53.0, 'last_update_timestamp': 1673675558839, 'label': #'hedgingSpot-open-1673675540', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 53.0, 'direction': #'sell', 'creation_timestamp': 1673675541623, 'commission': 0.0, 'average_price': 1547.6, 'api': True, 'amount': 53.0}, 
                            #    {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, #'reduce_only': False, 'profit_loss': 0.0, 'price': 1547.6, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', #'order_id': 'ETH-3249516850', 'mmp': False, 'max_show': 53.0, 'last_update_timestamp': 1673675541623, 'label': #'hedgingSpot-open-1673675540', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', #'creation_timestamp': 1673675541623, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 53.0}
                            #    ]
                            
                            if item_in_open_orders_open_with_same_id != []:

                                pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id, 100000, True)
                                
                            pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id, True)

            else:
                pickling.replace_data (my_path_orders_open, [], True)
                        
        except Exception as error:
            catch_error (error)
        
    