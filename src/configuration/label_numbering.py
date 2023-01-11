#!/usr/bin/env python

def get_now_unix_time ()->int: 
    
    """
    """
    from utilities import time_modification
    now_utc = time_modification.convert_time_to_utc () ['utc_now']        
    return int(time_modification.convert_time_to_unix (now_utc)/1000)

def labelling (order: str, 
               strategy: str, 
               id_strategy: int = None
               )-> str:
    
    """
    labelling based on  strategy and unix time at order is made
    """
        
    id_unix_time = get_now_unix_time () if id_strategy == None else id_strategy
        
    return (f'{strategy}-{order}-{id_unix_time}') if id_strategy == None else  (f'{id_strategy}')
