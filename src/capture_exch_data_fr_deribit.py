#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from datetime import datetime, timedelta
import os
from os.path import join, dirname
import json
from functools import lru_cache

# installed
import websockets
import asyncio
import orjson
from loguru import logger as log
from dotenv import load_dotenv

# user defined formula 
from utilities import pickling, system_tools, string_modification
from configuration import id_numbering
from portfolio.deribit import open_orders_management, myTrades_management
import deribit_get
import apply_strategies

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id'),
            'client_secret': os.environ.get('client_secret')
            }
    
def telegram_bot_sendtext(bot_message, 
                          purpose: str = 'general_error'
                          ) -> None:
    from utilities import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)
    
class StreamAccountData:
    
    '''
        
    +----------------------------------------------------------------------------------------------+ 
    +----------------------------------------------------------------------------------------------+ 

    '''       
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        live=True
        ) -> None:
        
        # Async Event Loop
        self.loop = asyncio.get_event_loop() 
        
        if not live:
            self.ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'
        elif live:
            self.ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
        else:
            raise Exception('live must be a bool, True=real, False=paper')
        
        # Instance Variables
        self.connection_url: str = 'https://www.deribit.com/api/v2/' \
            if 'test' not in self.ws_connection_url else 'https://test.deribit.com/api/v2/'
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
            #for currency in currencies: isu, multiple currency could interfere each other in the calculation function
            currency = 'ETH'

            my_path_instruments = system_tools.provide_path_for_file(
                                                                    'instruments',  
                                                                     currency
                                                                     ) 
            instruments = pickling.read_data (my_path_instruments)
            #instruments_name: list =  [o['instrument_name'] for o in instruments if o['kind'] == 'future']
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'user.portfolio.{currency}'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'user.changes.any.{currency.upper()}.100ms'
                    )
                )
            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                message: dict = orjson.loads(message)
                message_channel: str = None
                #log.warning (message)
                if 'id' in list(message):
                    
                    if message['id'] == 9929:
                        if self.refresh_token is None:
                            await self.get_sub_accounts(currency)
                            log.debug('Successfully authenticated WebSocket Connection')
                            
                        else:
                            log.info('Successfully refreshed the authentication of the WebSocket Connection')
                            
                            syn = apply_strategies. ApplyHedgingSpot (
                                                                    self.connection_url,
                                                                    self.client_id,
                                                                    self.client_secret,
                                                                    currency
                                                                           )
                            server_time = await syn.current_server_time ()
                            await (syn.cancel_orders_hedging_spot_based_on_time_threshold(server_time, 
                                                                                          'hedgingSpot'
                                                                                          )
                                   )
                            await (syn.cancel_redundant_orders_in_same_labels_closed_hedge())
                            await self.get_sub_accounts(currency)
                            #await synchronizing_files

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
                        #log.info (message_channel)
            
                        data_orders: list = message['params']['data']
                        currency: str = string_modification.extract_currency_from_text (message_channel)
                                                                                                                
                        if message_channel == f'user.changes.any.{currency.upper()}.100ms':
                            log.info (data_orders)
                            positions = data_orders ['positions']
                            trades = data_orders ['trades']
                            orders = data_orders ['orders']
                            
                            if trades:
                                my_trades = myTrades_management.MyTrades (trades)
                                my_trades.distribute_trade_transaction(currency)
                                
                            if orders:
                                my_orders = open_orders_management.MyOrders (orders)
                                my_orders.distribute_order_transactions (currency)
                                
                            if positions:
                                #log.error (positions)
                                my_path_position = system_tools.provide_path_for_file (
                                                                                        'positions', 
                                                                                        currency
                                                                                        )
                                pickling.replace_data(my_path_position, 
                                                      positions
                                                      )
                                
                        await self.get_sub_accounts(currency)                                                      
            else:
                log.info('WebSocket connection has broken.')
                system_tools.catch_error_message (error, 
                                                    .1, 
                                                    'WebSocket connection EXCHANGE has broken'
                                                    )
                
    async def get_sub_accounts(self,
                               currency
                               ) -> list:
        """
        """
        
        try:
            
            result: dict =  await deribit_get.get_subaccounts (
                                                                self.connection_url, 
                                                                self.client_id,
                                                                self.client_secret, 
                                                                currency
                                                            )
            #log.warning(result)
            result_sub_account =  result ['result'] 
            my_path_sub_account = system_tools.provide_path_for_file ('sub_accounts', 
                                                                      currency
                                                                      )
            pickling.replace_data(my_path_sub_account, 
                                  result_sub_account
                                  )
            return result_sub_account
    
        except Exception as error:
            log.warning (error)

    async def establish_heartbeat(self) -> None:
        """
        Requests DBT's `public/set_heartbeat` to
        establish a heartbeat connection.
        """
        msg: dict = {
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
        msg: dict = {
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
        msg: dict = {
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
                    msg: dict = {
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
        
        msg: dict = {
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
                
def main ():
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
    
    try:

        StreamAccountData (
        client_id=client_id,
        client_secret= client_secret
        )

    except Exception as error:
        system_tools.catch_error_message (error, 10, 'fetch and save EXCHANGE data from deribit')
    
if __name__ == "__main__":

    try:
        main()
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        system_tools.catch_error_message (error, 10, 'fetch and save EXCHANGE data from deribit')

    
