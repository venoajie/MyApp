#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from typing import Dict
from datetime import datetime, timedelta
import os
from os.path import join, dirname
import json
from functools import lru_cache
from pathlib import Path
import pathlib

##
# installed
import websockets
import asyncio
import orjson
from loguru import logger as log
from dotenv import load_dotenv
#from dask import delayed, compute    

# user defined formula 
from utils import pickling, system_tools, formula
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    

    return {'client_id': os.environ.get('client_id'),
            'client_secret': os.environ.get('client_secret')
            }

#root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#log.warning(root)

none_data = [None, [], '0.0', 0]

#@dataclass(unsafe_hash=True, slots=True)
class DeribitMarketDownloader:
    
    '''
        
    +----------------------------------------------------------------------------------------------+ 
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
                    ws_channel='user.portfolio.ETH'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='user.orders.future.ETH.raw'
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

                    if message['id'] == 402:
                        pickling.replace_data('instruments.pkl', message)
                    
                elif 'method' in list(message):
                    # Respond to Heartbeat Message
                    if message['method'] == 'heartbeat':
                        await self.heartbeat_response()

                if 'params' in list(message):
                    
                    if message['method'] != 'heartbeat':
                        message_channel = message['params']['channel']
                        
                        index_price = pickling.read_data (system_tools.create_path_for_market_data_deribit_output ('eth-index.pkl') )[0]
                        log.warning (index_price)
            
                        instruments = pickling.read_data (system_tools.create_path_for_market_data_deribit_output ('eth-instruments.pkl') )[0]['result']
                            
                        all_instruments_name = [] if instruments == [] else [o['instrument_name'] for o in instruments]   
                        log.warning (all_instruments_name)


                        if message_channel == 'user.portfolio.eth':
                            data_orders: list = message['params']['data']
                            log.debug(data_orders)
                            pickling.replace_data('eth-portfolio.pkl', data_orders)
                            
                        if portfolio  in none_data:
                            try:
                                portfolio = pickling.read_data('portfolio-eth.pkl')
                            except:
                                portfolio = []                            
                            for instrument in all_instruments_name:
                                log.error (instrument)
                                if portfolio != [] and index_price != []:
                                    pass

                        
                            
            else:
                log.info('WebSocket connection has broken.')
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
        
def main ():
    
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

    
