"""
Description:
    Deribit WebSocket Asyncio Example.
    - Authenticated connection.
Usage:
    python3.9 dbt-ws-authenticated-example.py
Requirements:
    - websocket-client >= 1.2.1
"""

# built ins
import asyncio
import sys
import json
import logging
from typing import Dict
from datetime import datetime, timedelta
from loguru import logger as log
from dask import delayed, compute    
import os
#from utils import formula

# installed
import websockets
import orjson
# user defined formula
from utils import save_open_files

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class main:
    
    '''
    # Market maker
    +----------------------------------------------------------------------------------------------+ 
        - tentukan koin yang akan ditransaksikan (pertimbangkan fundimg rate dan likuiditas)
        - kirim order long dan short secara bersamaan
        - tp: 0,5%. no cl
        - bila ada satu posisi rugi, maka di avg down (10%). posisi lawan kirim order dengan qty x 2
        
        id convention for subscription    4
        get             5
        
        public	        1
        private	        2
        --------------
        portfolio	    1	1	11
        user_order	    1	2	12
        my_trade	    1	3	13
        order_book	    2	4	24
        trade	        2	5	25
        index	        2	6	26
        announcement	2	7	27

    +----------------------------------------------------------------------------------------------+ 
    #  References: 
        + https://github.com/ElliotP123/crypto-exchange-code-samples/blob/master/deribit/websockets/dbt-ws-authenticated-example.py
    +----------------------------------------------------------------------------------------------+ 

    '''       
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

            # Subscribe to the specified WebSocket Channel
            #self.loop.create_task(
            #    self.ws_operation(
            #        operation='subscribe',
            #        ws_channel='trades.BTC-PERPETUAL.raw'
            #       )
            #    )

            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='user.portfolio.ETH'
                    )
                )
            
            self.loop.create_task(
            self.ws_operation(
                operation='subscribe',
                ws_channel='user.orders.ETH-PERPETUAL.raw'
                )
            )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='user.portfolio.BTC'
                    )
                )

            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel='book.BTC-PERPETUAL.none.20.100ms'
                    )
                )

            self.loop.create_task(
                self.ws_operation_get_instruments('ETH'
                    )
                )
            
            #self.loop.create_task(self.ws_operation_get_currencies())         

            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                #message: Dict = json.loads(message)
                #message: Dict = orjson.dumps(message)
                message: Dict = orjson.loads(message)
                message_channel: str = None
                balance_eth: float = []
                log.debug(message)
                
                #log.critical(message_or)

                if 'id' in list(message):
                    if message['id'] == 9929:
                        if self.refresh_token is None:
                            logging.debug('Successfully authenticated WebSocket Connection')
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
                
                if message_channel == 'trades.BTC-PERPETUAL.raw':
                    data_trades: list = message['params']['data']
                    log.info(data_trades)
                if message_channel == 'user.portfolio.btc':
                    data_portfolio: list = message['params']['data']
                    log.error(data_portfolio)
                if message_channel == 'user.portfolio.eth':
                    data_portfolio: list = message['params']['data']
                    balance_eth: list = data_portfolio ['balance']
                    log.critical(data_portfolio)
                    if balance_eth != []:
                        self.loop.create_task(
                    self.ws_operation(
                        operation='subscribe',
                        ws_channel='book.BTC-PERPETUAL.none.20.100ms'
                        )
                    )
                        
                    message: bytes = await self.websocket_client.recv()
                    #message: Dict = json.loads(message)
                    #message: Dict = orjson.dumps(message)
                    message: Dict = orjson.loads(message)
                    message_channel: str = None
                    balance_eth: float = []
                    log.debug(message)
                
                if message_channel == 'user.orders.ETH-PERPETUAL.raw':
                    data_orders: list = message['params']['data']
                    log.debug(data_orders)
                    
                if message_channel == 'book.BTC-PERPETUAL.none.20.100ms':
                    data_orders: list = message['params']['data']
                    
                    log.error(data_orders)
                    #save_open_files.save_file('order_books', data_orders)
                    
                    bids = data_orders['bids']
                    asks = data_orders['asks']
                    best_bid_prc = bids[0][0]
                    best_ask_prc = asks[0][0]
                    #save_open_files.save_file('order_books',data_orders)
                    log.warning(best_bid_prc)
                    log.error(best_ask_prc)
                log.critical (balance_eth)
            else:
                logging.info('WebSocket connection has broken.')
                sys.exit(1)
                
        return balance_eth

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

    async def ws_operation_get_currencies(
        self
            ) -> None:
        """
        """
        await asyncio.sleep(5)

        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": f"public/get_currencies",
                    "id": 42
                    }

        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )

    def get_currencies(self):
        self.loop.create_task(
                self.ws_operation_get_currencies()
                )


    async def ws_operation_get_instruments(
        self,
        currency: str,
        expired: str=False
            ) -> None:
        """
        Requests `public/subscribe` or `public/unsubscribe`
        to DBT's API for the specific WebSocket Channel.
        """
        await asyncio.sleep(5)
        params = {
            "currency": currency,
            "expired": expired
        }
        

        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": f"public/get_instruments",
                    "id": 55,
                    "params": params
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
    logging.basicConfig(
        level='DEBUG',
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )

    # DBT LIVE WebSocket Connection URL
    # ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    # DBT TEST WebSocket Connection URL
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'

    # DBT Client ID
    client_id: str = os.environ.get("client_id")
    # DBT Client Secret
    client_secret: str = os.environ.get("client_secret")

    app = main(
        ws_connection_url=ws_connection_url,
        client_id=client_id,
        client_secret=client_secret
        )
    app.ws_manager()
