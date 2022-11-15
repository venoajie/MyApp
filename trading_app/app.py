import websockets
import json
import time
from datetime import datetime
from loguru import logger as log
import asyncio
import numpy as np
import datetime as dt
#from configuration import api_configs


# https://hatpub.tistory.com/111
    
    # 거래소에서 발급 받은 publick, secret key
#client_id = 'F1Gp2cmS'
#client_secret = 'gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ'
    

class DeribitWS:

    def __init__(self, client_id, client_secret, live=False):

        if not live:
            self.url = 'wss://test.deribit.com/ws/api/v2'
        elif live:
            self.url = 'wss://www.deribit.com/ws/api/v2'
        else:
            raise Exception('live must be a bool, True=real, False=paper')


        self.client_id = client_id
        self.client_secret = client_secret

        self.auth_creds = {
              "jsonrpc" : "2.0",
              "id" : 0,
              "method" : "public/auth",
              "params" : {
                "grant_type" : "client_credentials",
                "client_id" : self.client_id,
                "client_secret" : self.client_secret
              }
            }

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

    async def priv_api(self, msg):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(self.auth_creds))
            while websocket.open:
                response = await websocket.recv()
                await websocket.send(msg)
                response = await websocket.recv()
                break
            return json.loads(response)

    @staticmethod
    def async_loop(api, message):
        return asyncio.get_event_loop().run_until_complete(api(message))


    def market_order(self, instrument, amount, direction):
        params = {
                "instrument_name" : instrument,
                "amount" : amount,
                "type" : "market",
              }

        if direction.lower() == 'long':
            side = 'buy'
        elif direction.lower() == 'short':
            side = 'sell'
        else:
            raise ValueError('direction must be long or short')

        self.msg["method"] = f"private/{side}"
        self.msg["params"] = params

        response = self.async_loop(self.priv_api, json.dumps(self.msg))

        return response


    def limit_order(self, instrument, amount, direction, price,
                   post_only, reduce_only):
        params = {
            "instrument_name": instrument,
            "amount": amount,
            "type": "limit",
            "price": price,
            "post_only":  post_only,
            "reduce_only": reduce_only

        }
        if direction.lower() == 'long':
            side = 'buy'
        elif direction.lower() == 'short':
            side = 'sell'
        else:
            raise ValueError('direction must be long or short')

        self.msg["method"] = f"private/{side}"
        self.msg["params"] = params
        response = self.async_loop(self.priv_api, json.dumps(self.msg))
        return response

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

        order_book = self.async_loop(self.pub_api, json.dumps(self.msg))
        return order_book

    def get_currencies(self):
        params = {}
        self.msg["method"] = "public/get_currencies"
        self.msg["params"] = params

        order_book = self.async_loop(self.pub_api, json.dumps(self.msg))
        return order_book
    
    def get_quote(self, instrument):
        params = {
            "instrument_name": instrument
        }
        self.msg["method"] = "public/ticker"
        self.msg["params"] = params
        quote = self.async_loop(self.pub_api, json.dumps(self.msg))

        return quote['result']['last_price']

    #account methods
    def account_summary(self, currency, extended=True):
        params = {
            "currency": currency,
            "extended": extended
        }

        self.msg["method"] = "private/get_account_summary"
        self.msg["params"] = params
        summary = self.async_loop(self.priv_api, json.dumps(self.msg))
        return summary

    def get_positions(self, instrument, kind="future"):
        params = {
            "instrument_name": instrument,
            "kind": kind
        }
        self.msg["method"] = "private/get_positions"
        self.msg["params"] = params
        positions = self.async_loop(self.priv_api, json.dumps(self.msg))
        return positions

    def available_instruments(self, currency, kind="future", expired=False):
        params = {
            "currency": currency,
            "kind": kind,
            "expired": expired
        }

        self.msg["method"] = "public/get_instruments"
        self.msg["params"] = params
        resp = self.async_loop(self.pub_api, json.dumps(self.msg))
        instruments = [d["instrument_name"] for d in resp['result']]
        return instruments


async def main():
    
    creds = {
  "real": {
    "client_id" : "F1Gp2cmS",
    "client_secret" : "gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ"
    },
  "paper": {
     "client_id" : "F1Gp2cmS",
    "client_secret" : "gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ"
  }
}

    client_id = creds['paper']['client_id']
    client_secret = creds['paper']['client_secret']
    exchange = DeribitWS(client_id=client_id, client_secret=client_secret, live=True)
    log.warning(exchange)
    await exchange.market_order("BTC-PERPETUAL", 100, 'short')
    #markets = list(exchange.markets.values())
    #symbols = [market['symbol'] for market in markets if not market['darkpool']]
    #await asyncio.gather(*[loop(exchange, symbol, n) for n, symbol in enumerate(symbols)])
    await exchange.close()


if __name__ == '__main__':
    creds = {
  "real": {
    "client_id" : "F1Gp2cmS",
    "client_secret" : "gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ"
    },
  "paper": {
     "client_id" : "F1Gp2cmS",
    "client_secret" : "gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ"
  }
}

    client_id = creds['paper']['client_id']
    client_secret = creds['paper']['client_secret']
    
    loop = asyncio.get_event_loop()


    #asyncio.run(main())
    while True:
        try:



            ws = DeribitWS(client_id=client_id, client_secret=client_secret, live=True)
            #market order for $100 worth of btc
            test_resp = ws.market_order("BTC-PERPETUAL", 100, 'short')
            #get historic data for btc
            data = ws.fetch_ohlc("BTC-PERPETUAL", 1554373800000, 1554376800000, '1')
            log.warning(data)
            #code below is for limit orders
            # limit_response = ws.limit_order(instrument="BTC-PERPETUAL", amount=100, direction='short',
            #                                 price= 13500 ,  post_only= True, reduce_only=False)
            
            #shows the available futures contracts
            instruments = ws.available_instruments('ETH')
            log.error(instruments)
            currencies = ws.get_currencies()
            log.error(currencies)
            
            #get order book
            orderbook = ws.get_orderbook("BTC-PERPETUAL")
            log.info(orderbook)
            #get last bitcoin price
            btc_price = ws.get_quote("BTC-PERPETUAL")
            endtime = dt.datetime(2023, 11, 7, 20, 30) #change this to a suitable datetime
            log.debug(btc_price)
                    
            loop.run_until_complete()
            loop.run_forever()
    
        except Exception as error:
            log.debug (error)
