# -*- coding: utf-8 -*-

# built ins
import pickle
import os


def read_data (file_name_pkl: str)-> None:

    """
    """

    try:
        if os.path.exists(file_name_pkl):
            with open(file_name_pkl,'rb') as handle:
                read_pickle = pickle.load(handle)
                return read_pickle
    except:
        return []
    
def check_duplicate_elements (file_name: str)-> None:

    from utils import string_modification
    from loguru import logger as log

    data_from_db: list = read_data (file_name)
   #! 
   
    if 'myTrades' in str(file_name):
        log.info (f'{file_name=}')
        sum_db = sum([o['amount'] for o in data_from_db  ])
        log.info (f'BEFORE {len(data_from_db)} {sum_db} {data_from_db=}')
    #!
    free_from_duplicates_data = string_modification.remove_redundant_elements (data_from_db)
    
    dump_data_as_list (file_name, free_from_duplicates_data)
#! 
    if 'myTrades' in str(file_name):
        data_from_db: list = read_data (file_name)
        sum_db = sum([o['amount'] for o in data_from_db  ])    
        log.warning (f'AFTER {len(data_from_db)}  {sum_db} {data_from_db=}')

def dump_data_as_list (file_name: str, data: dict, check_duplicates: bool = False)-> None:

    """
    """    

    with open(file_name,'wb') as handle:
        try:
            
            if data !=[]:
                
                if isinstance(data, dict):
                    pickle.dump([data], handle, protocol=pickle.HIGHEST_PROTOCOL)
                    
                if isinstance(data, list):
                    free_from_none_data = ( [o for o in data if isinstance(o, dict)] )

                    pickle.dump(free_from_none_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
            if data == []:
                data_from_db: list = read_data (file_name)
                
                # to avoid record [] in db with valid contents
                if data_from_db:
                    pass
                
                if data_from_db ==[]:
                    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
        except Exception as error:
            print (f'pickling {error}')    

    if check_duplicates == True:
        check_duplicate_elements (file_name)

            
def append_data (file_name_pkl: str, data: dict)-> None:

    """
    https://stackoverflow.com/questions/28077573/python-appending-to-a-pickled-list
    """
    
    data_from_db = []
    #print (f"append_data data fr exc {data}")

    #collected_data: list = []
    if os.path.exists(file_name_pkl):
        data_from_db = read_data (file_name_pkl)

    if isinstance(data, list) and data !=[]:
        data = data [0]
            
    if data_from_db != []:
        data_from_db.append(data)

    combined_data = [data] if data_from_db == [] else data_from_db
    
    # Now we "sync" our database
    dump_data_as_list (file_name_pkl, combined_data)
    
            
def replace_data (file_name: str, data: dict, check_duplicates: bool = False)-> None:

    """
    """

    read = read_data (file_name)

    if read == []:
        pass
    
    dump_data_as_list (file_name, data, check_duplicates)
    
def append_and_replace_items_based_on_qty (file_name_pkl: str, data: dict, max_qty: int, check_duplicates: bool = False)-> None:

    """
    append_and_replace_items_based_on_qty (file_name, resp, 3)
    """

   # print (f"data fr exc {data}")
    
    append_data(file_name_pkl, data)
    data_from_db: list = read_data (file_name_pkl)


    if isinstance(data_from_db, dict):
        data_list = list (data_from_db)
        
    if isinstance(data_from_db, list):
        data_list = list (data_from_db [0])
                    
    #print (f"append_and_replace_items_based_on_qty {data_from_db}")
    #data_list = list (data [0])
    
    if 'change_id' in data_list:
        sorted_data: list = sorted([o['timestamp']  for o in data_from_db ])
        len_tick_data_ordBook: int = len (sorted_data)  

        if len_tick_data_ordBook > max_qty:
        
            filtered_timestamps =  (sorted_data) [max_qty:]

            result: list = [o for o in data_from_db if o['timestamp'] not in filtered_timestamps ]
            
            dump_data_as_list (file_name_pkl, result, check_duplicates)
                
    if 'params' in data_list:

        data_from_db = [o['params']  for o in data_from_db ]

        data_from_db = [o['data']  for o in data_from_db ]

        sorted_data: list = sorted([o['tick']  for o in data_from_db ])
        len_tick_data_ohlc: int = len ([o['tick']  for o in sorted_data ])  
        
        if len_tick_data_ohlc > max_qty:
            filtered_timestamps =  (sorted_data) [max_qty:]

            result: list = [o for o in data_from_db if o['tick'] not in filtered_timestamps ]

            dump_data_as_list (file_name_pkl, result, check_duplicates)
            
def append_and_replace_items_based_on_time_expiration (file_name_pkl: str, 
                                                       data: dict, time_expiration: int, 
                                                       check_duplicates: bool = False
                                                       )-> None:

    """
    append_and_replace_items_based_on_time_expiration in minute
    """
    from utils import time_modification

    append_data(file_name_pkl, data)
    data: object = read_data (file_name_pkl)

    if isinstance(data, dict):
        data_list = list (data)
        
    if isinstance(data, list):
        data_list = list (data [0])
        
    #data_list = list (data [0])
    now_time_utc = time_modification.convert_time_to_utc()['utc_now']
    now_time_utc_in_unix = time_modification. convert_time_to_unix (now_time_utc)

    one_hour_ago = now_time_utc_in_unix - time_expiration
    
    if 'change_id' in data_list:
        result: list =  ([o for o in data if  o['timestamp'] > one_hour_ago]) 
        dump_data_as_list (file_name_pkl, result, check_duplicates)
                
    if 'params' in data_list:

        data = [o['params']  for o in data ]

        data = [o['data']  for o in data ]
        
        result: list =  ([o for o in data if  o['tick'] < one_hour_ago])    
        dump_data_as_list (file_name_pkl, result)
        
