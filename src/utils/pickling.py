# -*- coding: utf-8 -*-

# built ins
import pickle
import os

def append_data (file_name: str, data: dict)-> None:

    """
    https://stackoverflow.com/questions/28077573/python-appending-to-a-pickled-list
    """

    file_name=f"""{file_name}.pkl"""
    
    scores = []
    
    if os.path.exists(file_name):

        with open(file_name,'rb') as handle: 
            scores = pickle.load(handle)

    scores.append(data)

    # Now we "sync" our database
    with open(file_name,'wb') as handle:
        pickle.dump(scores, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Re-load our database
    with open(file_name,'rb') as handle:
        scores = pickle.load(handle)
    return scores

def read_data (file_name: str)-> None:

    """
    """

    with open(file_name,'rb') as handle:
        scores = pickle.load(handle)
        return scores

def replace_data (file_name: str, data: dict)-> None:

    """
    """

    with open(file_name,'wb') as handle:
        pickle.dump([data], handle, protocol=pickle.HIGHEST_PROTOCOL)



