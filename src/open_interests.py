#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
import requests

# installed
from loguru import logger as log
from dataclassy import dataclass

# user defined formula
from utils import formula

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
            try:
                return requests.get(self.open_interest_symbol_endPoint()).json()['data']
            except:
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
            try:
                return requests.get(self.open_interest_historical_endPoint(time_type, currency)).json()['data']
            except:
                return requests.get(self.open_interest_historical_endPoint(time_type, currency), headers=self.headers).json()['data']

        except Exception as error:
            import traceback
            log.error(f"{error}")
            log.error(traceback.format_exc())

    def open_interest_aggregated_ohlc_endPoint(self, interval, start_time, end_time):
                    
        '''
        interval = m1 m5 m15 h1 h4 h12 all
    
        '''       
        return  (f' https://open-api.coinglass.com/public/v2/indicator/open_interest_aggregated_ohlc?symbol={self.symbol}&interval={interval}&start_time={start_time}&end_time={end_time}')
    
    def open_interest_aggregated_ohlc(self, interval, start_time, end_time):
                    
        '''
        interval = m1 m5 m15 h1 h4 h12 all
    
        '''

        return requests.get(self.open_interest_aggregated_ohlc_endPoint(interval, start_time, end_time), headers=self.headers)
    
def check_and_save_every_5_minutes ():
    from utils import pickling
        
    try:
        open_interest =  OpenInterest('ETH')
        open_interest_historical = open_interest. open_interest_historical ()
        pickling.replace_data('open_interest_historical.pkl', open_interest_historical)
        
        open_interest_symbol = open_interest. open_interest_symbol ()
        pickling.replace_data('open_interest_symbol.pkl', open_interest_symbol)
        
    except Exception as error:
        import traceback
        log.error(f"{error}")
        log.error(traceback.format_exc())

if __name__ == "__main__":
    
    try:

        check_and_save_every_5_minutes()
        formula.sleep_and_restart_program (600)
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        
        formula.log_error('open interest','open interest main', error, 10)
        