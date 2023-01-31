# -*- coding: utf-8 -*-

def remove_redundant_elements (data: list)->list:
    
    '''  
    + Checks if the data is a list and not empty
    + If the data is a list and not empty, create a new list with unique values from the data
    '''     
    
    # Create an empty list
    result = []
    
    # Check if the data is a list and not empty
    if isinstance(data, list) and data !=[]:
        
        try:         
            # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python  
            result = list(
            {
                frozenset(
                    item.items()
                    ):item for item in data
                }.values()
            )  
            
        except:   
            # https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43         
            result = list(dict.fromkeys(data))
            
    return result


def find_unique_elements (data1: list, 
                          data2: list
                          )->list:
    
    '''  
    data1 = all data
    data2 = subset of data1
    # https://stackoverflow.com/questions/45098206/unique-values-between-2-lists
    
    '''      
    return [i for i in data1 if i not in data2]
    

def extract_currency_from_text (words: str) -> str:
    
    '''  
    extracting currency from channel message
    '''      
    
    if 'eth' in (words).lower():
        return 'eth'
    if 'btc' in (words).lower():
        return 'btc'

def extract_integers_from_text (words: list) -> int:
    
    '''  
    extracting integers from label text
    '''      
    
    try:
        return int (''.join([o for o in words if o.isdigit()]))

    except:
        return []

    
