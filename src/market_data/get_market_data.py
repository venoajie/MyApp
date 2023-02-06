#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
import requests
from datetime import datetime

# installed
from dataclassy import dataclass

# user defined formula
from utilities import time_modification
#

def catch_error (error, 
                 idle: int = None
                 ) -> list:
    """
    """
    from utilities import system_tools
    system_tools.catch_error_message(error, idle)
    
        
@dataclass(unsafe_hash=True, slots=True)
class MarketData ():
                
    '''
 
    '''       
          
    currency: str = 'ETH'
    symbol: str = 'ETH-PERPETUAL'
    headers: list = {
            "accept": "application/json",
            "coinglassSecret": "877ad9af931048aab7e468bda134942e"
        }
    
    def ohlc_endPoint(self, 
                      resolution: int, 
                      start_timestamp: int, 
                      end_timestamp: int
                      ):
        return  (f' https://deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp={end_timestamp}&instrument_name={self.symbol}&resolution={resolution}&start_timestamp={start_timestamp}')
        
    def ohlc(self, 
             resolution, 
             qty_candles
             ):
            
        now_utc = datetime.now()
        now_unix = time_modification.convert_time_to_unix (now_utc)
        start_timestamp = now_unix - 60000 * qty_candles
        
        try:            
            return requests.get(self.ohlc_endPoint(resolution, start_timestamp, now_unix)).json()['result']

        except Exception as error:
            catch_error (error)

    def open_interest_symbol_endPoint(self):
        return  (f' https://open-api.coinglass.com/public/v2/open_interest?symbol={self.currency}')
        
    def open_interest_symbol(self):

        try:            
            try:
                return requests.get(self.open_interest_symbol_endPoint()).json()['data']
            except:
                return requests.get(self.open_interest_symbol_endPoint(), headers=self.headers).json()['data']

        except Exception as error:
            catch_error (error)

    def open_interest_historical_endPoint(self, 
                                          time_frame: str, 
                                          currency: str
                                          ):
        return  (f' https://open-api.coinglass.com/public/v2/open_interest_history?symbol={self.currency}&time_type={time_frame}&currency={currency}')
    
    def open_interest_historical(self, 
                                 time_frame: str = 'm5', 
                                 currency: str = 'USD'
                                 ):
        
                    
        '''
        time_frame = m1 m5 m15 h1 h4 h12 all
        currency = USD or symbol
    
        '''       

        try:
            try:
                return requests.get(self.open_interest_historical_endPoint(time_frame, currency)).json()['data']
            except:
                return requests.get(self.open_interest_historical_endPoint(time_frame, currency), headers=self.headers).json()['data']

        except Exception as error:
            catch_error (error)

    def open_interest_aggregated_ohlc_endPoint(self, 
                                               time_frame: str
                                               ):
                    
        '''
        interval = m1 m5 m15 h1 h4 h12 all
    
        '''       
        return  (f' https://open-api.coinglass.com/public/v2/indicator/open_interest_aggregated_ohlc?symbol={self.currency}&interval={time_frame}')
    
    
    def open_interest_aggregated_ohlc(self, 
                                      time_frame: str = 'm5'
                                      ):
                    
        '''
        interval = m1 m5 m15 h1 h4 h12 all
    
        '''

        try:
            try:
                return requests.get(
                                    self.open_interest_aggregated_ohlc_endPoint(time_frame)
                                    ).json()['data']
            except:
                return requests.get(
                                    self.open_interest_aggregated_ohlc_endPoint(time_frame), 
                                    headers=self.headers
                                    ).json()['data']
            
        except Exception as error:
            catch_error (error)
        