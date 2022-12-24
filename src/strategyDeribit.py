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
from configuration import id_numbering, label_numbering
import deribit_get#,deribit_rest
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
    
class strategyDeribit:
    
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
                my_path_instruments = system_tools.provide_path_for_file ('instruments', currency.lower())
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
                

                for instrument in instruments_name:
                    self.loop.create_task(
                        self.ws_operation(
                            operation='subscribe',
                            ws_channel=f'book.{instrument}.none.20.100ms'
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
                #log.debug (message)
                
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

                        currency = string_modification.extract_currency_from_text (message_channel)
                        
                        symbol_index = (f'{currency.lower()}_usd')
                        my_path = system_tools.provide_path_for_file ('index', symbol_index)
                        index_price = []
                        
                        try:
                            index_price = pickling.read_data(my_path)[0]['price']
                        except:
                            index_price = []
                                                      
                        #log.debug (f'{currency.lower()=}')   
                        my_path = system_tools.provide_path_for_file ('instruments',  currency)          

                        instruments = pickling.read_data (my_path)

                        #instruments_with_rebates = [o['instrument_name'] for o in instruments if o['maker_commission'] <0]
                        log.critical (instruments_name)
                        instruments_name = [] if instruments == [] else [o['instrument_name'] for o in instruments] 

                        my_path_orders_open = system_tools.provide_path_for_file ('orders', currency, 'open')
                        
                        one_minute = 60000
                        one_hour = one_minute * 60000
                        
                        instrument_book = "".join(list(message_channel) [5:][:-14])
                        if message_channel == f'book.{instrument_book}.none.20.100ms':
                            #log.error (data_orders)
                            
                            my_path = system_tools.provide_path_for_file ('ordBook',  instrument_book) 
                            
                            try:
                                pickling.append_and_replace_items_based_on_time_expiration (my_path, data_orders, one_hour)
                            except:
                                continue        
                            
                        symbol_index =  (message_channel)[-7:]
                        if message_channel == f'deribit_price_index.{symbol_index}':
                            
                            my_path = system_tools.provide_path_for_file ('index', symbol_index.lower()) 

                            pickling.replace_data(my_path, data_orders)
                           
                            
                        if message_channel == f'user.orders.future.{currency.upper()}.raw':
                            
                            log.warning (f'{data_orders=}')
                            order_state = data_orders ['order_state']
                            order_id= data_orders ['order_id']
                            
                            my_path_orders_else = system_tools.provide_path_for_file ('orders', currency, order_state)
                            open_orders_open = pickling.read_data (my_path_orders_open) 
                            log.debug (f'{open_orders_open=}')
                            log.warning (f'{order_state=}')
                            
                            if order_state == 'open':
                                log.error ('ORDER_STATE')
                                pickling.append_and_replace_items_based_on_qty (my_path_orders_open, data_orders, 100000)
                            else:
                                log.error ('ORDER_STATE')
                                item_in_open_orders_open_with_same_id =  [o for o in open_orders_open if o['order_id'] == order_id ] 
                                item_in_open_orders_open_with_diff_id =  [o for o in open_orders_open if o['order_id'] != order_id ] 
                                log.info (f'{item_in_open_orders_open_with_same_id=}')
                                log.warning (f'{item_in_open_orders_open_with_diff_id=}')
                                
                                pickling.append_and_replace_items_based_on_qty (my_path_orders_else, data_orders, 100000)
                                
                                if item_in_open_orders_open_with_same_id != []:
                                    log.critical ('item_in_open_orders_open_with_same_id')
                                    pickling.append_and_replace_items_based_on_qty (my_path_orders_else, item_in_open_orders_open_with_same_id[0], 100000)
                                    
                                pickling.replace_data (my_path_orders_open, item_in_open_orders_open_with_diff_id)
                                
                        #open_orders_all: list = pickling.read_data (my_path_orders_open)

                        open_orders_open_byAPI: list = pickling.read_data(my_path_orders_open)
                        open_order_mgt = open_orders_management.MyOrders (open_orders_open_byAPI)
                        #open_orders_byBot: list = open_order_mgt.my_orders_api()
                        
                        #log.error (open_orders_byBot not in none_data)
                        
                        if open_orders_open_byAPI not in none_data :
                            
                            three_minute = one_minute * 3
                            current_time = await deribit_get.get_server_time(self.connection_url)
                            current_server_time = current_time ['result']
                            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
                            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
                            open_orders_deltaTime : int = current_server_time - open_orders_lastUpdateTStamp_min                       

                            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')                        
                            if open_orders_deltaTime > three_minute:
                                await deribit_get.get_cancel_order_byOrderId(self.connection_url, client_id, client_secret, open_order_id)
                                
                        my_trades_path_open = system_tools.provide_path_for_file ('myTrades', currency, 'open')
                        my_trades_path_closed = system_tools.provide_path_for_file ('myTrades', currency, 'closed')
                        
                        label_hedging = 'hedging spot'
                            
                        if message_channel == f'user.trades.future.{currency.upper()}.100ms':                            
                            
                            my_trades_path_manual = system_tools.provide_path_for_file ('myTrades', currency, 'manual')
                            my_trades_open = pickling.read_data(my_trades_path_open)  
                                     
                            log.info (data_orders)
                            log.debug (f'{my_trades_open=}')
                            
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

                            log.debug ('open' in label_id)
                            log.debug ('closed' in label_id)
                            
                            if 'open' in label_id:
                                log.error ('label_id open')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_open, data_orders[0], 100000)
                                
                            if 'closed' in label_id:
                                log.error ('label_id closed')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, data_orders[0], 100000)
                                my_trades_open = pickling.read_data(my_trades_path_open)  
                                remaining_open_trades = ([o for o in my_trades_open if  str(closed_label_id_int)  not in o['label'] ])
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_open, remaining_open_trades[0], 100000)
                                closed_trades = ([o for o in my_trades_open if  str(my_trades_open)  in o['label'] ])
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_closed, closed_trades[0], 100000)
                                
                            if label_id == [] :
                                log.error ('[]')
                                pickling.append_and_replace_items_based_on_qty (my_trades_path_manual, data_orders[0], 100000)
                                
                        my_path_portfolio = system_tools.provide_path_for_file ('portfolio', currency.lower()) 
                                                                                    
                        if message_channel == f'user.portfolio.{currency.lower()}':
                            pickling.replace_data(my_path_portfolio, data_orders)

                        portfolio = pickling.read_data(my_path_portfolio)
                        
                        if  index_price !=[] and portfolio !=[]:
                            
                            equity = portfolio [0]['equity']
                            notional = index_price * equity    
                        
                            spot_was_unhedged = False
                            
                            # refresh myTrades source
                            my_trades_open = pickling.read_data(my_trades_path_open) 
                            #log.warning (f'{my_trades_open=}') 
                            
                            spot_hedged = spot_hedging.SpotHedging (label_hedging,
                                                                    my_trades_open
                                                                    )
                            
                            for instrument in instruments_name:
                                log.warning (f'{instrument}')

                                instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 
                                
                                my_path_ordBook = system_tools.provide_path_for_file ('ordBook', instrument) 
                                
                                ordBook = pickling.read_data(my_path_ordBook)
                                #log.warning (ordBook)
                                
                                if ordBook !=[] :
                                    max_time_stamp_ordBook = max ([o['timestamp'] for o in ordBook ])
                                    most_current_ordBook = [o for o in ordBook if o['timestamp'] == max_time_stamp_ordBook ]

                                    best_bid_prc= most_current_ordBook[0]['bids'][0][0]
                                    best_ask_prc= most_current_ordBook[0]['asks'][0][0]
                                    
                                min_trade_amount = instrument_data ['min_trade_amount']
                                contract_size = instrument_data ['contract_size']
                                    
                                #label_hedging_spot_open: str = 'hedging spot-open'
                                #! CHECK SPOT HEDGING
                                
                                label: str = label_numbering.labelling ('open', 'hedging spot')
                    
                                perpetual = 'PERPETUAL'
                                #log.critical(f'{perpetual in instrument =} { ordBook !=[]=}')

                                # perpetual or other designated instruments
                                if perpetual in instrument and  ordBook !=[] :                                        

                                    check_spot_hedging = spot_hedged.is_spot_hedged_properly (open_orders_open_byAPI, 
                                                                                            notional, 
                                                                                            min_trade_amount,
                                                                                            contract_size
                                                                                            ) 
                                    spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']

                                    spot_was_hedged = spot_was_unhedged == False
                                    actual_hedging_size = spot_hedged.compute_actual_hedging_size ()

                                    label: str = label_numbering.labelling ('open', label_hedging)

                                    log.critical(f'{spot_was_unhedged=} {spot_was_hedged=} {actual_hedging_size=}')
                                    
                                    #check possibility average up/profit realization
                                    if spot_was_hedged and actual_hedging_size != 0:
                                        threshold = 2/100
                                        
                                        myTrades_max_price_plus_threshold = spot_hedged.my_trades_max_price_plus_threshold (threshold, index_price)
                                        log.warning (myTrades_max_price_plus_threshold)
                                        myTrades_max_price_attributes = spot_hedged.my_trades_api_basedOn_label_max_price_attributes ()
                                        myTrades_max_price_attributes_label = myTrades_max_price_attributes ['label']
                                        label_int = string_modification.extract_integers_from_text (myTrades_max_price_attributes_label)
                                        label = f'hedging spot-closed-{label_int}'
                                        open_orders_close =   pickling.read_data(my_trades_path_closed) 
                                        
                                        if myTrades_max_price_plus_threshold ['index_price_higher_than_threshold'] and open_orders_close == []:

                                            await self.send_orders (
                                                                    'sell', 
                                                                    instrument, 
                                                                    best_ask_prc, 
                                                                    myTrades_max_price_attributes ['size'], 
                                                                    label
                                                                    )

                                        if myTrades_max_price_plus_threshold ['index_price_lower_than_threshold'] and open_orders_close ==[]:
                                            
                                            await self.send_orders (
                                                                    'buy', 
                                                                    instrument, 
                                                                    best_bid_prc, 
                                                                    myTrades_max_price_attributes ['size'], 
                                                                    label
                                                                    )

                                    if spot_was_unhedged:
                                        log.warning(f'{instrument=} {best_ask_prc=} {spot_hedged=} {label=}')
                                    
                                        await self.send_orders (
                                                                'sell', 
                                                                instrument, 
                                                                best_ask_prc,
                                                                check_spot_hedging ['hedging_size'], 
                                                                label
                                                                )
                                        
                                        #! synchronize
                                        # refresh, check by independent endpoint
                                        open_orders: list = await self.open_orders (currency)
                                        open_orders_byAPI: list = open_orders.my_orders_api()

                                        if  spot_hedged.is_over_hedged (open_orders_byAPI, check_spot_hedging ['hedging_size']):
                                            open_order_id: list = open_orders.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')
                                            #log.critical (open_orders_hedging_lastUpdate_tStamp_minId)
                                            await deribit_get.get_cancel_order_byOrderId (
                                                                                            self.connection_url, 
                                                                                            client_id, 
                                                                                            client_secret, 
                                                                                            open_order_id
                                                                                            )
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

        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, client_id, client_secret, currency.upper())
        open_ordersREST: list = open_ordersREST ['result']
        open_orders: list = open_orders_management.MyOrders (open_ordersREST)
                        
        return open_orders_management.MyOrders (open_ordersREST)
    
    async def send_orders (self, side: str, instrument: str, prc: float, size: float, label: str = None) -> None:
        """
        """

        try:
            await deribit_get.send_order_limit (
                                            self.connection_url,
                                            client_id, 
                                            client_secret, 
                                            side, 
                                            instrument, 
                                            size, 
                                            prc,
                                            label
                                            )
        except Exception as e:
            log.error (e)
            
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

        strategyDeribit (
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

    
