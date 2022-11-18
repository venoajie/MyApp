#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
import sys
import logging
from typing import Dict
from datetime import datetime, timedelta
from time import sleep
import os
from functools import lru_cache
#from utils import formula

# installed
import websockets
import asyncio
import orjson
import json
from dask import delayed, compute    
from loguru import logger as log
from os.path import join, dirname
from dotenv import load_dotenv
from dataclassy import dataclass
import deribit_get
# user defined formula
from utils import save_open_files
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

log.warning(root)
log.warning(sys.path.append(root + '/python'))
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
        
        id convention
        
        method
        subscription    3
        get             4
        
        auth
        public	        1
        private	        2
        
        instruments
        all             0
        btc             1
        eth             2
        
        subscription
        --------------  method      auth    seq    inst
        portfolio	        3	    1	    01
        user_order	        3	    1	    02
        my_trade	        3	    1	    03
        order_book	        3	    2	    04
        trade	            3	    1	    05
        index	            3	    1	    06
        announcement	    3	    1	    07

        get
        --------------
        currencies	        4	    2	    01
        instruments	        4	    2	    02
        positions	        4	    1	    03
        
        
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
                    ws_channel='book.ETH-PERPETUAL.none.20.100ms'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation_get_instruments('ETH','future'
                    )
                )
            
            self.loop.create_task (self.ws_operation_get_positions("ETH"))
            self.loop.create_task (self.ws_operation_get_currencies())
            
            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                #message: Dict = json.loads(message)
                #message: Dict = orjson.dumps(message)
                message: Dict = orjson.loads(message)
                message_channel: str = None
                message_channel_list: str = None
                #log.debug(message)
                #await self.ws_manager_private()
                endpoint_position: str = 'private/get_positions'
                                
                #log.critical(list(message))

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
                    log.warning((message))
                    log.warning(list(message))
                    log.warning(message['params']['channel'] != ['ETH','eth'])

                    if message['method'] != 'heartbeat':
                        message_channel = message['params']['channel']
                                    
                    if  message['params']['channel'] == ['ETH','eth']:
                    
                        log.error(f'{message=}')
                        data_orders: list = message['params']['data']
                        
                        #log.error(message_channel)
                        position =  await deribit_get.get_position(client_id, client_secret, endpoint_position, "ETH")#['result']
                        instrument_name =  [o['instrument_name'] for o in position ]
                        net_position = sum([o['size'] for o in position ])
                        log.info(instrument_name)
                        log.info(net_position)
                        #log.info(data_orders)
                        #log.error(position)
                        index_price = position[0]['index_price']
                        log.error(index_price)
                        
                        #save_open_files.save_file('order_books', data_orders)
                        
                        #save_open_files.save_file('order_books',data_orders)
                        
                        if message_channel == 'user.portfolio.eth':
                            data_orders: list = message['params']['data']
                            equity = data_orders ['equity']
                            #log.debug(data_orders)
                            log.debug(f'{equity=}')
                            notional = index_price * equity
                            min_hedged_size = notional
                            log.error(f'{notional=}')
                        
                            if equity not in none_data:
                                        
                                save_open_files.save_file_to_pickle('portfolio-eth.pkl', equity)
                        # 
                            if equity  in none_data:

                                bids = data_orders['bids']
                                asks = data_orders['asks']                                        
                                best_bid_prc = bids[0][0]
                                best_ask_prc = asks[0][0]
                                log.critical(best_bid_prc)
                                log.critical(best_ask_prc)
                                balance = save_open_files.open_file_pickle('portfolio-eth.pkl')
                                log.warning(balance)
                                    
                            data_portfolio: list = message['params']['data']
                            #log.critical(data_portfolio)
                            balance_eth: list = data_portfolio ['balance']
                        #log.critical(balance_eth)
                                              #if balance_eth in none_data:
                        #    balance = save_open_files.open_file_pickle('portfolio-eth.pkl')
                        #    log.warning(balance)
                                    
                if message_channel == 'trades.BTC-PERPETUAL.raw':
                    data_trades: list = message['params']['data']
                    log.info(data_trades)
                if message_channel == 'user.portfolio.btc':
                    data_portfolio: list = message['params']['data']
                    log.error(data_portfolio)
                
                    
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
        id: int=42
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
        log.critical(msg)

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

        test = await self.websocket_client.send(
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
    async def ws_operation_get_positions(
        self,
        currency: str
            ) -> None:
        """
        """
        await asyncio.sleep(5)
        params = {
            "currency": currency,
        }
        

        method =  f"private/get_positions"
        id = id_numbering.id(method, method)
        msg: Dict = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "id": id,
                    "params": params
                    }

        log.warning(msg)

        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )
        
            
    def run_connection(conn):
        try:
            conn.run()
        except KeyboardInterrupt:
            print("Interrupted execution by user")
            asyncio.get_event_loop().run_until_complete(conn.stop_ws())
            exit(0)
        except Exception as e:
            print(f'Exception from websocket connection: {e}')
        finally:
            print("Trying to re-establish connection")
            sleep(3)
            #run_connection(conn)
        
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
    
    main(
        ws_connection_url=ws_connection_url,
        client_id=client_id,
        client_secret=client_secret
        )
