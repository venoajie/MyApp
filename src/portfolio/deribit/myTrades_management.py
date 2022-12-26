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
                'order_id':  ([o['order_id'] for o in trade_list_with_max_price])[0] ,
                'instrument':  ([o['instrument_name'] for o in trade_list_with_max_price])[0] ,
                'size':  ([o['amount'] for o in trade_list_with_max_price])[0] ,
                'label':  ([o['label'] for o in trade_list_with_max_price])[0] ,
            
            }
        if my_trades ==[]:
            return []