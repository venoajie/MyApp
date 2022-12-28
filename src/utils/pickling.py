# -*- coding: utf-8 -*-

# built ins
import pickle
import os

def append_data (file_name_pkl: str, data: dict)-> None:

    """
    https://stackoverflow.com/questions/28077573/python-appending-to-a-pickled-list
    """

    collected_data: list = []
    if os.path.exists(file_name_pkl):

        with open(file_name_pkl,'rb') as handle: 
            collected_data = pickle.load(handle)

    collected_data.append(data)

    # Now we "sync" our database
    with open(file_name_pkl,'wb') as handle:
        pickle.dump(collected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Re-load our database

    #print(f'{data=}')
    #print(f'{collected_data=}')
    with open(file_name_pkl,'rb') as handle:
        collected_data = pickle.load(handle)
    return collected_data

def read_data (file_name_pkl: str)-> None:

    """
    """

    try:
        with open(file_name_pkl,'rb') as handle:
            read_pickle = pickle.load(handle)
            return read_pickle
    except:
        return []


def dump_data_as_list (file_name: str, data: dict)-> None:

    """
    """

    with open(file_name,'wb') as handle:
            
        if isinstance(data, dict):
            pickle.dump([data], handle, protocol=pickle.HIGHEST_PROTOCOL)
        if isinstance(data, list):
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
def replace_data (file_name: str, data: dict)-> None:

    """
    """
    read_data (file_name)

    with open(file_name,'wb') as handle:
        print (f'{isinstance(data, dict)=}')
        print (f'{isinstance(data, list)=}')
        
            
        if isinstance(data, dict):
            pickle.dump([data], handle, protocol=pickle.HIGHEST_PROTOCOL)
        if isinstance(data, list):
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
def append_and_replace_items_based_on_qty (file_name_pkl: str, data: dict, max_qty: int)-> None:

    """
    append_and_replace_items_based_on_qty (file_name, resp, 3)
    """
    
    from loguru import logger as log
    #file_name_pkl:str =f"""{file_name}.pkl"""

    append_data(file_name_pkl, data)
    data: object = read_data (file_name_pkl)
    data_list = list (data [0])
    
    if 'change_id' in data_list:
        sorted_data: list = sorted([o['timestamp']  for o in data ])
        len_tick_data_ordBook: int = len (sorted_data)  

        if len_tick_data_ordBook > max_qty:
        
            filtered_timestamps =  (sorted_data) [max_qty:]

            result: list = [o for o in data if o['timestamp'] not in filtered_timestamps ]
            
            dump_data_as_list (file_name_pkl, result)
            
            #with open(file_name_pkl,'wb') as handle:
            #    pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
    if 'params' in data_list:

        data = [o['params']  for o in data ]

        data = [o['data']  for o in data ]

        sorted_data: list = sorted([o['tick']  for o in data ])
        len_tick_data_ohlc: int = len ([o['tick']  for o in sorted_data ])  
        
        if len_tick_data_ohlc > max_qty:
            filtered_timestamps =  (sorted_data) [max_qty:]

            result: list = [o for o in data if o['tick'] not in filtered_timestamps ]

            dump_data_as_list (file_name_pkl, result)
            
def append_and_replace_items_based_on_time_expiration (file_name_pkl: str, data: dict, time_expiration: int)-> None:

    """
    append_and_replace_items_based_on_time_expiration in minute
    """
    from utils import time_modification

    append_data(file_name_pkl, data)
    data: object = read_data (file_name_pkl)
    data_list = list (data [0])
    now_time_utc = time_modification.convert_time_to_utc()['utc_now']
    now_time_utc_in_unix = time_modification. convert_time_to_unix (now_time_utc)

    one_hour_ago = now_time_utc_in_unix - time_expiration
    
    if 'change_id' in data_list:
        result: list =  ([o for o in data if  o['timestamp'] > one_hour_ago]) 
        dump_data_as_list (file_name_pkl, result)
                
    if 'params' in data_list:

        data = [o['params']  for o in data ]

        data = [o['data']  for o in data ]
        
        result: list =  ([o for o in data if  o['tick'] < one_hour_ago])    
        dump_data_as_list (file_name_pkl, result)
