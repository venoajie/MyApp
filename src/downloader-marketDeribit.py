#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from typing import Dict
from datetime import datetime, timedelta
import os
from os.path import join, dirname
import json
from functools import lru_cache

##
# installed
import websockets
import asyncio
import orjson
from loguru import logger as log
from dotenv import load_dotenv

# user defined formula 
from utils import pickling, formula, system_tools, string_modification
from configuration import id_numbering
import deribit_get

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id'),
            'client_secret': os.environ.get('client_secret')
            }
none_data = [None, [], '0.0', 0]
    
    
async def call_api(curr, msg):
    async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
        
        #await asyncio.gather(*[self.call_api(json.dumps(item)) for item in url ])
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            response: dict = orjson.loads(response)
            response_data: dict = response ['result']

            if response['id'] == 7617:
                file_name = (f'{curr.lower()}-instruments.pkl')
                my_path = system_tools.provide_path_for_file (file_name, "market_data", "deribit")

                pickling.replace_data(my_path, response_data)  
                                          
            if response['id'] == 7538:
                file_name = (f'currencies.pkl')
                my_path = system_tools.provide_path_for_file (file_name, "market_data", "deribit")
                pickling.replace_data(my_path, response_data)   
                
currencies = ['ETH', 'BTC']
for curr in currencies:

    msg = \
        {
        "jsonrpc" : "2.0",
        "id" : 7617,
        "method" : "public/get_instruments",
        "params" : {
            "currency" : f"{curr}",
            "kind" : "future",
            "expired" : False
        }
        }
    msg_curr = \
        {
        "jsonrpc" : "2.0",
        "id" : 7538,
        "method" : "public/get_currencies",
        "params" : {

        }
        }    
    url =  [msg, msg_curr] 
    
    asyncio.gather(*[call_api(curr, json.dumps(item)) for item in url ])       
    
class DeribitMarketDownloader:
    
    '''
        
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

            currencies = ['ETH', 'BTC']
            for currency in currencies:
                file_name_instruments = (f'{currency.lower()}-instruments.pkl')
                my_path_instruments = system_tools.provide_path_for_file (file_name_instruments, "market_data", "deribit")
                instruments = pickling.read_data (my_path_instruments)
                instruments_name: list =  [o['instrument_name'] for o in instruments ]
                
                instruments_name = [] if instruments == [] else [o['instrument_name'] for o in instruments]  
                
                for instrument in instruments_name:
                
                    self.loop.create_task(
                        self.ws_operation(
                            operation='subscribe',
                            ws_channel=f'book.{instrument}.none.20.100ms'
                            )
                        )
                    
                    if instrument in ['ETH-PERPETUAL', 'BTC-PERPETUAL'] :
                        self.loop.create_task(
                            self.ws_operation(
                                operation='subscribe',
                                ws_channel=f'chart.trades.{instrument}.1'
                                )
                            )
                            
                        self.loop.create_task(
                            self.ws_operation(
                                operation='subscribe',
                                ws_channel=f'deribit_price_index.{currency.lower()}_usd'
                                )
                            )
                
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
                    
                elif 'method' in list(message):
                    # Respond to Heartbeat Message
                    if message['method'] == 'heartbeat':
                        await self.heartbeat_response()

                if 'params' in list(message):
                    
                    if message['method'] != 'heartbeat':
                        message_channel = message['params']['channel']
            
                        symbol_index =  (message_channel)[-7:]
                        data_orders: list = message['params']['data']
                        currency = string_modification.extract_for_currency (message_channel)

                        log.critical (currency)
                        if message_channel == f'deribit_price_index.{symbol_index}':
                            currency = (symbol_index)[:3]
                            
                            file_name = (f'{currency.lower()}-index.pkl')
                            my_path = system_tools.provide_path_for_file (file_name, "market_data", "deribit")

                            pickling.replace_data(my_path, data_orders)
                             
                        instrument = "".join(list(message_channel) [5:][:-14])
                        if message_channel == f'book.{instrument}.none.20.100ms':

                            file_name = (f'{instrument.lower()}-ordBook')
                            my_path = system_tools.provide_path_for_file (file_name, "market_data", "deribit")
                            
                            try:
                                pickling.append_and_replace_items_based_on_qty (my_path, data_orders, 10)          
                            except:
                                continue        
                                                        
                        instrument = "".join(list(message_channel) [13:][:-2])
                        if message_channel == f'chart.trades.{instrument}.1':
                            
                            file_name = (f'{instrument.lower()}-ohlc-1m')                            
                            my_path = system_tools.provide_path_for_file (file_name, "market_data", "deribit")

                            try:
                                pickling.append_and_replace_items_based_on_qty (my_path, data_orders, 600)          
                            except:
                                continue
                        
            else:
                log.info('WebSocket connection has broken.')
                formula.log_error('WebSocket connection has broken','downloader-marketDeribit', 'error', 1)
                system_tools.sleep_and_restart_program(1)
                
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
                
def main ():
    
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    try:

        DeribitMarketDownloader (
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
            main()
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)

    
