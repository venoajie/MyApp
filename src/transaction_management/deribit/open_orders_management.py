# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log
from utilities import  pickling, system_tools, number_modification, string_modification as str_mod

def catch_error (error, idle: int = None) -> list:
    """
    """
    system_tools.catch_error_message(error, idle)


def telegram_bot_sendtext (bot_message, 
                           purpose: str = 'general_error'
                           ) -> None:
    from utilities import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

@dataclass(unsafe_hash=True, slots=True)
class MyOrders ():

    
    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up open orders data 
    '''       
    
    open_orders_from_db: list
            
    def open_orders_all (self)-> list:
        
        '''
        '''    
        none_data = [None, []]
        return [] if self.open_orders_from_db in none_data else self.open_orders_from_db 
    
    def open_orders_api (self)-> list:
        
        '''
        '''
        return [] if self.open_orders_all() == [] else [
            o for o in self.open_orders_all() if o['api'] == True
            ]
    
    def open_orders_manual (self)->list:
        
        '''
        '''    
        return [] if self.open_orders_all() == [] else  [
            o for o in self.open_orders_all() if o['api'] == False
            ]
    
    def open_orders_status (self, status)->list:
        
        '''
        '''    
        
        none_data = [None, []]
        
        try:
            trade_seq = [o ['trade_seq'] for o in self.open_orders_all()]
            orders_status = [o for o in self.open_orders_all() if o['state'] == status]
        except:
            orders_status = [o for o in self.open_orders_all() if o['order_state'] == status]
            
        return [] if self.open_orders_all() in none_data else  orders_status
    
    def open_orders_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        
        return [] if self.open_orders_api () == [] else  [
            o for o in self.open_orders_api () if  label in o['label'] ]
    
    def open_orders_api_last_update_timestamps (self)-> list:
        
        '''
        '''    
        return [] if self.open_orders_api () == [] else  [
            o['last_update_timestamp'] for o in self.open_orders_api ()
            ]
    
    def open_orders_api_basedOn_label_last_update_timestamps (self, 
                                                            label: str
                                                            )-> list:
        
        '''
        '''    
        return [] if self.open_orders_api_basedOn_label (label) == [] \
            else  [
                o['last_update_timestamp'] for o in self.open_orders_api_basedOn_label (label) 
                ]
    
    def open_orders_api_basedOn_label_last_update_timestamps_min (self, 
                                                                label: str
                                                                )-> list:
        
        '''
        '''    
        
        return [] if self.open_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  min (self.open_orders_api_basedOn_label_last_update_timestamps (label))
    
    def open_orders_api_basedOn_label_last_update_timestamps_max (self, 
                                                                label: str
                                                                )-> list:
        
        '''
        '''    
        
        return [] if self.open_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  max (self.open_orders_api_basedOn_label_last_update_timestamps (label))
    
    def open_orders_api_basedOn_label_last_update_timestamps_min_id (self, 
                                                                   label: str
                                                                   )-> list:
        
        '''
        '''    
        
        return [] if self.open_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  ([o['order_id'] for o in self.open_orders_api_basedOn_label (label) \
                if o['last_update_timestamp'] == self.open_orders_api_basedOn_label_last_update_timestamps_min (label)])[0]
            
    def open_orders_api_basedOn_label_last_update_timestamps_max_id (self, 
                                                                   label: str)-> list:
        
        '''
        '''    
        
        return [] if self.open_orders_api_basedOn_label_last_update_timestamps (label) == [] \
            else  ([o['order_id'] for o in self.open_orders_api_basedOn_label (label) \
                if o['last_update_timestamp'] == self.open_orders_api_basedOn_label_last_update_timestamps_max (label)])[0]
                        
    def open_orders_api_basedOn_label_items_qty (self, 
                                               label: str
                                               )-> list:
        
        '''
        '''    
        return [] if self.open_orders_api_basedOn_label (label) == [] \
            else  len ([o for o in self.open_orders_api_basedOn_label (label)])
            
    def open_orders_api_basedOn_label_items_net (self, 
                                               label: str = None
                                               )-> list: #! inconsistent output comparing to other funcs.
        
        '''
        '''   
        
        if label == None:
            
            result =  0 if self.open_orders_api () == [] \
                else  self.net_sum_order_size (self.open_orders_api ()) 
        
        else:
            #log.debug (self.open_orders_api () )
            result =  0 if self.open_orders_api_basedOn_label (label) == [] \
            else  self.net_sum_order_size (
                [o for o in self.open_orders_api_basedOn_label (
                    label
                    )
                 ]
                )
                
        return result
            
    def net_sum_order_size (self, 
                            selected_transactions: list
                            )-> float:
        
        '''
        '''           
        return number_modification.net_position (selected_transactions)
    
    def open_orders_api_basedOn_label_items_size (self, 
                                                label: str
                                                )-> list:
        
        '''
        '''    
        return [] if self.open_orders_api_basedOn_label (label) == [] \
            else  self.net_sum_order_size  (
                self.open_orders_api_basedOn_label (label)
                                      )
            
    def recognizing_order (self, 
                           order: dict
                           ) -> dict:
                
        ''' 
            
        Captured some order attributes
        
        Args:
            order (dict): Order from exchange.
            
        Returns:
            dict: explaining order state and order id.
    
        '''

        try: 
            
            log.info (order) # log the order to the log file
                
            if 'trade_seq' not in order: 
                
                # get the order id
                order_id= order ['order_id'] 
                
                # get the order state
                order_state = order ['order_state'] 
                
            if 'trade_seq' in order: 
                                   
                # get the order id
                order_id= order ['order_id'] 
                
                # get the order state
                order_state = order ['state'] 
                
        except Exception as error:
            catch_error (error)  

        return {'order_state_open': order_state == 'open', 
                'order_state_else': order_state != 'open', 
                'order_id': order_id}
    
    def combine_open_orders_based_on_id (self, 
                                         open_orders_open: list, 
                                         order_id: str) -> dict:
        
        '''
        '''                   
        return {'item_with_same_id': [o for o in open_orders_open if o['order_id'] == order_id ],
                'item_with_diff_id': [o for o in open_orders_open if o['order_id'] != order_id ]
                }
            
    def compare_open_order_per_db_vs_get(self,
                                         open_orders_from_sub_account_get: list) -> int:
        
        '''
        ''' 

        try:
            
            both_sources_are_equivalent =  open_orders_from_sub_account_get == self. open_orders_from_db
            #log.critical (f'both_sources_are_equivalent {both_sources_are_equivalent} open_order_from_get {open_orders_from_sub_account_get} open_order_from_db {self. open_orders_from_db}')
            
            if both_sources_are_equivalent == False:
                    info= (f'OPEN ORDER DIFFERENT open_order_from_get \
                        {open_orders_from_sub_account_get}  \
                            open_order_from_db \
                                {self. open_orders_from_db} \n ')
                    telegram_bot_sendtext(info) 
                #log.warning (f'difference {difference}')
                
            return  both_sources_are_equivalent
                    
        except Exception as error:
            catch_error (error)
                        
                        
    def open_orderLabelCLosed (self, 
                                     open_orders: list = None
                                     ) -> list:
        
        '''
        Get order with closed labels  but have no open labels  pair
        The result should be further compared to open trades with open labels
        '''                   
        
        
        
        if open_orders == None:
            open_orders = self.open_orders_from_db
            
        # get order with open labels
        order_label_open = [str_mod.extract_integers_from_text (o['label']) \
            for o in open_orders if 'open' in (o['label']) ]

        # furthermore, extract order with closed label but not
            # registered in open labels above 
        
        order_label_closed = [str_mod.extract_integers_from_text (o['label']) \
            for o in open_orders if 'closed' in (o['label']) \
                and str_mod.extract_integers_from_text (o['label']) not in order_label_open ]
        
        #log.error (str_mod.remove_redundant_elements (order_label_closed))
        # remove redundant labels
        return str_mod.remove_redundant_elements (order_label_closed)
    
    def distribute_order_transactions (self, 
                                       currency
                                       ) -> None:
        
        '''
        '''       
       
        from loguru import logger as log
        
        my_path_orders_open = system_tools.provide_path_for_file ('orders', 
                                                                  currency, 
                                                                  'open'
                                                                  )
        try:
            
            if self.open_orders_from_db: 
                log.debug (self.open_orders_from_db)
                
                for order in self.open_orders_from_db:
                            
                    order_state = self.recognizing_order (order)
                    log.critical (order_state)
            
                    if order_state ['order_state_open']:
                        log.error ('ORDER_STATE OPEN')
                        log.info (f'{order=}')
                        
                        pickling.append_and_replace_items_based_on_qty (my_path_orders_open, 
                                                                        order, 
                                                                        1000, 
                                                                        True)
                        
                    if order_state ['order_state_else']:
                        
                        my_path_orders_else = system_tools.provide_path_for_file ('orders', 
                                                                                  currency, 
                                                                                  'else'
                                                                                  )
                        log.critical ('ORDER_STATE ELSE')
                        log.info (f'{order=}')
                        log.critical (f'{order_state=}')
                        log.critical (f'{my_path_orders_else=}')
                        
                        order_id = order_state ['order_id']
                        
                        open_orders_open = pickling.read_data (my_path_orders_open) 
                        
                        item_in_open_orders_open = self.combine_open_orders_based_on_id(open_orders_open, 
                                                                                        order_id
                                                                                        )
                        log.info (f'{open_orders_open=}')
                        log.debug (f'{item_in_open_orders_open=}')
                        
                        item_with_same_id = item_in_open_orders_open ['item_with_same_id'] 
                        item_with_diff_id = item_in_open_orders_open ['item_with_diff_id'] 
                        
                        pickling.append_and_replace_items_based_on_qty (my_path_orders_else, 
                                                                        order, 
                                                                        1000, 
                                                                        True
                                                                        )
                        
                        if item_with_same_id != []:

                            pickling.append_and_replace_items_based_on_qty (my_path_orders_else,
                                                                            item_with_same_id, 
                                                                            100000, 
                                                                            True
                                                                            )
                            
                        pickling.replace_data (my_path_orders_open, 
                                               item_with_diff_id,
                                               True
                                               )
                        
            else:
                pickling.replace_data (my_path_orders_open, [], True)
                        
        except Exception as error:
            catch_error (error)
            
    def transactions_label_strategy (self, 
                                     open_transactions_label,
                                     strategy) -> None:
        
        '''
        '''      
        return ([o for o in open_transactions_label \
            if str_mod.get_strings_before_character(o['label']) == strategy])
 
    def net_sum_trade_size_based_on_label_strategy (self, 
                                           open_transactions_label,
                                           strategy) -> None:
        
        '''
        '''      
        return self.net_sum_order_size (self.transactions_label_strategy(open_transactions_label,strategy))
    
        
    def is_open_trade_has_exit_order_sl (self, open_trades_label, strategy) -> None:
        
        '''
        order type to search = stop market
        '''   
        # get net position with the respective strategy
        net_position_based_on_label = self.net_sum_trade_size_based_on_label_strategy (open_trades_label, strategy)
        
        # get open order with the respective strategy and order type stop market
            # to reduce the possibility of order not executed, stop loss using 
                # stop market as order type default order
        open_order_label_strategy_type = ([o for o in self. open_orders_from_db \
            if str_mod.get_strings_before_character(o['label']) == strategy \
                and o['order_type'] == 'stop_market']
                )

        # prepare net sum of the open order size based on label strategy
            # default net sum value (just in case there are no open orders)
        sum_open_order_label_strategy_type = 0
        
            # net sum operation
        if open_order_label_strategy_type !=[]:
            sum_open_order_label_strategy_type = self.net_sum_order_size([o for o in open_order_label_strategy_type ])
        
        # compare size per trade vs per order open. The amoungt should be 0/zero
        net_position = net_position_based_on_label + sum_open_order_label_strategy_type
            
        # tp has properly ordered if net position == 0
        is_sl_ok = net_position_based_on_label != 0 and net_position == 0

        
        get_strategy_label = str_mod.get_strings_before_character (strategy,'-', 0)
        get_strategy_int = str_mod.get_strings_before_character (strategy,'-', 1)
        params = {'instrument': abs(net_position),
                  'size': abs(net_position),
                  'label': label_sl,
                  'type': 'stop_market',
                  'trigger_price': trigger_price,
                  
                  }

        label_sl= f'{get_strategy_label}-closed-{get_strategy_int}'
        
        return {'is_sl_ok': is_sl_ok,
                'size_sl': abs(net_position),
                'params': params,
                'label_sl': label_sl }


    def is_open_trade_has_exit_order_tp (self, open_trades_label, strategy) -> None:
        
        '''
        order type to search =  take limit
        '''   
         
        # get net position of the respective strategy
        net_position_based_on_label = self.net_sum_trade_size_based_on_label_strategy (open_trades_label, strategy)
        
        # get open order with the respective strategy and order type take_limit
            # to optimise the profit, using take_limit as order type default order
        open_order_label_strategy_type = ([o for o in self. open_orders_from_db \
            if str_mod.get_strings_before_character(o['label']) == strategy \
                and o['order_type'] == 'take_limit']
                )

        # prepare net sum of the open order size based on label strategy
            # default net sum value (just in case there are no open orders)
        sum_open_order_label_strategy_type = 0
        
            # net sum operation
        if open_order_label_strategy_type !=[]:
            sum_open_order_label_strategy_type = self.net_sum_order_size([o for o in open_order_label_strategy_type ])
        
        # compare size per trade vs per order open. The amoungt should be 0/zero
        net_position = net_position_based_on_label + sum_open_order_label_strategy_type
            
        # tp has properly ordered if net position == 0
        is_tp_ok = net_position_based_on_label != 0 and net_position == 0
        get_strategy_label = str_mod.get_strings_before_character (strategy,'-', 0)
        get_strategy_int = str_mod.get_strings_before_character (strategy,'-', 1)

        label_tp= f'{get_strategy_label}-closed-{get_strategy_int}'
        
        return {'is_tp_ok': is_tp_ok,
                'size_tp': abs(net_position),
                'instrument': abs(net_position),
                'label_tp': label_tp }