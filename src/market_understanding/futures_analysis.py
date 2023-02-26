# -*- coding: utf-8 -*-

from utilities import time_modification

def get_now_unix_time ()-> int:
    
    '''
    Get the current time in UNIX format.
    
    Args:
        None
        
    Returns:
        int: current time in UNIX.

    '''
    now_utc = time_modification.convert_time_to_utc () ['utc_now']
    return int(time_modification.convert_time_to_unix (now_utc))

def compute_remaining_active_hours_before_expiration (future_expiration: int)-> float: 
    
    '''
    Compute the remaining active hours before expiration.
    
    Args:
        future_expiration (int): The future expiration time in unix-ms.
        
    Returns:
        float: The remaining active hours before expiration.
    '''
    return time_modification.time_delta_between_two_times ('unix-ms', 
                                                           get_now_unix_time(),
                                                           future_expiration
                                                           )['hours']
        
def get_futures_market_expectation (margin: float)-> str:
    
    '''
    Returns the market expectation based on the margin
    between the spot price and the futures price.

    Args:
        margin (float): The difference between the spot price and the futures price.
        
    Returns:
        str: contango/backwardation/neutral
    '''
    return  'contango' if margin > 0 else (
        'backwardation' if margin < 0 else 'neutral'
        )

def is_fee_rebated (fee: float)-> bool:
    
    '''
    Checks if the fee is rebated or not based on 
    ticker fee/comission information
    
    Args:
        fee (float): Fee provided from instrument tickers.
        
    Returns:
        bool: True if fee < 0 (trading fee will be rebated and considered as income).
    '''
    return fee < 0

def get_margin_and_ratio (mark_price: float, 
                          index_price: float
                          )-> dict: 
    
    '''
    '''
    margin = mark_price - index_price
    
    return  {
        'margin':  margin,
        'ratio_price_to_index': margin / index_price
        }

def combining_individual_futures_analysis (index_price: float, 
                                           future: dict,
                                           ticker: dict) -> dict:

    '''
    '''   
    
    futures =[]

    try:

        mark_price = ticker ['mark_price']

        expiration_time: int = future ['expiration_timestamp']

        margin_and_ratio = get_margin_and_ratio(mark_price, 
                                                index_price
                                                )
                
        # combining current and next coins rate
        dicttemp = {}                
        dicttemp = {'instrument_name': ticker ['instrument_name'],
                    'with_rebates': is_fee_rebated (future ['maker_commission']),
                    'market_expectation': get_futures_market_expectation(margin_and_ratio['margin']),
                    'mark_price': mark_price,
                    'margin_usd': margin_and_ratio['margin'],
                    'ratio_price_to_index': margin_and_ratio ['ratio_price_to_index'],
                    'remaining_active_time_in_hours': round(compute_remaining_active_hours_before_expiration (expiration_time
                                                                                                              ),
                                                            2
                                                            )
                    }                    
        
        data_future = futures.append(dicttemp.copy())        
                    
    except Exception as error:

        print (error)
        
    return futures
