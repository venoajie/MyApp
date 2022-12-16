# -*- coding: utf-8 -*-

def remove_redundant_elements (data: list)->list:
    
    '''  
    # https://www.codegrepper.com/code-examples/python/remove+redundant+elements+in+list+python
    # https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43
    
    '''      
    
    return sorted(set(data))    

def extract_texts_for_currency(words: str) -> str:
    
    '''  
    extracting surrency from channel message
    '''      
    
    if 'eth' in (words).lower():
        return 'eth'
    if 'btc' in (words).lower():
        return 'btc'

    
