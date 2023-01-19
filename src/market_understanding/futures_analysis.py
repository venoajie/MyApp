# -*- coding: utf-8 -*-
from utilities import pickling, system_tools

def combining_futures_analysis (index_price: float, 
                                list_instruments:list,
                                server_time) -> dict:

    '''
    '''   
    
    futures =[]
    
    for future in list_instruments:
        #print (future)
        instrument = future ['instrument_name']
        print (instrument)
        my_path_ticker: str = system_tools.provide_path_for_file ('ticker', instrument) 
        ticker =  pickling.read_data(my_path_ticker)
        print (ticker)
        mark_price = ticker ['mark_price']
        print (mark_price)
        #print (future)
        #print (index_price)
        
        # obtain funding next rate based on individual coin
        margin: float  = mark_price - index_price  
        margin_pct: float  =  margin / index_price
        instruments_with_rebates: float = future ['maker_commission'] < 0
        
        future: int = future ['expiration_timestamp']
        remaining_active_time: int = future - server_time 
        remaining_active_time_hours: float = (remaining_active_time/(60000))/60

        # combining current and next coins rate
        dicttemp = {}                
        dicttemp = {'margin_usd': margin,
                    'mark_price': mark_price,
                    'margin_pct': margin_pct,
                    'with_rebates': instruments_with_rebates,
                    'remaining_active_time_in_hours': remaining_active_time_hours,
                    'expectation': 'contango' if margin > 0 else ('backwardation ' if margin < 0 else 'neutral')}                    
        
        data_future = futures.append(dicttemp.copy())        
                
    return [futures]