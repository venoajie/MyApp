# -*- coding: utf-8 -*-

def remove_redundant_elements (data: list)-> list:
    
    '''  
    Remove redundant items in a list
    
    Args:
        data (list) 

    Returns:
        list:  

    Example:
        data_original = ['A', 'A', 'B', 'B', 'B', 'C']
        data_cleaned = ['A','B','C']  
        
    Reference:
        1. https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python 
        2. https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43          
    '''     
    
    # Create an empty list
    result = []
    
    # Check if the data is a list and not empty
    if isinstance(data, list) and data !=[]:
        
        try:         
            # Ref 1
            result = list(
            {
                frozenset(
                    item.items()
                    ):item for item in data
                }.values()
            )  
            
        except:   
            # Ref 2     
            result = list(dict.fromkeys(data))
            
    return result

def find_unique_elements (data1: list, 
                          data2: list
                          )->list:
    
    '''  
    
    Comparing two lists and picking only unique items between them
    
    Args:
        data (list)  and its subset (list) for comparation
 
    Returns:
        list
        
    Example:
        data_original = [1, 2, 3, 4, 5] # all data
        data_redundant = [2, 4] # subset of all data
        data_cleaned =  [1, 3, 5]    
    
    Reference:
        https://stackoverflow.com/questions/45098206/unique-values-between-2-lists
    
    '''      
    return [i for i in data1 if i not in data2]
    

def extract_currency_from_text (words: str) -> str:
    
    '''  
    Extracting currency from channel message
    '''      
    
    if 'eth' in (words).lower():
        return 'eth'
    if 'btc' in (words).lower():
        return 'btc'

def extract_integers_from_text (words: list) -> int:
    
    '''  
    Extracting integers from label text
    '''      
    
    try:
        return int (''.join([o for o in words if o.isdigit()]))

    except:
        return []

    
