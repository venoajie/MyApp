#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
from functools import lru_cache
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from functools import wraps
from unittest import result
from loguru import logger as log
from unsync import unsync

none_data=[None, 0, []]


def remove_redundant_elements (data):
    
    '''  
    # https://www.codegrepper.com/code-examples/python/remove+redundant+elements+in+list+python
    # https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43
    
    '''      
    
    return sorted(set(data))    

def extract_for_currency(words) -> None:
    
    if 'eth' in (words).lower():
        return 'eth'
    if 'btc' in (words).lower():
        return 'btc'
  
        
if __name__ == "__main__":

    # DBT Client ID
    resp = 'user.trades.future.BTC.100ms'
    #curr = (resp)[-3:]#[:3]
    instrument = extract_for_currency (resp)
    print (instrument)
    instrument = (instrument)
    print (instrument)
    
