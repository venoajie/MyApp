import websockets
import json
import time
from datetime import datetime
from loguru import logger as log
import asyncio
import numpy as np
import datetime as dt
#from configuration import api_configs

class DeribitWS:

    def __init__(self, live=False):

        if not live:
            self.url = 'wss://test.deribit.com/ws/api/v2'
        elif live:
            self.url = 'wss://www.deribit.com/ws/api/v2'
        else:
            raise Exception('live must be a bool, True=real, False=paper')

        self.msg = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": None,
        }

    async def pub_api(self, msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(msg)
            while websocket.open:
                response = await websocket.recv()
                return json.loads(response)
            
    @staticmethod
    def async_loop(api, message):
        return asyncio.get_event_loop().run_until_complete(api(message))


    # market data methods
    def fetch_ohlc(self, instrument, start, end, timeframe):
        params =  {
                "instrument_name": instrument,
                "start_timestamp": start,
                "end_timestamp": end,
                "resolution": timeframe
            }

        self.msg["method"] = "public/get_tradingview_chart_data"
        self.msg["params"] = params

        data = self.async_loop(self.pub_api, json.dumps(self.msg))
        return [data ['result']]

    def get_orderbook(self, instrument, depth=5):
        params = {
            "instrument_name": instrument,
            "depth": depth
        }
        self.msg["method"] = "public/get_order_book"
        self.msg["params"] = params

        order_book = self.async_loop(self.pub_api, json.dumps(self.msg)) ['result']
        return order_book

    def get_currencies(self):
        params = {}
        self.msg["method"] = "public/get_currencies"
        self.msg["params"] = params

        order_book = self.async_loop(self.pub_api, json.dumps(self.msg))['result']
        return  [o['currency'] for o in [ o for o in order_book]]
    
    def get_quote(self, instrument):
        params = {
            "instrument_name": instrument
        }
        self.msg["method"] = "public/ticker"
        self.msg["params"] = params
        quote = self.async_loop(self.pub_api, json.dumps(self.msg))

        return quote['result']['last_price']

    def available_instruments(self, currency, expired=False):
        params = {
            "currency": currency,
            #"kind": None,
            "expired": expired
        }

        self.msg["method"] = "public/get_instruments"
        self.msg["params"] = params
        result = self.async_loop(self.pub_api, json.dumps(self.msg)) ['result']
        return {'all': [o for o in [ o for o in result]],
                'future': [o  for o in [ o for o in result if o['kind']== 'future']],
                'option': [o  for o in [ o for o in result if o['kind']== 'option']],
                'future_combo': [o  for o in [ o for o in result if o['kind']== 'future_combo']],
                'option_combo': [o  for o in [ o for o in result if o['kind']== 'option_combo']],
                }

if __name__ == '__main__':

    while True:
        try:

            ws = DeribitWS(live=True)
            
            #get historic data for btc
            data = ws.fetch_ohlc("BTC-PERPETUAL", 1554373800000, 1554376800000, '1')
            log.warning(data)
            #code below is for limit orders
            # limit_response = ws.limit_order(instrument="BTC-PERPETUAL", amount=100, direction='short',
            #                                 price= 13500 ,  post_only= True, reduce_only=False)
            
            #shows the available futures contracts
            instruments = ws.available_instruments('ETH')
            log.error(instruments['option_combo'])
            currencies = ws.get_currencies()
            log.error(currencies)
            
            #get order book
            orderbook = ws.get_orderbook("BTC-PERPETUAL")
            log.info(orderbook)
            #get last bitcoin price
            btc_price = ws.get_quote("BTC-PERPETUAL")
            endtime = dt.datetime(2023, 11, 7, 20, 30) #change this to a suitable datetime
            log.debug(btc_price)
    
        except Exception as error:
            log.debug (error)
