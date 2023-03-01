# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log
from utilities import pickling, system_tools, string_modification as str_mod

def catch_error (error, idle: int = None) -> list:
    """
    """
    from utilities import system_tools
    system_tools.catch_error_message(error, idle)

async def telegram_bot_sendtext (bot_message, 
                                 purpose: str = 'general_error'
                                 ) -> None:
    
    import deribit_get 
    
    result = await deribit_get.telegram_bot_sendtext (bot_message,
                                 purpose
                                 )
    
    return result

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
    
    def my_trades_api_basedOn_label (
                                     self, 
                                     label: str
                                     )-> list:
        
        '''
        '''    
        return [] if self.my_trades_api () == [] \
            else [o for o in self.my_trades_api () if  label in o['label'] ]
    
    def my_trades_api_net_position(self, 
                                   selected_trades: list
                                   ) -> float:
        
        '''
        '''    

        try:
            if selected_trades != []:
                # sum sell
                sum_sell = ([o['amount'] for o in selected_trades \
                    if o['direction']=='sell'])
                
                sum_sell = 0 if sum_sell == [] \
                        else sum (
                            sum_sell
                            )
                # sum buy
                sum_buy = [
                    o['amount'] for o in selected_trades if o['direction'] == 'buy'
                    ]
                
                sum_buy = 0  if sum_buy == [] \
                        else sum(sum_buy)
                    
            return selected_trades if selected_trades == [] \
                else  sum_buy - sum_sell
        
        except Exception as error:
            catch_error(error)
            
    def recognize_trade_transactions (self, 
                                      trade_order: list
                                      ) -> dict:
        
        '''
        '''       
        
        
        #log.critical (f'DATA FROM EXC LOOP {trade_order=}')

        try:            
            
            try:
                label_id = trade_order [0]['label']
                trade_seq = trade_order [0]['trade_seq']
                order_type = trade_order [0]['order_type']
                closed_label_id_int = str_mod.extract_integers_from_text(label_id)
                
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
                #await telegram_bot_sendtext(info) 
            
        except Exception as error:
            catch_error (error)

        return {
                'liquidation_event': liquidation_event,
                'label_id': label_id,
                'closed_label_id_int': closed_label_id_int,
                'opening_position': 'open' in label_id,
                'closing_position': 'closed' in label_id
                }
        
    def gather_transactions_under_the_same_id_int (self, 
                                                   label: str, 
                                                   my_trades_open: list
                                                   ) -> dict:
        
        '''
        my_trades_open = re-read from db after previous closed transaction was appended
        '''       
        
        transactions_under_same_id = self.transactions_same_id (label,
                                                          my_trades_open
                                                          )
        
        remaining_open_trades = self.remaining_open_trades (label,
                                                          my_trades_open
                                                          )
        
        return {'transactions_same_id':transactions_under_same_id['transactions_same_id'],
                # summing transaction under the same label id
                'transactions_same_id_contain_open_label': transactions_under_same_id['transactions_same_id_contain_open_label'],
                'transactions_same_id_net_qty': self.my_trades_api_net_position (transactions_under_same_id['transactions_same_id']),
                'transactions_same_id_len': len (transactions_under_same_id['transactions_same_id']),
                'remaining_open_trades': str_mod.remove_redundant_elements (remaining_open_trades)
                }
        
    def transactions_same_id (self,
                              label: str,
                              my_trades_open: list
                                      ) -> None:
        
        '''
        '''       
        transactions_under_same_id = [o for o in my_trades_open \
            if (label) == str_mod.extract_integers_from_text (o['label']) ]
        return {'transactions_same_id': transactions_under_same_id,
                'transactions_same_id_contain_open_label': False if transactions_under_same_id == [] \
                    else 'open' in [o['label'] for o in transactions_under_same_id][0],
                }
    
    
    def extracting_unique_label_id (self,
                                    my_trades_open: list
                                      ) -> None:
        
        '''
        '''       

        return str_mod.remove_redundant_elements (
            [
                str_mod.extract_integers_from_text (
                        o['label']
                        ) for o in my_trades_open if 'closed' in o['label']
             ]
                    )
        
    def remaining_open_trades (self,
                              label: str,
                              my_trades_open: list
                                      ) -> None:
        
        '''
        '''       
        #
        return [o for o in my_trades_open if (label) != str_mod.extract_integers_from_text (o['label']) ]
            
    def closed_open_order_label_in_my_trades_open (self,
                                                   my_trades_open: list,
                                                   label: str
                                                   ) -> None:
        
        '''
        '''       
        #
        
        if my_trades_open == None:
            my_trades_open = self.my_trades_open
            
        label_trades = (
            [
                str_mod.extract_integers_from_text (
                        o['label']
                        ) for o in my_trades_open 
             ]
                    )
        log.info (label_trades)
        return label in label_trades 
    
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
        
        # sum transaction with the same label id
        sum_closed_trades_in_my_trades_open_net = gather_transactions_under_the_same_id_int ['transactions_same_id_net_qty']
        
        log.critical (f'sum_closed_trades_in_my_trades_open_net {sum_closed_trades_in_my_trades_open_net}')
        
        remaining_open_trades =  gather_transactions_under_the_same_id_int ['remaining_open_trades']  

        #! SYNCHRONIZATION (DIFF SYSTEM VS DB)
        
        log. critical ( (gather_transactions_under_the_same_id_int ['transactions_same_id_contain_open_label'] ))
        if gather_transactions_under_the_same_id_int ['transactions_same_id_contain_open_label']:       
            
            if len (my_trades_open) > 1:
                                    
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
        
         # orphan closed orders:                    
        else:
            log. critical (remaining_open_trades)
            log. critical (self.my_trades_api_net_position (remaining_open_trades))
            

            pickling.replace_data (my_trades_path_open, 
                                    remaining_open_trades, 
                                    True 
                                    )          

    def distribute_trade_transactions (self, 
                                      currency: str,
                                      rebuilt: bool = False
                                      ) -> None:
        
        '''
        rebuilt: False = population consist of ALL NEW trade transactions
        rebulit: True = population consist of EXISTING trade transactions represente by/
            ONLY label numbers in all transactions 
                (same label numbers will be consider as one transactions) --> to avoid 
                    double counting on transactions loop
        '''       
        
        try:
        
            my_trades_path_open = system_tools.provide_path_for_file ('myTrades', 
                                                                      currency, 
                                                                      'open'
                                                                      )
            numb = 0
            my_trades = self.my_trades
            if rebuilt == True:
                for data_order in my_trades:
                    
                    pickling.append_data (
                        my_trades_path_open, 
                        data_order, 
                        True
                        ) 
                    
                my_trades_open = pickling.read_data(my_trades_path_open)
                
                #log.warning (my_trades_open)
                
                my_trades_closed_label = self.extracting_unique_label_id (
                    my_trades_open
                    )
                
                log.warning (my_trades_closed_label)
                for id in my_trades_closed_label:
                    log.warning (id)
                    self. synchronizing_closed_tradings(id, 
                                                        my_trades_open, 
                                                        my_trades_path_open
                                                        )
            
            for data_order in my_trades:

                data_order = [data_order]
                numb = numb + len(data_order)

                log.info (data_order)

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
                    log.error ('LABEL ID OPEN')
                    #log.error (data_order)

                    # append trade to db.check potential duplicate
                    pickling.append_data (my_trades_path_open, 
                                          data_order, 
                                          True
                                          )
                    
                if trade_transactions['closing_position']:
                    log.debug ('LABEL ID CLOSED')
                    #log.error (data_order)
                    
                    # append trade to db.check potential duplicate
                    pickling.append_data (my_trades_path_open, 
                                          data_order,
                                          True
                                          )
                                
                    # fetch previous open trading data from local db
                    my_trades_open = pickling.read_data(my_trades_path_open)
                    
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