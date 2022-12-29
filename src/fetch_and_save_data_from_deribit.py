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
from utils import pickling, formula, system_tools, string_modification, time_modification
from configuration import id_numbering, label_numbering
import deribit_get#,deribit_rest
from risk_management import spot_hedging
from portfolio.deribit import open_orders_management
import synchronizing_files

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id_test'),
            'client_secret': os.environ.get('client_secret_test')
            }
none_data = [None, [], '0.0', 0]
     
     

def telegram_bot_sendtext(bot_message, purpose: str = 'general_error') -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

    
class StreamMarketAccountData:
    
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
        self.connection_url: str = 'https://www.deribit.com/api/v2/' if 'test' not in ws_connection_url else 'https://test.deribit.com/api/v2/'
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

            my_path_instruments = system_tools.provide_path_for_file ('instruments',  currency) 
            instruments = pickling.read_data (my_path_instruments)
            instruments_name: list =  [o['instrument_name'] for o in instruments if o['kind'] == 'future']
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'user.portfolio.{currency}'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'user.orders.future.{currency}.raw'
                    )
                )
            
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'user.trades.future.{currency.upper()}.100ms'
                    )
                )
    
            self.loop.create_task(
                self.ws_operation(
                    operation='subscribe',
                    ws_channel=f'deribit_price_index.{currency.lower()}_usd'
                    )
                )
            
            for instrument in instruments_name:
                
                self.loop.create_task(
                    self.ws_operation(
                        operation='subscribe',
                        ws_channel=f'book.{instrument}.none.20.100ms'
                        )
                    )
                
            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                message: Dict = orjson.loads(message)
                message_channel: str = None
                #log.warning (message)
                if 'id' in list(message):
                    
                    if message['id'] == 9929:
                        if self.refresh_token is None:
                            log.debug('Successfully authenticated WebSocket Connection')
                            
                        else:
                            log.info('Successfully refreshed the authentication of the WebSocket Connection')
                            syn = synchronizing_files. SynchronizingFiles (
                                                                connection_url=self.connection_url,
                                                                client_id=self.client_id,
                                                                client_secret= self.client_secret
        )
                            await (syn.cancel_orders_hedging_spot_based_on_time_threshold(currency, 'hedging spot'))

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
            
                        symbol_index =  (message_channel)[-7:]
                        data_orders: list = message['params']['data']
                        currency = string_modification.extract_currency_from_text (message_channel)
                        currency = string_modification.extract_currency_from_text (message_channel)   
                                                      
                        my_path = system_tools.provide_path_for_file ('instruments',  currency)       

                        my_path_orders_open = system_tools.provide_path_for_file ('orders', currency, 'open')
                        
                        one_minute = 60000
                        
                        instrument_book = "".join(list(message_channel) [5:][:-14])
                        if message_channel == f'book.{instrument_book}.none.20.100ms':
                            #log.error (data_orders)
                            
                            my_path = system_tools.provide_path_for_file ('ordBook',  instrument_book) 
                            
                            try:
                                pickling.append_and_replace_items_based_on_time_expiration (my_path, data_orders, one_minute)
                            except:
                                continue        
                            
                        #log.critical (currency)                                                   
                                                   
                        symbol_index =  (message_channel)[-7:]
                        if message_channel == f'deribit_price_index.{symbol_index}':
                            
                            my_path = system_tools.provide_path_for_file ('index', symbol_index.lower()) 

                            pickling.replace_data(my_path, data_orders)
                           
                        #log.critical (message_channel == f'user.orders.future.{currency.upper()}.raw')
                        if message_channel == f'user.orders.future.{currency.upper()}.raw':
                            
                            #log.warning (f'{data_orders=}')
                            order_state = data_orders ['order_state']
                            order_id= data_orders ['order_id']
                            
                            my_path_orders_else = system_tools.provide_path_for_file ('orders', currency, order_state)
                            open_orders_open = pickling.read_data (my_path_orders_open) 
                            #log.debug (f'BEFORE {open_orders_open=}')
                            #log.warning (f'{order_state=}')
                            
                            if order_state == 'open':
                                #log.error ('ORDER_STATE OPEN')
                                pickling.append_and_replace_items_based_on_qty (my_path_orders_open, data_orders, 1000)
                                
                            else:
                                #log.error ('ORDER_STATE ELSE')
                                item_in_open_orders_open_with_same_id =  [o for o in open_orders_open if o['order_id'] == order_id ] 
                                item_in_open_orders_open_with_diff_id =  [o for o in open_orders_open if o['order_id'] != order_id ] 
                                #log.info (f'{item_in_open_orders_open_with_same_id=}')
                                #log.warning (f'{item_in_open_orders_open_with_diff_id=}')
                                
                                pickling.append_and_replace_items_based_on_qty (my_path_orders_else, data_orders, 1000)
                                
                                if item_in_open_orders_open_with_same_id != []:
                                    #log.critical ('item_in_open_orders_open_with_same_id')
                                    pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id, 100000)
                                    
                                pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id)
                                
                            open_orders_open = pickling.read_data (my_path_orders_open)     
                            #log.debug (f'AFTER {open_orders_open=}')
                        
                        my_trades_path_open = system_tools.provide_path_for_file ('myTrades', currency, 'open')
                        my_trades_path_closed = system_tools.provide_path_for_file ('myTrades', currency, 'closed')
                            
                        if message_channel == f'user.trades.future.{currency.upper()}.100ms':                            
                            #!
                            my_trades_open1 = pickling.read_data(my_trades_path_open)
                            label_my_trades_open1 = [o['label'] for o in my_trades_open1  ]
                            amount_my_trades_open = [o['amount'] for o in my_trades_open1  ]
                            sum_my_trades_open1 = sum([o['amount'] for o in my_trades_open1  ])
                            log.info (f'DATA TRADE FROM DB {sum_my_trades_open1} {amount_my_trades_open} {label_my_trades_open1}')
                            
                            log.error (f'DATA FROM EXC {data_orders=}')
                            log.error ([o['label'] for o in data_orders  ])
                            
                            #determine label id
                            try:
                                label_id= data_orders [0]['label']
                            except:
                                label_id= []
                            
                            # for data with label id/ordered through API    
                            if label_id != []:
                                pass

                            closed_label_id_int = string_modification.extract_integers_from_text(label_id)
                            log.critical (label_id)
                            log.critical (closed_label_id_int)

                            #log.debug ('open' in label_id)
                            #log.debug ('closed' in label_id)
                            
                            #!
                            sum_new_trading = [o['amount'] for o in data_orders  ][0]
                            sum_open_trading_after_new_trading = 0
                            #!

                            if 'open' in label_id:
                                log.critical ('LABEL ID OPEN')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_orders , 10000)
                                
                                #!
                                my_trades_open = pickling.read_data(my_trades_path_open)
                                label_my_trades_open = [o['label'] for o in my_trades_open  ]
                                amount_my_trades_open = [o['amount'] for o in my_trades_open  ]
                                sum_open_trading_after_new_trading = sum([o['amount'] for o in my_trades_open  ])
                                log.warning (f'DATA OPEN TRADE AFTER APPEND {sum_open_trading_after_new_trading}  {sum_open_trading_after_new_trading} {amount_my_trades_open=}')
                                #!
                                
                            if 'closed' in label_id:
                                log.critical ('LABEL ID CLOSED')
                                my_trades_open = pickling.read_data(my_trades_path_open)  
                                
                                #update mytrades db with the closed ones
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, data_orders , 10000)
                                
                                # SEPARATE OPEN AND CLOSED TRANSACTIONS IN OPEN DB
                                #update mytrades db with the still open ones
                                #my_trades_open = pickling.read_data(my_trades_path_open)  
                                remaining_open_trades = ([o for o in my_trades_open if  str(closed_label_id_int)  not in o['label'] ])
                                
                                #log.critical (f'REMAINING OPEN TRADES {remaining_open_trades=}')
                                pickling.replace_data (my_trades_path_open, remaining_open_trades )
                                    
                                #!
                                my_trades_open = pickling.read_data(my_trades_path_open)
                                label_my_trades_open = [o ['label']  for o in my_trades_open  ]
                                amount_my_trades_open = [o ['amount']  for o in my_trades_open  ]
                                sum_my_trades_open = sum([o['amount'] for o in my_trades_open  ])
                                log.warning (f'DATA REMAINING OPEN TRADE AFTER REPLACE CLOSED TRADES {sum_my_trades_open} {amount_my_trades_open} {label_my_trades_open=}')
                                    
                                closed_trades_in_my_trades_open = ([o for o in my_trades_open if  str(closed_label_id_int)  in o['label'] ])
                                #log.error (f'{closed_trades_in_my_trades_open=}')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, closed_trades_in_my_trades_open , 10000)
                                
                                #!
                                my_trades_closed = pickling.read_data(my_trades_path_closed)
                                if my_trades_closed !=[]:
                                    log.warning (my_trades_closed)
                                    label_my_trades_closed = [o ['label']  for o in my_trades_closed  ]
                                    sum_my_trades_open = sum([o['amount'] for o in my_trades_closed  ])
                                    log.warning (f'DATA CLOSED TRADE FINAL {sum_my_trades_open} {label_my_trades_closed=}')
                                    
                                    
                            if label_id == [] :
                                my_trades_path_manual = system_tools.provide_path_for_file ('myTrades', currency, 'manual')
                                log.error ('[]')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_manual, data_orders, 10000)
                                
                            
                            #!
                            my_trades_open = pickling.read_data(my_trades_path_open)
                            #log.debug (f'AFTER 2 {my_trades_open=}')
                            sum_open_trading_after_new_closed_trading = sum([o['amount'] for o in my_trades_open  ])
                            
                            info= (f'CHECK TRADING SUM {label_id=} sum_new_trading: {sum_new_trading} sum_open_trading_after_new_trading: {sum_open_trading_after_new_trading} final_sum_open: {sum_open_trading_after_new_closed_trading} \n ')
                            
                            log.critical (info)
                            telegram_bot_sendtext(info)
                            #!
                            
                        my_path_portfolio = system_tools.provide_path_for_file ('portfolio', currency.lower())                                                                                     
                        if message_channel == f'user.portfolio.{currency.lower()}':
                            pickling.replace_data(my_path_portfolio, data_orders)

            else:
                log.info('WebSocket connection has broken.')
                formula.log_error('WebSocket connection has broken','fetch and save ALL data from deribit ', 'error', .1)
                
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

        #log.warning(id)
        log.warning(msg)
        await self.websocket_client.send(
            json.dumps(
                msg
                )
            )
                
def main ():
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
    try:

        StreamMarketAccountData (
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

    
