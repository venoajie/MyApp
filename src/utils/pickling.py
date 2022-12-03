# -*- coding: utf-8 -*-

# built ins
import pickle
import os

def append_data (file_name: str, data: dict)-> None:

    """
    https://stackoverflow.com/questions/28077573/python-appending-to-a-pickled-list
    """

    file_name: str =f"""{file_name}.pkl"""
    
    collected_data: list = []
    if os.path.exists(file_name):

        with open(file_name,'rb') as handle: 
            collected_data = pickle.load(handle)

    collected_data.append(data)

    # Now we "sync" our database
    with open(file_name,'wb') as handle:
        pickle.dump(collected_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Re-load our database
    with open(file_name,'rb') as handle:
        collected_data = pickle.load(handle)
    return collected_data

def read_data (file_name: str)-> None:

    """
    """

    try:
        with open(file_name,'rb') as handle:
            scores = pickle.load(handle)
            return scores
    except:
        return []

def replace_data (file_name: str, data: dict)-> None:

    """
    """

    with open(file_name,'wb') as handle:
        pickle.dump([data], handle, protocol=pickle.HIGHEST_PROTOCOL)

def append_and_replace_items_based_on_qty (file_name: str, data: dict, max_qty: int)-> None:

    """
    append_and_replace_items_based_on_qty (file_name, resp, 3)
    """
    
    
    file_name_pkl:str =f"""{file_name}.pkl"""

    append_data(file_name, data)
    data: object = read_data (file_name_pkl)
    #print (data)

    len_tick_data: int = len ([o['tick']  for o in data ])  

    if len_tick_data > max_qty:
        filter: list = [min([o['tick']  for o in data ])]
        result: list = ([o for o in data if o['tick'] not in filter ])

        with open(file_name_pkl,'wb') as handle:
            
            pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
if __name__ == "__main__":

    # DBT Client ID
    resp = {
      "volume": 259.157425,
      "tick": 1669939740000,
      "open": 1275.85,
      "low": 1275.85,
      "high": 1275.85,
      "cost": 330521,
      "close": 1275.85
    }
 
    try:
        file_name = 'was'
        append_and_replace_items_based_on_qty (file_name, resp, 3)

    except Exception as error:
        print (error)

    
