# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass

@dataclass(unsafe_hash=True, slots=True)
class MyTrades ():

    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up my trades data
    '''       
    my_trades: list
            
    def my_trades_api (self) -> list:
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == True]
    
    def my_trades_manual (self) -> list:
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == False]
    
    
    
    def my_trades_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_trades_api () == [] else  ([o for o in self.my_trades_api () if  label in o['label'] ])
    
    def my_trades_api_net_position(self, selected_trades: list) -> list:
        
        '''
        '''    

        if selected_trades != []:
            sum_closed_trades_in_my_trades_open_sell = ([o['amount'] for o in selected_trades if o['direction']=='sell'  ])
            sum_closed_trades_in_my_trades_open_sell = 0 if sum_closed_trades_in_my_trades_open_sell == [] else sum(sum_closed_trades_in_my_trades_open_sell)
            sum_closed_trades_in_my_trades_open_buy = sum([o['amount'] for o in selected_trades if o['direction']=='buy'  ])
            sum_closed_trades_in_my_trades_open_buy = 0 if sum_closed_trades_in_my_trades_open_buy == [] else sum(sum_closed_trades_in_my_trades_open_buy)
                
        return [] if selected_trades == [] else  sum_closed_trades_in_my_trades_open_buy - sum_closed_trades_in_my_trades_open_sell
    
    def distribute_trade_transaction (self, currency: str) -> None:
        
        '''
        '''       
        from utils import string_modification, pickling, system_tools
        

        my_trades_path_open = system_tools.provide_path_for_file ('myTrades', currency, 'open')
        my_trades_path_closed = system_tools.provide_path_for_file ('myTrades', currency, 'closed')

        for data_order in self.my_trades:
            data_order = [data_order]
            #log.info (f'DATA FROM EXC LOOP {data_order=}')
            
            #determine label id. 
            try:
                label_id= data_order [0]['label']
                trade_seq= data_order [0]['trade_seq']
            except:
                label_id= []
                trade_seq= []
            
            # for data with label id/ordered through API    
            if label_id != []:
                pass

            closed_label_id_int = string_modification.extract_integers_from_text(label_id)
            ##log.info (f' {label_id=}  {trade_seq=}  {closed_label_id_int} \n ')

            
            #! DISTRIBUTE trading transaction as per label id
            if 'open' in label_id:
#                log.error ('LABEL ID OPEN')

                # append trade to db.check potential duplicate
                pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_order , 10000, True)
                pickling.check_duplicate_elements (my_trades_path_open)
                
            if 'closed' in label_id:
                from loguru import logger as log
                #log.debug ('LABEL ID CLOSED')
                
                # fetch previous open trading data from local db
                my_trades_open = pickling.read_data(my_trades_path_open)  
                
                # filter open trades which have the same label id with trade transaction
                closed_trades_in_my_trades_open = ([o for o in my_trades_open if  str(closed_label_id_int)  in o['label'] ])
                # sum transaction with the same label id
                sum_closed_trades_in_my_trades_open_net = self.my_trades_api_net_position (closed_trades_in_my_trades_open)
                log.critical (f'{sum_closed_trades_in_my_trades_open_net=} {closed_trades_in_my_trades_open=}')
                
                # if net transaction != 0: transaction closing process not completed yet. all transaction with the same id stay in open db
                if sum_closed_trades_in_my_trades_open_net !=0:
                    log.critical (trade_seq)
                    
                    # put the trading at open db until fully closed (buy = sell)
                    pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_order , 10000, True)
                    pickling.check_duplicate_elements (my_trades_path_open)
                    
                #! SYNCHRONIZATION (DIFF SYSTEM VS DB)
                my_trades = self.my_trades
                log.debug ( len (my_trades))
                if len (my_trades) > 1:
                    log.error (str(closed_label_id_int))
                    
                                        
                    label = 'label' # https://www.appsloveworld.com/coding/python3x/291/how-to-handle-missing-keys-in-list-of-json-objects-in-python
                    for key in my_trades:
                        if label not in key:
                            key [label] = []
       
                    #log.debug ((my_trades))
                    mixed_trades_with_the_same_label = ([o for o in my_trades if  str(closed_label_id_int)  in o['label'] ])
                    sum_mixed_trades_in_my_trades_open_net = self.my_trades_api_net_position (mixed_trades_with_the_same_label)
                    log.critical (f'{sum_mixed_trades_in_my_trades_open_net=} {mixed_trades_with_the_same_label=}')
                    if sum_mixed_trades_in_my_trades_open_net != 0:
                        for data_order in mixed_trades_with_the_same_label:
                                
                            pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_order , 10000, True)
                            pickling.check_duplicate_elements (my_trades_path_open)
                            
                    if sum_mixed_trades_in_my_trades_open_net == 0: 

                        remaining_open_trades = ([o for o in my_trades if  str(closed_label_id_int)  not in o['label']  ])     
                        log.critical (remaining_open_trades)               
                        for data_order in remaining_open_trades:
                                            
                            try:
                                label_id= data_order [0]['label']
                            except:
                                label_id= []
                            
                            # for data with label id/ordered through API    
                            if label_id != []:
                                log.critical (data_order)   
                            
                                pickling.replace_data (my_trades_path_open, data_order, True )
                                pickling.check_duplicate_elements (my_trades_path_open)                                
                        
                # transaction has fully completed. move all the transactions with the same id to closed db
                if sum_closed_trades_in_my_trades_open_net == 0:
                                                    
                    #update mytrades db with the closed ones
                    #! AT CLOSED DB
                    pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, closed_trades_in_my_trades_open , 10000, True)
                    pickling.check_duplicate_elements (my_trades_path_closed)

                    #! AT OPEN DB
                    # SEPARATE OPEN AND CLOSED TRANSACTIONS IN OPEN DB
                    #update mytrades db with the still open ones
                    #my_trades_open = pickling.read_data(my_trades_path_open)  
                    remaining_open_trades = ([o for o in my_trades_open if  str(closed_label_id_int)  not in o['label'] ])                    
                    pickling.replace_data (my_trades_path_open, remaining_open_trades, True )
                    pickling.check_duplicate_elements (my_trades_path_open)
                                        
                if label_id == [] :
                    my_trades_path_manual = system_tools.provide_path_for_file ('myTrades', currency, 'manual')
                    #log.error ('[]')
                    pickling.append_and_replace_items_based_on_qty (my_trades_path_manual, data_order, 10000, True)                                    
            
    def my_trades_max_price_attributes_filteredBy_label (self, trade_sources_filtering: list) -> dict:
        
        '''
        trade_sources: 'API'
        '''       
        my_trades = []
        if trade_sources_filtering != None:
            my_trades = self.my_trades_api_basedOn_label (trade_sources_filtering)

        if my_trades !=[]:
            max_price = max ([o['price'] for o in my_trades])
            trade_list_with_max_price =  ([o for o in my_trades if o['price'] == max_price ])
            len_trade_list_with_max_price = len(trade_list_with_max_price)
            
            # if multiple items, select only the oldest one
            if len_trade_list_with_max_price > 0:
                trade_list_with_max_price_min_timestamp = min([o['timestamp'] for o in trade_list_with_max_price])
                trade_list_with_max_price =  ([o for o in trade_list_with_max_price if o['timestamp'] == trade_list_with_max_price_min_timestamp ])
            
            return  {
                'max_price': max_price,
                'trade_id':  ([o['trade_id'] for o in trade_list_with_max_price])[0] ,
                'timestamp':  ([o['timestamp'] for o in trade_list_with_max_price])[0] ,
                'order_id':  ([o['order_id'] for o in trade_list_with_max_price])[0] ,
                'instrument':  ([o['instrument_name'] for o in trade_list_with_max_price])[0] ,
                'size':  ([o['amount'] for o in trade_list_with_max_price])[0] ,
                'label':  ([o['label'] for o in trade_list_with_max_price])[0] ,
            
            }
        if my_trades ==[]:
            return []