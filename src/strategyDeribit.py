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
import deribit_get,deribit_rest
from risk_management import spot_hedging
from portfolio.deribit import open_orders_management

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@lru_cache(maxsize=None)
def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id_test'),
            'client_secret': os.environ.get('client_secret_test')
            }
none_data = [None, [], '0.0', 0]
    
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
            for currency in currencies:
                file_name_instruments = (f'{currency.lower()}-instruments.pkl')
                my_path_instruments = system_tools.provide_path_for_file (file_name_instruments, "market_data", "deribit")
                instruments = pickling.read_data (my_path_instruments)
                instruments_name: list =  [o['instrument_name'] for o in instruments ]
                
                instruments_name = [] if instruments == [] else [o['instrument_name'] for o in instruments]  
                                            
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
            
                        data_orders: list = message['params']['data']

                        currency = string_modification.extract_texts_for_currency (message_channel)
                        
                        file_name_index = (f'{currency.lower()}-index.pkl')
                        my_path = system_tools.provide_path_for_file (file_name_index, "market_data", "deribit")
                        index_price = pickling.read_data(my_path)[0]['price']
                                               
                        file_name_instruments = (f'{currency.lower()}-instruments.pkl')
                        file_name_myTrades = (f'{currency.lower()}-myTrades-open.pkl')
                        my_path_instruments = system_tools.provide_path_for_file (file_name_instruments, "market_data", "deribit")
                        my_path_myTrades = system_tools.provide_path_for_file (file_name_myTrades, "portfolio", "deribit")
                        instruments = pickling.read_data (my_path_instruments)
                        myTrades = pickling.read_data (my_path_myTrades)
                        log.error (myTrades)
                        instruments_with_rebates = [o['instrument_name'] for o in instruments if o['maker_commission'] <0]
                        instruments_name = [] if instruments == [] else [o['instrument_name'] for o in instruments] 
                        log.debug (instruments_name)
                            
                        endpoint_position: str = 'private/get_positions'
                        endpointCancel: str = 'private/cancel'
                        position =  await deribit_get.get_position(client_id, client_secret, endpoint_position, currency.upper())
                        position = position ['result']
                        #log.warning (position)
                                            
                        if message_channel == f'user.orders.future.{currency}.raw':
                            log.debug (data_orders)
                            
                            file_name = (f'{currency.lower()}-orders')    
                                                    
                            my_path = system_tools.provide_path_for_file (file_name, "portfolio", "deribit")
                            
                            pickling.append_and_replace_items_based_on_qty (my_path, data_orders, 100000)
                                                   
                        if message_channel == f'user.trades.future.{currency.upper()}.100ms':
                            log.error (data_orders)
                            
                            file_name = (f'{currency.lower()}-myTrades-open')    
                                                    
                            my_path = system_tools.provide_path_for_file (file_name, "portfolio", "deribit")
                            
                            pickling.append_and_replace_items_based_on_qty (my_path, data_orders[0], 100000)

                        open_orders: list = await self.open_orders (currency)

                        open_orders_byBot: list = open_orders.my_orders_api()

                        open_orders_lastUpdateTStamps: list = open_orders.my_orders_api_last_update_timestamps()
                        
                        #endpoint_open_orders_currency: str = f'private/get_open_orders_by_currency'
                        #open_ordersREST = await deribit_get.get_open_orders_byCurrency (client_id, client_secret, endpoint_open_orders_currency, currency.upper())
                        #open_ordersREST = open_ordersREST ['result']
                        #open_orders_byManual = [o for o in open_ordersREST if o['web'] == True]
                        #open_orders_byBot = [o for o in open_ordersREST if o['web'] == False ]
                        #open_orders_Hedging = ([o for o in open_orders_byBot if o['label'] == "hedging spot"])
                        #open_orders_lastUpdateTStamps = ([o['last_update_timestamp'] for o in open_orders_byBot ])

                        one_minute = 60000

                        now_time = time_modification.convert_time_to_utc()['utc_now']
                        now_time_unix = time_modification.convert_time_to_unix (now_time)
                        
                        if open_orders_byBot not in none_data:
                            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
                            open_orders_lastUpdateTStamp_min_Id= ([o['order_id'] for o in open_orders_byBot if o['last_update_timestamp'] == open_orders_lastUpdateTStamp_min])[0]
                            open_orders_deltaTime = now_time_unix - open_orders_lastUpdateTStamp_min                       
                            
                            if open_orders_deltaTime > one_minute:
                                await deribit_get.get_cancel_order_byOrderId(client_id, client_secret, endpointCancel, open_orders_lastUpdateTStamp_min_Id)
                        
                        if message_channel == f'user.portfolio.{currency.lower()}':
                            
                            file_name = (f'{currency.lower()}-portfolio.pkl')

                            my_path_portfolio = system_tools.provide_path_for_file (file_name, "portfolio", "deribit")
                            
                            pickling.replace_data(my_path_portfolio, data_orders)
                            
                            portfolio = pickling.read_data(my_path_portfolio)
                            equity = portfolio [0]['equity']
                            notional = index_price * equity    
                                
                            for instrument in instruments_name:
                                instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 
                                    
                                file_name_ordBook = (f'{instrument.lower()}-ordBook.pkl')
                                my_path_ordBook = system_tools.provide_path_for_file (file_name_ordBook, "market_data", "deribit")
                                
                                ordBook = pickling.read_data(my_path_ordBook)
                                #print (ordBook)
                                max_time_stamp_ordBook = max ([o['timestamp'] for o in ordBook ])
                                most_current_ordBook = [o for o in ordBook if o['timestamp'] == max_time_stamp_ordBook ]
                                #print (most_current_ordBook)
                                best_bid_prc= most_current_ordBook[0]['bids'][0][0]
                                best_ask_prc= most_current_ordBook[0]['asks'][0][0]
                                    
                                min_trade_amount = instrument_data ['min_trade_amount']
                                contract_size = instrument_data ['contract_size']
                                min_hedged_size = notional / min_trade_amount * contract_size
                                log.info(f'{min_hedged_size=} {notional=} {min_trade_amount=}')
                                instrument_position = sum([o['size'] for o in position if o['instrument_name'] == instrument ])
                                instrument_position_hedging = sum([o['size'] for o in position if o['instrument_name'] in instruments_with_rebates ])
                                hedging_size = int(min_hedged_size if instrument_position_hedging == [] else min_hedged_size + instrument_position_hedging)
                                #!open_orders_hedging:list = [o for o in open_ordersREST if o['label'] == 'hedging spot'] 
                                open_orders_hedging:list = [o for o in open_orders_byBot if o['label'] == 'hedging spot'] 
                                open_orders_hedging_size:int = sum([o['amount'] for o in open_orders_hedging] )
                                #log.info(f'{position=}')
                                endpoint_short: str = 'private/sell'
                                endpoint_long: str = 'private/buy'
                                log.warning (f'{instrument}')
                                log.warning (f'{open_orders_hedging_size}')
                        
                                if open_orders_hedging_size in none_data and hedging_size > 0:
                                    label: str = 'hedging spot'
                                    perpetual = 'PERPETUAL'
                                    log.warning (f'{open_orders_hedging_size}')
                                    
                                    log.warning (f'{perpetual in instrument}')
                                    
                                    #if perpetual in instrument:
                                    if instrument in instruments_with_rebates:
                                        log.error (f'{instrument}')
                                        
                                        await deribit_get.send_order_limit (client_id, 
                                                                    client_secret, 
                                                                    endpoint_short, 
                                                                    instrument, 
                                                                    hedging_size, 
                                                                    best_ask_prc, 
                                                                    label)
                                                        
                                        #open_ordersREST = await deribit_get.get_open_orders_byCurrency (client_id, client_secret, endpoint_open_orders_currency, currency.upper())
                                        #open_ordersREST = open_ordersREST ['result']
                                        open_orders: list = await self.open_orders (currency)
                                        open_orders_byBot: list = open_orders.my_orders_api()
                                        open_orders_Hedging = ([o  for o in open_orders_byBot if o['label'] == "hedging spot"])
                                        open_orders_HedgingSum = sum([o['amount'] for o in open_orders_Hedging ])
                                        if open_orders_HedgingSum > hedging_size:
                                            open_orders_Hedging_lastUpdateTStamps = ([o['last_update_timestamp'] for o in open_orders_Hedging ])
                                            open_orders_Hedging_lastUpdateTStamp_min = min(open_orders_Hedging_lastUpdateTStamps)
                                            open_orders_Hedging_lastUpdateTStamp_minId = ([o['order_id'] for o in open_orders_byBot if o['last_update_timestamp'] == open_orders_Hedging_lastUpdateTStamp_min])[0]
                                            await deribit_get.get_cancel_order_byOrderId(client_id, client_secret, endpointCancel, open_orders_Hedging_lastUpdateTStamp_minId)
                                            
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

    def compute_notional_value(self, index_price: float,  equity: float) -> float:
        """
        """

        return index_price * equity
    
    async def open_orders (self, currency) -> float:
        """
        """

        open_ordersREST: list = await deribit_rest.get_open_orders_byCurrency (self.connection_url, client_id, client_secret, currency.upper())
        open_ordersREST: list = open_ordersREST ['result']
        open_orders: list = open_orders_management.MyOrders (open_ordersREST)
                        
        return open_orders_management.MyOrders (open_ordersREST)
    
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
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    ws_connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    ws_connection_url: str = 'wss://test.deribit.com/ws/api/v2'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
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

    
