#!/usr/bin/env python

def labelling (order: str, strategy: str, id_strategy: int = None):
    
    """
    labelling based on  strategy and unix time at order is made
    """
    from utils import time_modification
    
    now_utc = time_modification.convert_time_to_utc () ['utc_now']
    now_unix = time_modification.convert_time_to_unix (now_utc)
    
    id_unix_time = now_unix if id_strategy == None else id_strategy
        
    return (f'{strategy}-{order}-{id_unix_time}') if id_strategy == None else  (f'{id_strategy}')
