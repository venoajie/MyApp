#!/usr/bin/env python
# -*- coding: utf-8 -*-

# built ins
import requests

# installed
from loguru import logger as log
from dataclassy import dataclass

@dataclass(unsafe_hash=True, slots=True)
class MarketData ():
                
    '''
 
    '''       
          
    symbol: str = None
    
    def ohlc_endPoint(self):
        return  (f' https://test.deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp=1554376800000&instrument_name=ETH-PERPETUAL&resolution=30&start_timestamp=1554373800000')
        
    def ohlc(self):

        try:            
            return requests.get(self.ohlc_endPoint()).json()['result']

        except Exception as error:
            import traceback
            log.error(f"{error}")
            log.error(traceback.format_exc())


if __name__ == "__main__":
    
    try:

        market_data = MarketData('ETH-PERPETUAL')
        ohlc = market_data.ohlc()
        print (ohlc)
                
        #file_name = 'TRXBTC_1h.bin'
        #home_path = str(pathlib.Path.home())
        #data_path = os.path.join(home_path, file_name)
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        
        formula.log_error('open interest','open interest main', error, 10)
        