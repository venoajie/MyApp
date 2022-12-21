#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
import numpy as np
import pandas as pd

# installed
from loguru import logger as log
from market_understanding import some_statistics

# user defined formula 
from utils import pickling, system_tools

def transform_result_to_data_frame (data: object):

    df = pd.DataFrame(ordBook)

    # Column name standardization
    df	= 	df.rename(columns={'tick':'date','open': 'open','high': 'high', 'low': 'low',
                            'close': 'close','volume': 'volume','cost': 'costUsd' })
    
    # Filter relevant data
    df = df.loc[:,['date', 'open', 'high', 'low', 'close',  'volume', 'costUsd']]

    for col in ('open', 'high', 'low', 'close', 'volume', 'costUsd'):
        df[col] = df[col].astype(np.float32)
        
    log.critical (instrument)
    print (df)
    # Set index
    tsidx = pd.DatetimeIndex(pd.to_datetime(df['date'], unit='ms'), dtype='datetime64[ns]')
    df.set_index(df['date'], inplace=True)
    df = df.drop(columns=['date'])
    df.index.names = ['date']
    df = df.iloc[::-1].reset_index()   
    return df    
            
            

instruments_perpetual = ['ETH-PERPETUAL', 'BTC-PERPETUAL']

for instrument in instruments_perpetual:

    file_name = (f'{instrument.lower()}-ohlc-1m.pkl')   
    my_path_ordBook = system_tools.provide_path_for_file ('ohlc-1m', 'read', instrument)    
    ordBook = pd.read_pickle (my_path_ordBook)
    df = transform_result_to_data_frame(ordBook)
    chechk_outliers = some_statistics.check_outliers (df,'costUsd')
    outliers = some_statistics.outlier (df,'costUsd')

    log.critical (chechk_outliers)
    log.critical (outliers)
    # Set index

    if 'ETH' in instrument:
        pass#log.error (df)
    if 'BTC' in instrument:
        pass#log.warning (df)       
            