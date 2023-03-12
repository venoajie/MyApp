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
                                     strategy_label) -> None:
        
        '''
        '''      

        try:
            result = ([o for o in open_transactions_label \
                if strategy_label in str_mod.get_strings_before_character(o['label'])])
        except:
            result = []

        return result
 
    def trade_based_on_label_strategy (self, 
                                       open_transactions_label,
                                       strategy_label,
                                       type: str = 'limit') -> None:
        
        '''
        '''      

        transactions = self.transactions_label_strategy(open_transactions_label,strategy_label)
        
        return {'net_sum_order_size': [] if transactions == [] else self.net_sum_order_size (transactions),
                'len_transactions': [] if transactions == [] else  len(transactions),
                'transaction_label_strategy_type': [] if transactions == [] else  ([o for o in transactions\
                if type in o['order_type'] ]),
                'instrument': [] if transactions == [] else  [ o["instrument_name"] for o in transactions ][0]
                }
    
    def determine_order_size_and_side_for_outstanding_transactions (self, 
                                 max_size: int, 
                                 strategy_from_outstanding_transactions: str,
                                 net_sum_current_position: int) -> None:

        """
        Determine order size based on current position size vs current position
        - Additional main order size
        - Exit order size
        - Side for every order size
            
        Args:
            net_sum_current_position (int): sum myTradebuy - sum myTradesell
            strategy_from_outstanding_transactions (str): taken from o/s my trades label (format example = supplyDemandShort60)

        Returns:
            dict
            
        Example:
            data_original = 'hedgingSpot-open-1671189554374' become 'hedgingSpot'
        
            
        
        """
        from strategies import entries_exits
        
        strategies = entries_exits.strategies
        
        try:     
            basic_strategy = str_mod.get_strings_before_character(strategy_from_outstanding_transactions,'-', 0) 
            side_basic_strategy = [o for o in strategies if basic_strategy in o['strategy'] ][0]['side']

            if side_basic_strategy == 'sell':
                
                # sell side is always negative
                max_size = max_size * -1 if max_size > 0 else max_size
                
                main_orders_sum_vs_max_orders = max_size - net_sum_current_position

                if main_orders_sum_vs_max_orders > 0:
                    remain_main_orders = 0
                    remain_exit_orders = (main_orders_sum_vs_max_orders)
                    side = 'buy'
                    
                if main_orders_sum_vs_max_orders < 0:
                    remain_main_orders = main_orders_sum_vs_max_orders
                    remain_exit_orders = 0
                    side = 'sell'
                    
                if main_orders_sum_vs_max_orders == 0:
                    remain_main_orders = 0
                    remain_exit_orders = 0
                    side = None
                    
            if side_basic_strategy == 'buy':
                
                main_orders_sum_vs_max_orders = net_sum_current_position - max_size

                if main_orders_sum_vs_max_orders > 0:
                    remain_main_orders = 0
                    remain_exit_orders = - main_orders_sum_vs_max_orders
                    side = 'sell'
                    
                if main_orders_sum_vs_max_orders < 0:
                    remain_main_orders = abs(main_orders_sum_vs_max_orders)
                    remain_exit_orders = 0
                    side = 'buy'
                    
                if main_orders_sum_vs_max_orders == 0:
                    remain_main_orders = 0
                    remain_exit_orders = 0
                    side = None
                    
            open_orders_from_db = self.open_orders_from_db
            # get open order with the respective strategy and order type take_limit
                # to optimise the profit, using take_limit as order type default order
                
            if open_orders_from_db != []:
                open_order_label_strategy_type_limit = self.trade_based_on_label_strategy (open_orders_from_db,
                                                                                      basic_strategy,
                                                                                      'limit')
                len_open_order_label_strategy_type_limit = open_order_label_strategy_type_limit ['len_transactions']            
                
                # get open order with the respective strategy and order type stop market
                    # to reduce the possibility of order not executed, stop loss using 
                        # stop market as order type default order
                open_order_label_strategy_type_market = self.trade_based_on_label_strategy (open_orders_from_db,
                                                                                        basic_strategy,
                                                                                        'stop_market')
                len_open_order_label_strategy_type_market = open_order_label_strategy_type_market ['len_transactions']
            
            return {'remain_main_orders': remain_main_orders,
                    'remain_exit_orders': remain_exit_orders,
                    #'proforma_size_ok': proforma_size < max_size,
                    'order_type_market': True if len_open_order_label_strategy_type_market == [] \
                        else len_open_order_label_strategy_type_market < 1,
                    'order_type_limit': True if len_open_order_label_strategy_type_limit == [] \
                        else  len_open_order_label_strategy_type_limit < 1,
                    'side': side
                    }
            
        except Exception as error:
            catch_error(error)
        
    def is_open_trade_has_exit_order_sl (self, open_trades_label, max_size, strategy) -> None:
        
        '''
        order type to search = stop market
        '''   
        trade_based_on_label_strategy = self.trade_based_on_label_strategy (open_trades_label, strategy)
        
        # get net position with the respective strategy
        net_position_based_on_label = trade_based_on_label_strategy ['net_sum_order_size']
        #log.error (net_position_based_on_label)
        
        # get open order with the respective strategy and order type stop market
            # to reduce the possibility of order not executed, stop loss using 
                # stop market as order type default order
        open_order_label_strategy_type = ([o for o in self. open_orders_from_db \
            if str_mod.get_strings_before_character(o['label']) == strategy \
                and o['order_type'] == 'stop_market']
                )
        len_open_order_label_strategy_type =  (len(open_order_label_strategy_type))

        # prepare net sum of the open order size based on label strategy
            # default net sum value (just in case there are no open orders)
        sum_open_order_label_strategy_type = 0
        
            # net sum operation
        if open_order_label_strategy_type !=[]:
            sum_open_order_label_strategy_type = self.net_sum_order_size([o for o in open_order_label_strategy_type ])
        
        # compare size per trade vs per order open. The amoungt should be 0/zero
        net_position = net_position_based_on_label + sum_open_order_label_strategy_type
        determine_size_and_side = self.determine_size_and_side (max_size, strategy, net_position_based_on_label)
        len_position_based_on_label = trade_based_on_label_strategy ['len_transactions']
        trade_position_exit_order_ok = len_position_based_on_label > 0 and net_position == 0
        #log.error (sum_open_order_label_strategy_type)
        log.error (trade_position_exit_order_ok)
            
        # tp has properly ordered if net position == 0
        #is_over_order = net_position == 0 
        #is_sl_ok = net_position_based_on_label != 0 and is_over_order and len_open_order_label_strategy_type > 0

        
        get_strategy_label = str_mod.get_strings_before_character (strategy,'-', 0)
        get_strategy_int = str_mod.get_strings_before_character (strategy,'-', 1)
        label_sl= f'{get_strategy_label}-closed-{get_strategy_int}'

        #log.info (f'net_position_based_on_label  {net_position_based_on_label} sum_open_order_label_strategy_type {sum_open_order_label_strategy_type}')
        #log.critical (f'net_position_based_on_label != 0 {net_position_based_on_label != 0} net_position == 0 {net_position == 0}')
        #log.critical (f'len_open_order_label_strategy_type {len_open_order_label_strategy_type} {len_open_order_label_strategy_type > 0}')
        log.warning (f'is_exit_order_ok  {len_open_order_label_strategy_type > 0}')
        # gather parameter items for order detail
        params = {'instrument': trade_based_on_label_strategy ['instrument'],
                  'size': abs(net_position),
                  'label': label_sl,
                  'side': determine_size_and_side['side'],
                  'type': 'stop_market'
                  }

        
        return {'is_exit_order_ok': len_open_order_label_strategy_type > 0 and trade_position_exit_order_ok,
                'current_order_len_exceeding_minimum': len_open_order_label_strategy_type > 1,
                'list_order_exceeding_minimum': open_order_label_strategy_type,
                'size_sl': abs(net_position),
                'params': params,
                'label_sl': label_sl 
                }


    def is_open_trade_has_exit_order_tp (self, open_trades_label, max_size, strategy) -> None:
        
        '''
        order type to search =  take limit
        '''   
         
        
        # get open order with the respective strategy and order type take_limit
            # to optimise the profit, using take_limit as order type default order
        open_order_label_strategy_type = ([o for o in self. open_orders_from_db \
            if str_mod.get_strings_before_character(o['label']) == strategy \
                and 'limit' in o['order_type'] ]
                )
        len_open_order_label_strategy_type =  (len(open_order_label_strategy_type))

        # prepare net sum of the open order size based on label strategy
            # default net sum value (just in case there are no open orders)
        sum_open_order_label_strategy_type = 0
        
            # net sum operation
        if open_order_label_strategy_type !=[]:
            sum_open_order_label_strategy_type = self.net_sum_order_size([o for o in open_order_label_strategy_type ])
        
        # compare size per trade vs per order open. The amoungt should be 0/zero
        net_position = net_position_based_on_label + sum_open_order_label_strategy_type
        determine_size_and_side = self.determine_size_and_side (max_size, strategy, net_position_based_on_label)
        log.warning (determine_size_and_side)
            
        # tp has properly ordered if net position == 0
        #is_over_order = net_position == 0 
        #is_tp_ok = net_position_based_on_label != 0 and is_over_order and len_open_order_label_strategy_type > 0
        get_strategy_label = str_mod.get_strings_before_character (strategy,'-', 0)
        get_strategy_int = str_mod.get_strings_before_character (strategy,'-', 1)

        label_tp= f'{get_strategy_label}-closed-{get_strategy_int}'
        
        # gather parameter items for order detail
        params = {'instrument': trade_based_on_label_strategy['instrument'],
                  'size': abs(net_position),
                  'label': label_tp,
                  'side': determine_size_and_side['side'],
                  'type': 'limit'
                  }
        return {'is_exit_order_ok': len_open_order_label_strategy_type > 0 and trade_position_exit_order_ok,
                'current_order_len_exceeding_minimum': len_open_order_label_strategy_type > 1,
                'list_order_exceeding_minimum': open_order_label_strategy_type,
                'size_tp': abs(net_position),
                'params': params,
                'label_tp': label_tp
                }
        
            
    def check_proforma_position(self, max_size, strategy, open_trades_label: float = []) -> None:

        """
        Check proforma: current position + new order/ check whether new order will exceed threhold
        """

        try:
            log.warning (f'max_size  {max_size}')
            log.warning (f'open_trades_label  {open_trades_label}')
            # [], None: indicate new order/position/label
            if  open_trades_label == []:
                exceed_threhold = False
            
            # indicate position has opened
            else:
                label_strategy =  strategy  ['strategy']
                log.error (f'trade_based_on_label_strategy  {label_strategy}')
                trade_based_on_label_strategy = self.trade_based_on_label_strategy (open_trades_label, label_strategy)
                log.error (f'trade_based_on_label_strategy  {trade_based_on_label_strategy}')
                
                # get net position with the respective strategy
                net_sum_current_position = trade_based_on_label_strategy ['net_sum_order_size']
                
                main_orders_sum_vs_max_orders = max_size - net_sum_current_position
                if strategy ['side'] == 'sell':
                    pass
                if strategy ['side'] == 'buy':
                    pass
                remain_main_orders = 0
                remain_exit_orders = 0
                log.error (f'net_sum_current_position  {net_sum_current_position}')
                side = 'sell' if (net_sum_current_position) > 0 else 'buy'
                side = 'buy' if (net_sum_current_position) < 0 else 'sell'
                
                # position has closed
                if net_sum_current_position == 0:
                    side = None
                    order_size = None
                    proforma_size = None
                    exceed_threhold = True
                    
                # net position in long
                if net_sum_current_position > 0:
                    order_size = (net_sum_current_position)
                    log.warning (order_size)
                    proforma_size = net_sum_current_position - order_size
                    log.warning (proforma_size)
                    exceed_threhold = proforma_size != 0
                    
                # net position in short
                if net_sum_current_position < 0:
                    order_size = (net_sum_current_position)
                    proforma_size = net_sum_current_position - order_size
                    exceed_threhold = proforma_size != 0


            return {'side': side,
                    'order_size': order_size,
                    'proforma_size': proforma_size,
                    'is_new_position_exceed_threhold': exceed_threhold
                    }
                
        except Exception as error:
            catch_error(error)
            
            
    def established_threshold_before_opening_order(self, label, open_order, trade_item
    ) -> None:

        """
        state: closed/open
        """
        max_order = 0

        try:
            if 'closed' in label:
                max_order = sum([o['amount'] for o in trade_item ]) - sum([o['amount'] for o in open_order ])
            if 'open' in label:
                max_order = None


            return max_order
                
        except Exception as error:
            catch_error(error)