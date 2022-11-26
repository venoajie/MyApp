#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import  pathlib, os
from loguru import logger as log
from dataclassy import dataclass

@dataclass(unsafe_hash=True, slots=True)
class OpenInterest ():
                
    '''
 
    '''       
          
    symbol: str = None
    headers: list = {
            "accept": "application/json",
            "coinglassSecret": "877ad9af931048aab7e468bda134942e"
        }
    
    def open_interest_symbol_endPoint(self):
        return  (f' https://open-api.coinglass.com/public/v2/open_interest?symbol={self.symbol}')
        
    def open_interest_symbol(self):

        try:            
            return requests.get(self.open_interest_symbol_endPoint(), headers=self.headers).json()['data']

        except Exception as error:
            import traceback
            log.error(f"{error}")
            log.error(traceback.format_exc())
    
    
    def open_interest_historical_endPoint(self, time_type: str = 'm5', currency: str = 'USD'):
        return  (f' https://open-api.coinglass.com/public/v2/open_interest_history?symbol={self.symbol}&time_type={time_type}&currency={currency}')
    
    def open_interest_historical(self, time_type: str = 'm5', currency: str = 'USD'):
        
                    
        '''
        time_type = m1 m5 m15 h1 h4 h12 all
        currency = USD or symbol
    
        '''       

        try:
            log.warning (self.open_interest_symbol_endPoint())
            log.warning (self.headers)
            req= requests.get(self.open_interest_historical_endPoint(time_type, currency), headers=self.headers).json()['data']
            log.error (req)
            return requests.get(self.open_interest_historical_endPoint(time_type, currency), headers=self.headers).json()['data']

        except Exception as error:
            import traceback
            log.error(f"{error}")
            log.error(traceback.format_exc())


def check_and_save_every_5_minutes ():
    from utils import pickling
        
    try:
        open_interest =  OpenInterest('BTC')
        open_interest_historical = open_interest. open_interest_historical ()
        pickling.replace_data('open_interest_historical.pkl', open_interest_historical)
        log.debug (pickling.read_data('open_interest_historical.pkl'))
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())
    
check_and_save_every_5_minutes()

file_name = 'TRXBTC_1h.bin'
home_path = str(pathlib.Path.home())
data_path = os.path.join(home_path, file_name)
log.warning (home_path)
log.error (data_path)

    
# https://opensource.com/article/20/4/python-crypto-trading-bot
    