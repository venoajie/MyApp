# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log
from utilities import pickling, system_tools, string_modification

def catch_error (error, idle: int = None) -> list:
    """
    """
    from utilities import system_tools
    system_tools.catch_error_message(error, idle)

def telegram_bot_sendtext (bot_message, 
                           purpose: str = 'general_error'
                           ) -> None:
    
    from utilities import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

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
        return  ([o for o in self.my_trades if o['api'] == True])
    
    def my_trades_manual (self) -> list:
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == False]
    
    def my_trades_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_trades_api () == [] else   ([o for o in self.my_trades_api () if  label in o['label'] ])
    
    def my_trades_api_net_position(self, 
                                   selected_trades: list
                                   ) -> float:
        
        '''
        '''    

        try:
            if selected_trades != []:
            # sum sell
                #selected_trades = set (selected_trades)
                sum_closed_trades_in_my_trades_open_sell = ([o['amount'] for o in selected_trades \
                    if o['direction']=='sell'])
                
                sum_closed_trades_in_my_trades_open_sell = 0 \
                    if sum_closed_trades_in_my_trades_open_sell == [] \
                        else sum(sum_closed_trades_in_my_trades_open_sell)
                # sum buy
                sum_closed_trades_in_my_trades_open_buy = ([o['amount'] for o in selected_trades \
                    if o['direction']=='buy'])
                
                sum_closed_trades_in_my_trades_open_buy = 0 \
                    if sum_closed_trades_in_my_trades_open_buy == [] \
                        else sum(sum_closed_trades_in_my_trades_open_buy)
                    
            return selected_trades if selected_trades == [] \
                else  sum_closed_trades_in_my_trades_open_buy - sum_closed_trades_in_my_trades_open_sell
        
        except Exception as error:
            catch_error(error)
            
    def recognize_trade_transactions (self, trade_order) -> dict:
        
        '''
        '''       
        from utilities import string_modification
        
        #log.info (f'DATA FROM EXC LOOP {trade_order=}')

        try:
            
            
            try:
                label_id = trade_order [0]['label']
                trade_seq = trade_order [0]['trade_seq']
                order_type = trade_order [0]['order_type']
                closed_label_id_int = string_modification.extract_integers_from_text(label_id)
                
            except:
                label_id = []
                trade_seq = []
                order_type = []
                closed_label_id_int = []
            
            # for data with label id/ordered through API    
            if label_id != []:
                pass  
            
            liquidation_event = 'liquidation' in order_type
            if liquidation_event:
                info= (f'LIQUIDATION {trade_order} \n ')
                log.error (info)
                telegram_bot_sendtext(info) 
            
        except Exception as error:
            catch_error (error)

        
        return {'liquidation_event': liquidation_event,
                'label_id': label_id,
                'closed_label_id_int': closed_label_id_int,
                'opening_position': 'open' in label_id,
                'closing_position': 'closed' in label_id}
        
    def gather_transactions_under_the_same_id_int (self, 
                                                   closed_label_id_int: str, 
                                                   my_trades_open: list
                                                   ) -> dict:
        
        '''
        my_trades_open = re-read from db after previous closed transaction appended
        '''       
        
        # filter open trades which have the same label id with trade transaction
        label = str(closed_label_id_int)
        transactions_same_id = [o for o in my_trades_open if label in o['label'] ]
        
        remaining_open_trades = [o for o in my_trades_open if  label not in o['label']  ]
        
        #! DELETE ###########################################################################################
                                                
        #log.info (my_trades_open)
        log.critical (f' closed_label_id_int {label} transactions_same_id {transactions_same_id} \
            transactions_same_id_net_qty {self.my_trades_api_net_position (transactions_same_id)}')\
                #remaining_open_trades {string_modification.remove_redundant_elements (remaining_open_trades)}')
        #! DELETE ###########################################################################################
        
        return {'transactions_same_id':transactions_same_id,
                # summing transaction under the same label id
                'transactions_same_id_net_qty': self.my_trades_api_net_position (transactions_same_id),
                'remaining_open_trades': string_modification.remove_redundant_elements (remaining_open_trades)
                }
        
    def synchronizing_closed_tradings (self, 
                                       closed_label_id_int: str, 
                                       my_trades_open: list, 
                                       my_trades_path_open: str
                                       ) -> None:
        
        '''
        '''  
             
        gather_transactions_under_the_same_id_int = self.gather_transactions_under_the_same_id_int (closed_label_id_int, 
                                                                                                    my_trades_open
                                                                                                    )
        
        # filter open trades which have the same label id with trade transaction
        closed_trades_in_my_trades_open = gather_transactions_under_the_same_id_int ['transactions_same_id']

        log.debug (f'{closed_label_id_int} \n ')
        if closed_label_id_int == 1674134456 :
            log.critical (f' CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')
            #log.info (my_trades_open)
        
        # sum transaction with the same label id
        sum_closed_trades_in_my_trades_open_net = gather_transactions_under_the_same_id_int ['transactions_same_id_net_qty']
        #log.debug (f'closed_label_id_int {closed_label_id_int}')
        #log.critical (f'closed_trades_in_my_trades_open {closed_trades_in_my_trades_open}')
        #log.critical (f'sum_closed_trades_in_my_trades_open_net {sum_closed_trades_in_my_trades_open_net}')
        
        remaining_open_trades =  gather_transactions_under_the_same_id_int ['remaining_open_trades']  

        #! SYNCHRONIZATION (DIFF SYSTEM VS DB)
        #my_trades = self.my_trades
        
        #log. info ( ( self.my_trades))
        #log. debug ( (my_trades_open))
        #log. critical ( (string_modification.find_unique_elements (
        #            my_trades_open,  
        #                self.my_trades
        #                )))
        log. critical ((sum_closed_trades_in_my_trades_open_net))
        
        if len (my_trades_open) > 1:
            #log.error (str(closed_label_id_int))
                                
            label = 'label' # https://www.appsloveworld.com/coding/python3x/291/how-to-handle-missing-keys-in-list-of-json-objects-in-python
            for key in my_trades_open:
                if label not in key:
                    key [label] = []
            
            # the transaction did not make the respective label to be closed
            if sum_closed_trades_in_my_trades_open_net != 0:
                for data_order in closed_trades_in_my_trades_open:
                        
                    pickling.append_data (my_trades_path_open, 
                                          data_order , 
                                          True
                                          )
                    
            # the transaction closed the respective label
            if sum_closed_trades_in_my_trades_open_net == 0: 
                
                for data_order in remaining_open_trades:
                                    
                    try:
                        label_id= data_order [0]['label']
                    except:
                        label_id= []
                    
                    # for data with label id/ordered through API    
                    if label_id != []:
                        log.critical (data_order)   
                    
                        pickling.replace_data (my_trades_path_open, 
                                               remaining_open_trades, 
                                               True
                                               )
                
        # transaction has fully completed. move all the transactions with the same id to closed db
        if sum_closed_trades_in_my_trades_open_net == 0:
            
            #! SEPARATE OPEN AND CLOSED TRANSACTIONS IN OPEN DB
            # update mytrades db with the still open ones
            pickling.replace_data (my_trades_path_open, 
                                   remaining_open_trades, 
                                   True 
                                   )
                            

    def distribute_trade_transaction (self, 
                                      currency: str
                                      ) -> None:
        
        '''
        '''       
        #from time import sleep
        
        try:
        
            my_trades_path_open = system_tools.provide_path_for_file ('myTrades', 
                                                                      currency, 
                                                                      'open'
                                                                      )

            log.error (self.my_trades) 
            log.critical (len((self.my_trades) ))
            numb = 0
            for data_order in self.my_trades:
                lbl = data_order['label']
                data_order = [data_order]
                numb = numb + len(data_order[0])
                log.warning (f'{numb}  {lbl} ')
                log.info (data_order)
                #sleep (5)

                trade_transactions = self.recognize_trade_transactions (data_order)
                
                #determine label id. 
                label_id = trade_transactions['label_id']
                
                #! DISTRIBUTE trading transaction as per label id
                # for no label id trading (usually manual trade)
                if label_id == [] :
                    my_trades_path_manual = system_tools.provide_path_for_file ('myTrades', 
                                                                                currency,
                                                                                'manual'
                                                                                )
                    
                    pickling.append_data (my_trades_path_manual, 
                                          data_order, 
                                          True
                                          )                
                        
                if trade_transactions['liquidation_event']:

                    # append trade to db.check potential duplicate
                    pickling.append_data (my_trades_path_open, 
                                          data_order,
                                          True
                                          )
                    
                if trade_transactions['opening_position']:
                    #log.error ('LABEL ID OPEN')
                    #log.error (data_order)

                    # append trade to db.check potential duplicate
                    pickling.append_data (my_trades_path_open, 
                                          data_order, 
                                          True
                                          )
                    
                if trade_transactions['closing_position']:
                    log.debug ('LABEL ID CLOSED')
                    log.error (data_order)
                    
                    # append trade to db.check potential duplicate
                    pickling.append_data (my_trades_path_open, 
                                          data_order,
                                          True
                                          )
                                
                    # fetch previous open trading data from local db
                    my_trades_open = pickling.read_data(my_trades_path_open)
                    log.critical ('source for distribute_trade_transaction')
                    #log.warning (my_trades_open)
                    log.critical (len(my_trades_open))
                    
                    self. synchronizing_closed_tradings(trade_transactions['closed_label_id_int'], 
                                                        my_trades_open, 
                                                        my_trades_path_open
                                                        )
                                                            
        except Exception as error:
            catch_error(error)
            
    def my_trades_max_price_attributes_filteredBy_label (self, trade_sources_filtering: list) -> dict:
        
        '''
        trade_sources: 'API'
        '''       
        my_trades = []
        
        try:
                
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
                    'timestamp':  ([o['timestamp'] for o in trade_list_with_max_price])[0],
                    'order_id':  ([o['order_id'] for o in trade_list_with_max_price])[0],
                    'instrument':  ([o['instrument_name'] for o in trade_list_with_max_price])[0],
                    'size':  ([o['amount'] for o in trade_list_with_max_price])[0],
                    'label':  ([o['label'] for o in trade_list_with_max_price])[0],
                
                }
            if my_trades ==[]:
                return []
            
        except Exception as error:
            catch_error(error)