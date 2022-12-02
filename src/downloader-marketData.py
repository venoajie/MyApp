#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from typing import Dict
from datetime import datetime, timedelta
from time import sleep
import os
import json
from functools import lru_cache
from pathlib import Path

##
# installed
import websockets
import asyncio
import orjson
from loguru import logger as log
from dataclassy import dataclass
from dotenv import dotenv_values
from dotenv import load_dotenv
#from dask import delayed, compute    

# user defined formula 
from utils import pickling, formula
from configuration import id_numbering
import deribit_get

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    

    return {'client_id': os.environ.get('client_id'),
            'client_secret': os.environ.get('client_secret')
            }

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log.warning(root)
#sys.path.append(root + '/python')

#log.warning(sys.path.append(root + '/python'))
none_data = [None, [], '0.0', 0]

#@dataclass(unsafe_hash=True, slots=True)
class main:
    
    '''
    # Market maker
    +----------------------------------------------------------------------------------------------+ 
        - tentukan koin yang akan ditransaksikan (pertimbangkan fundimg rate dan likuiditas)
        - kirim order long dan short secara bersamaan
        - tp: 0,5%. no cl
        - bila ada satu posisi rugi, maka di avg down (10%). posisi lawan kirim order dengan qty x 2
        
    +----------------------------------------------------------------------------------------------+ 
    #  References: 
        + https://github.com/ElliotP123/crypto-exchange-code-samples/blob/master/deribit/websockets/dbt-ws-authenticated-example.py
        + https://niekdeschipper.com/projects/asyncio.md
        + https://stackoverflow.com/questions/40143289/why-do-most-asyncio-examples-use-loop-run-until-complete
        + https://realpython.com/async-io-python/
        + https://www.youtube.com/watch?v=ZzfHjytDceU
        + https://stackoverflow.com/questions/71279168/how-to-stop-python-websocket-connection-after-some-seconds
        + https://alpaca.markets/learn/advanced-live-websocket-crypto-data-streams-in-python/
        + https://sammchardy.github.io/async-binance-basics/
        + https://github.com/SilverBeavers/deribit_testnet_copy_trader/blob/main/deribit_ws.py
        + https://trading-data-analysis.pro/understanding-crypto-trading-order-book-and-depth-graphs-data-1bb2adc32976
        + https://pratham1202.medium.com/python-for-finance-5-efficient-frontier-and-creating-an-optimal-portfolio-4f4
        
        Basic:
        + https://websockets.readthedocs.io/en/6.0/intro.html
        + https://www.codementor.io/@jflevesque/python-asynchronous-programming-with-asyncio-library-eq93hghoc
    +----------------------------------------------------------------------------------------------+ 

    '''       
    def __init__(
        self,
        ws_connection_url: str,
        client_id: str,
        client_secret: str
            ) -> None:
        # Async Event Loop
        self.loop = asyncio.get_event_loop() # https://stackoverflow.com/questions/65206110/when-to-use-asyncio-get-running-loop-or-asyncio-get-event-loop-in-python

        # Instance Variables
        self.ws_connection_url: str = ws_connection_url
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.websocket_client: websockets.WebSocketClientProtocol = None
        self.refresh_token: str = None
        self.refresh_token_expiry_time: int = None

        # Start Primary Coroutine
        self.loop.run_until_complete(
            self.ws_manager()
            )
        
    #@lru_cache(maxsize=None)
    async def ws_manager(self) -> None:
        async with websockets.connect(
            self.ws_connection_url,
            ping_interval=None,
            compression=None,
            close_timeout=60
            ) as self.websocket_client:

            # Authenticate WebSocket Connection
            await self.ws_auth()

            # Establish Heartbeat
            await self.establish_heartbeat()

            # Start Authentication Refresh Task
            self.loop.create_task(
                self.ws_refresh_auth()
                )

            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='book.ETH-PERPETUAL.none.20.100ms'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='chart.trades.ETH-PERPETUAL.1'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='deribit_price_index.eth_usd'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation_get_instruments('ETH','future'
                    )
                )
            
            self.loop.create_task (self.ws_operation_get_currencies())
            
            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                message: Dict = orjson.loads(message)
                message_channel: str = None
                

                if 'id' in list(message):
                    
                    if message['id'] == 9929:
                        if self.refresh_token is None:
                            log.debug('Successfully authenticated WebSocket Connection')
                        else:
                            log.info('Successfully refreshed the authentication of the WebSocket Connection')

                        self.refresh_token = message['result']['refresh_token']

                        # Refresh Authentication well before the required datetime
                        if message['testnet']:
                            expires_in: int = 300
                        else:
                            expires_in: int = message['result']['expires_in'] - 240

                        self.refresh_token_expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)

                    elif message['id'] == 8212:
                        # Avoid logging Heartbeat messages
                        continue

                    if message['id'] == 402:
                        pickling.replace_data('instruments.pkl', message)
                    
                elif 'method' in list(message):
                    # Respond to Heartbeat Message
                    if message['method'] == 'heartbeat':
                        await self.heartbeat_response()

                if 'params' in list(message):
                    
                    # Set root equal to  current folder
                    root = Path(".")

                    if message['method'] != 'heartbeat':
                        message_channel = message['params']['channel']
            
                        index_price = []
                        data_orders: list = message['params']['data']
                        
                        if message_channel == 'deribit_price_index.eth_usd':

                            index_price = data_orders ['price']
                            my_path = root / "market_data" / "eth-index.pkl"
                            pickling.replace_data(my_path, index_price)
                            
                        try:
                            index_price = pickling.read_data('eth-index.pkl')#['result']
                            index_price = index_price [0]

                        except:
                            index_price = []
                            
                        if message_channel == 'book.ETH-PERPETUAL.none.20.100ms':

                            bids = data_orders['bids']
                            asks = data_orders['asks']                                        
                            best_bid_prc = bids[0][0]
                            best_ask_prc = asks[0][0]                       
                        
                        if message_channel == 'chart.trades.ETH-PERPETUAL.1':

                            data : list = message 
                            file_name = (f'eth-perpetual-ohlc-1m')
                            my_path = root / "market_data" / file_name

                            try:
                                pickling.append_and_replace_items_based_on_qty (my_path, data, 10000)          
                            except:
                                continue
            
                        tick_size = []
                        min_trade_amount = []
                        contract_size = []
                        instruments_with_rebates = []
                        all_instruments = []
                        min_hedged_size = []
                        
                        try:
                            instruments = pickling.read_data('instruments.pkl')['result']
                        except:
                            instruments = []
                            
                        all_instruments = [] if instruments == [] else [o['instrument_name'] for o in instruments]   
                        if instruments not  in none_data:
                            log.error(f'{all_instruments=}')
                            log.error(f'{all_instruments=} {portfolio=} {index_price=}')
                            
                            for instrument in all_instruments:
                                if portfolio != [] and index_price != []:

                                    try:
                                        portfolio = portfolio [0]
                                    except:
                                        portfolio = portfolio 

                                    instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 
                                    #log.error(f'{instrument_data=}')
                                    tick_size:float = instrument_data ['tick_size']
                                    min_trade_amount = instrument_data ['min_trade_amount']
                                    contract_size = instrument_data ['contract_size']
                                    expiration_timestamp = instrument_data ['expiration_timestamp']
                                    instruments_with_rebates = [o['instrument_name'] for o in instruments if o['maker_commission'] <0]     


                                    log.info(f'{instruments_with_rebates=}')
                                    log.warning(f'{min_hedged_size=}')
                                    #log.warning(instruments)
                                    log.error(f'{best_bid_prc=}')
                                    log.debug(f'{best_ask_prc=}')
                                    log.error(f'{index_price=}')
                                    log.warning(f'{expiration_timestamp=}')
                                    log.info(f'{tick_size=} {min_trade_amount=} {contract_size=} {instruments_with_rebates=}')
                                    
            else:
                log.info('WebSocket connection has broken.')
                formula.sleep_and_restart_program(1)
                
    async def establish_heartbeat(self) -> None:
        """
        Requests DBT's `public/set_heartbeat` to
        establish a heartbeat connection.
        """
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "id": 9098,
                    "method": "public/set_heartbeat",
                    "params": {
                              "interval": 10
                               }
                    }

                
        try:
            await self.websocket_client.send(
            json.dumps(
                msg
                )
                )
        except Exception as error:
            log.warning (error)

    async def heartbeat_response(self) -> None:
        """
        Sends the required WebSocket response to
        the Deribit API Heartbeat message.
        """
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "id": 8212,
                    "method": "public/test",
                    "params": {}
                    }

        try:
            await self.websocket_client.send(
            json.dumps(
                msg
                )
                )

        except Exception as error:
            log.warning (error)
            
    async def ws_auth(self) -> None:
        """
        Requests DBT's `public/auth` to
        authenticate the WebSocket Connection.
        """
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "id": 9929,
                    "method": "public/auth",
                    "params": {
                              "grant_type": "client_credentials",
                              "client_id": self.client_id,
                              "client_secret": self.client_secret
                               }
                    }

        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )

    async def ws_refresh_auth(self) -> None:
        """
        Requests DBT's `public/auth` to refresh
        the WebSocket Connection's authentication.
        """
        while True:
            if self.refresh_token_expiry_time is not None:
                if datetime.utcnow() > self.refresh_token_expiry_time:
                    msg: Dict = {
                                "jsonrpc": "2.0",
                                "id": 9929,
                                "method": "public/auth",
                                "params": {
                                          "grant_type": "refresh_token",
                                          "refresh_token": self.refresh_token
                                            }
                                }

                    await self.websocket_client.send(
                        json.dumps(
                            msg
                            )
                            )

            await asyncio.sleep(150)

    async def ws_operation(
        self,
        operation: str,
        ws_channel: str,
        id: int=100
            ) -> None:
        """
        Requests `public/subscribe` or `public/unsubscribe`
        to DBT's API for the specific WebSocket Channel.
        """
        await asyncio.sleep(5)

        id = id_numbering.id(operation, ws_channel)
        
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": f"public/{operation}",
                    "id": id,
                    "params": {
                        "channels": [ws_channel]
                        }
                    }

        log.warning(id)
        log.warning(msg)
        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )

    async def ws_operation_get_currencies(
        self
            ) -> None:
        """
        """
        await asyncio.sleep(5)

        msg: Dict = 'https://test.deribit.com/api/v2/public/get_currencies?'

        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )
        
    async def ws_operation_get_instruments(
        self,
        currency: str,
        kind: str=None,
        expired: bool=False
            ) -> None:
        """
        Requests `public/subscribe` or `public/unsubscribe`
        to DBT's API for the specific WebSocket Channel.
        """
        await asyncio.sleep(5)
        params = {
            "currency": currency,
            "kind": kind,
            "expired": expired
        }
        
        method =  f"public/get_instruments"
        id = id_numbering.id(method, method)
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "id": id,
                    "params": params
                    }


        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )
        
        
def main_ ():
    #config = dotenv_values(".env")
    #log.info (config)
    #log.info (load_dotenv())
    #print ( parse_dotenv())
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'
         # ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'

    try:
        main(
        ws_connection_url=ws_connection_url,
        client_id=client_id,
        client_secret= client_secret
        )

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
    
if __name__ == "__main__":

    # DBT Client ID
    client_id: str = parse_dotenv() ['client_id']
    # DBT Client Secret
    client_secret: str = parse_dotenv() ['client_secret']
    config = {
    'client_id': 'client_id',
    'client_secret': 'client_secret'
}
    db_config = [{k: os.environ.get(v) for k, v in config.items()}]
    #log.error (db_config)
    db_config = [o  for o in db_config]
    #log.error (db_config)
        
    try:
        main_()
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        asyncio.get_event_loop().run_until_complete(main_().stop_ws())
        #sys.exit()

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)

    
