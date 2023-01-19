# -*- coding: utf-8 -*-
from utilities import time_modification

def combining_individual_futures_analysis (index_price: float, 
                                future: dict,
                                ticker) -> dict:

    '''
    '''   
    
    futures =[]
    try:

        instrument = ticker ['instrument_name']
        
        mark_price = ticker ['mark_price']
        now_time = time_modification.convert_time_to_utc()['utc_now']
        now_time_unix = time_modification.convert_time_to_unix (now_time) 
        
        # obtain funding next rate based on individual coin
        margin: float  = mark_price - index_price  
        margin_pct: float  =  margin / index_price
        instruments_with_rebates: float = future ['maker_commission'] < 0
        
        future: int = future ['expiration_timestamp']
        remaining_active_time: int = future - now_time_unix 
        remaining_active_time_hours: float = (remaining_active_time/(60000))/60
        delta_price: float = (mark_price - index_price)
        ratio_price_to_index: float = delta_price / index_price

        # combining current and next coins rate
        dicttemp = {}                
        dicttemp = {'instrument_name': instrument,
                    'mark_price': mark_price,
                    'with_rebates': instruments_with_rebates,
                    'margin_usd': margin,
                    'ratio_price_to_index':  ratio_price_to_index,
                    'margin_pct': margin_pct,
                    'remaining_active_time_in_hours': remaining_active_time_hours,
                    'market_expectation': 'contango' if margin > 0 else ('backwardation' if margin < 0 else 'neutral')}                    
        
        data_future = futures.append(dicttemp.copy())        
                    
    except Exception as error:

        print (error)
        
    return futures
