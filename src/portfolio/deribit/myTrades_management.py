# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass

def telegram_bot_sendtext(bot_message, purpose: str = 'general_error') -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

@dataclass(unsafe_hash=True, slots=True)
class MyTrades ():

    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up my trades data
    '''       
    my_trades: list
            
    def my_trades_api (self):
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == True]
    
    def my_trades_manual (self):
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == False]
    
    
    
    def my_trades_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        return [] if self.my_trades_api () == [] else  ([o for o in self.my_trades_api () if  label in o['label'] ])
    
    def distribute_trade_transaction (self, currency) -> dict:
        
        '''
        trade_sources: 'API'
        '''       
        from utils import string_modification, pickling, system_tools
        from loguru import logger as log

        my_trades_path_open = system_tools.provide_path_for_file ('myTrades', currency, 'open')
        my_trades_path_closed = system_tools.provide_path_for_file ('myTrades', currency, 'closed')

        for data_order in self.my_trades:
            data_order = [data_order]
            log.info (f'DATA FROM EXC LOOP {data_order=}')
            
            #determine label id
            try:
                label_id= data_order [0]['label']
            except:
                label_id= []
            
            # for data with label id/ordered through API    
            if label_id != []:
                pass

            closed_label_id_int = string_modification.extract_integers_from_text(label_id)
            log.info (f' {label_id=}   {closed_label_id_int} \n ')

            #!
            sum_new_trading = [o['amount'] for o in data_order  ][0]
            sum_open_trading_after_new_trading = 0
            #!

            if 'open' in label_id:
                log.error ('LABEL ID OPEN')

                pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_order , 10000, True)
                pickling.check_duplicate_elements (my_trades_path_open)

                #!
                my_trades_open = pickling.read_data(my_trades_path_open)
                label_my_trades_open = [o['label'] for o in my_trades_open  ]
                amount_my_trades_open = [o['amount'] for o in my_trades_open  ]
                sum_open_trading_after_new_trading = sum([o['amount'] for o in my_trades_open  ])
                log.error (f'DATA OPEN TRADE AFTER APPEND {sum_open_trading_after_new_trading}  {sum_open_trading_after_new_trading} {amount_my_trades_open=}')
                #!
                
            if 'closed' in label_id:
                log.debug ('LABEL ID CLOSED')
                my_trades_open = pickling.read_data(my_trades_path_open)  
                                                
                #update mytrades db with the closed ones
                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, data_order , 10000, True)
                pickling.check_duplicate_elements (my_trades_path_closed)
                
                closed_trades_in_my_trades_open = ([o for o in my_trades_open if  str(closed_label_id_int)  in o['label'] ])
                log.debug (f'{closed_trades_in_my_trades_open=}')
                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, closed_trades_in_my_trades_open , 10000, True)
                pickling.check_duplicate_elements (my_trades_path_closed)

                
                # SEPARATE OPEN AND CLOSED TRANSACTIONS IN OPEN DB
                #update mytrades db with the still open ones
                #my_trades_open = pickling.read_data(my_trades_path_open)  
                remaining_open_trades = ([o for o in my_trades_open if  str(closed_label_id_int)  not in o['label'] ])
                
                #log.critical (f'REMAINING OPEN TRADES {remaining_open_trades=}')
                pickling.replace_data (my_trades_path_open, remaining_open_trades, True )
                pickling.check_duplicate_elements (my_trades_path_open)
                    
                #!
                my_trades_open = pickling.read_data(my_trades_path_open)
                label_my_trades_open = [o ['label']  for o in my_trades_open  ]
                amount_my_trades_open = [o ['amount']  for o in my_trades_open  ]
                sum_my_trades_open = sum([o['amount'] for o in my_trades_open  ])
                log.warning (f'DATA REMAINING OPEN TRADE AFTER REPLACE CLOSED TRADES {sum_my_trades_open} {amount_my_trades_open} {label_my_trades_open=}')
                    
                #!
                my_trades_closed = pickling.read_data(my_trades_path_closed)
                if my_trades_closed !=[]:
                    log.warning (my_trades_closed)
                    label_my_trades_closed = [o ['label']  for o in my_trades_closed  ]
                    sum_my_trades_open = sum([o['amount'] for o in my_trades_closed  ])
                    log.warning (f'DATA CLOSED TRADE FINAL {sum_my_trades_open} {label_my_trades_closed=}')
                    
            if label_id == [] :
                my_trades_path_manual = system_tools.provide_path_for_file ('myTrades', currency, 'manual')
                log.error ('[]')
                pickling.append_and_replace_items_based_on_qty (my_trades_path_manual, data_order, 10000, True)                                    
            
            #!
            my_trades_open = pickling.read_data(my_trades_path_open)
            #log.debug (f'AFTER 2 {my_trades_open=}')
            sum_open_trading_after_new_closed_trading = sum([o['amount'] for o in my_trades_open  ])
            
            info= (f'CHECK TRADING SUM {label_id=} sum_new_trading: {sum_new_trading} sum_open_trading_after_new_trading: {sum_open_trading_after_new_trading} final_sum_open: {sum_open_trading_after_new_closed_trading} \n ')
            
            log.critical (info)
            telegram_bot_sendtext(info)
            #!