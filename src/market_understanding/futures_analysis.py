# -*- coding: utf-8 -*-
from utilities import pickling, system_tools, time_modification

def combining_individual_futures_analysis (index_price: float, 
                                future: dict,
                                ticker) -> dict:

    '''
    '''   
    
    futures =[]

    instrument = future ['instrument_name']
    
    ticker =  ticker [0]
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

    # combining current and next coins rate
    dicttemp = {}                
    dicttemp = {'instrument_name': instrument,
                'mark_price': mark_price,
                'with_rebates': instruments_with_rebates,
                'margin_usd': margin,
                'margin_pct': margin_pct,
                'remaining_active_time_in_hours': remaining_active_time_hours,
                'market_expectation': 'contango' if margin > 0 else ('backwardation' if margin < 0 else 'neutral')}                    
    
    data_future = futures.append(dicttemp.copy())        
                
    return futures

def combining_futures_analysis (index_price: float, 
                                list_instruments:list,
                                server_time) -> dict:

    '''
    '''   
    
    futures =[]
    
    now_time = time_modification.convert_time_to_utc()['utc_now']
    now_time_unix = time_modification.convert_time_to_unix (now_time) 
    print (server_time)
    print (now_time_unix)
    for future in list_instruments:

        instrument = future ['instrument_name']
        my_path_ticker: str = system_tools.provide_path_for_file ('ticker', instrument) 
        ticker =  pickling.read_data(my_path_ticker)
        ticker =  ticker [0]
        mark_price = ticker ['mark_price']
        
        # obtain funding next rate based on individual coin
        margin: float  = mark_price - index_price  
        margin_pct: float  =  margin / index_price
        instruments_with_rebates: float = future ['maker_commission'] < 0
        
        future: int = future ['expiration_timestamp']
        remaining_active_time: int = future - server_time 
        remaining_active_time_hours: float = (remaining_active_time/(60000))/60

        # combining current and next coins rate
        dicttemp = {}                
        dicttemp = {'instrument_name': instrument,
                    'mark_price': mark_price,
                    'with_rebates': instruments_with_rebates,
                    'margin_usd': margin,
                    'margin_pct': margin_pct,
                    'remaining_active_time_in_hours': remaining_active_time_hours,
                    'market_expectation': 'contango' if margin > 0 else ('backwardation' if margin < 0 else 'neutral')}                    
        
        data_future = futures.append(dicttemp.copy())        
                
    return futures