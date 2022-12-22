
# built ins
import asyncio
import sys, os
import json
import logging
from typing import Dict
from datetime import datetime, timedelta
from os.path import join, dirname
from functools import lru_cache


# installed
import websockets
import orjson
from loguru import logger as log
from dotenv import load_dotenv

# user defined formula 
from utils import pickling, formula, system_tools, string_modification
from configuration import id_numbering
#import deribit_get

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id_test'),
            'client_secret': os.environ.get('client_secret_test')
            }

class main:
    def __init__(
        self,
        ws_connection_url: str,
        client_id: str,
        client_secret: str
            ) -> None:
        # Async Event Loop
        self.loop = asyncio.get_event_loop()

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
                my_path = system_tools.provide_path_for_file ('instruments', currency.lower()) 
                instruments = pickling.read_data (my_path)
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
                message: bytes = await self.websocket_client.recv()
                message: Dict = json.loads(message)
                logging.info(message)

                if 'id' in list(message):
                    if message['id'] == 9929:
                        if self.refresh_token is None:
                            logging.info('Successfully authenticated WebSocket Connection')
                        else:
                            logging.info('Successfully refreshed the authentication of the WebSocket Connection')

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
                        currency = string_modification.extract_currency_from_text (message_channel)

                        if message_channel == f'deribit_price_index.{symbol_index}':
                            
                            my_path = system_tools.provide_path_for_file ('index', symbol_index.lower()) 

                            pickling.replace_data(my_path, data_orders)

                        instrument = "".join(list(message_channel) [5:][:-14])
                        #log.debug (instrument)
                        one_minute = 60000
                        one_hour = one_minute * 60000
                        
                        if message_channel == f'book.{instrument}.none.20.100ms':
                            #log.error (data_orders)
                            
                            my_path = system_tools.provide_path_for_file ('ordBook',  instrument.lower()) 
                            
                            try:
                                pickling.append_and_replace_items_based_on_time_expiration (my_path, data_orders, one_hour)
                            except:
                                continue        
                            
                        instrument = "".join(list(message_channel) [13:][:-2])
                        if message_channel == f'chart.trades.{instrument}.1':
                                              
                            my_path = system_tools.provide_path_for_file ('ohlc-1m', instrument.lower()) 

                            try:
                                pickling.append_and_replace_items_based_on_time_expiration (my_path, data_orders, one_hour)
                            except:
                                continue
                        
                            
            else:
                logging.info('WebSocket connection has broken.')
                sys.exit(1)

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

        await self.websocket_client.send(
            json.dumps(
                msg
                )
                )

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

        await self.websocket_client.send(
            json.dumps(
                msg
                )
                )

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
        ws_channel: str
            ) -> None:
        """
        Requests `public/subscribe` or `public/unsubscribe`
        to DBT's API for the specific WebSocket Channel.
        """
        await asyncio.sleep(5)

        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": f"public/{operation}",
                    "id": 42,
                    "params": {
                        "channels": [ws_channel]
                        }
                    }

        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )


if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level='INFO',
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )

    # DBT LIVE WebSocket Connection URL
    # ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    # DBT TEST WebSocket Connection URL
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'

    # DBT Client ID
    client_id: str = '7aDpbWD0'
    # DBT Client Secret
    client_secret: str = 'M5xtKo6i-maY0y1MaO6a4uV1S6SKhGaraCQ_vY_D_pE'

    main(
         ws_connection_url=ws_connection_url,
         client_id=client_id,
         client_secret=client_secret
         )