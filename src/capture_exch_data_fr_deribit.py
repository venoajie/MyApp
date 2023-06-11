#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from datetime import datetime, timedelta
import asyncio
import json

# installed
import websockets
import orjson
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools, string_modification
from configuration import id_numbering, config
from transaction_management.deribit import open_orders_management, myTrades_management
import apply_strategies
from db_management import sqlite_management

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)


class StreamAccountData:

    """

    +----------------------------------------------------------------------------------------------+
    +----------------------------------------------------------------------------------------------+

    """

    def __init__(self, client_id: str, client_secret: str, live=True) -> None:
        # Async Event Loop
        self.loop = asyncio.get_event_loop()

        if not live:
            self.ws_connection_url: str = "wss://test.deribit.com/ws/api/v2"
        elif live:
            self.ws_connection_url: str = "wss://www.deribit.com/ws/api/v2"
        else:
            raise Exception("live must be a bool, True=real, False=paper")

        # Instance Variables
        self.connection_url: str = (
            "https://www.deribit.com/api/v2/"
            if "test" not in self.ws_connection_url
            else "https://test.deribit.com/api/v2/"
        )
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.websocket_client: websockets.WebSocketClientProtocol = None
        self.refresh_token: str = None
        self.refresh_token_expiry_time: int = None

        # Start Primary Coroutine
        self.loop.run_until_complete(self.ws_manager())

    # @lru_cache(maxsize=None)
    async def ws_manager(self) -> None:
        async with websockets.connect(
            self.ws_connection_url,
            ping_interval=None,
            compression=None,
            close_timeout=60,
        ) as self.websocket_client:
            # Authenticate WebSocket Connection
            await self.ws_auth()

            # Establish Heartbeat
            await self.establish_heartbeat()

            # Start Authentication Refresh Task
            self.loop.create_task(self.ws_refresh_auth())

            currencies = ["ETH", "BTC"]
            # for currency in currencies: isu, multiple currency could interfere each other in the calculation function
            currency = "ETH"

            my_path_instruments = system_tools.provide_path_for_file(
                "instruments", currency
            )
            instruments = pickling.read_data(my_path_instruments)
            # instruments_name: list =  [o['instrument_name'] for o in instruments if o['kind'] == 'future']

            self.loop.create_task(
                self.ws_operation(
                    operation="subscribe", ws_channel=f"user.portfolio.{currency}"
                )
            )

            self.loop.create_task(
                self.ws_operation(
                    operation="subscribe",
                    ws_channel=f"user.changes.any.{currency.upper()}.raw",
                )
            )
            while self.websocket_client.open:
                # Receive WebSocket messages
                message: bytes = await self.websocket_client.recv()
                message: dict = orjson.loads(message)
                message_channel: str = None
                # log.warning (message)
                if "id" in list(message):
                    if message["id"] == 9929:
                        syn = apply_strategies.ApplyHedgingSpot(
                            self.connection_url,
                            self.client_id,
                            self.client_secret,
                            currency
                            )

                        if self.refresh_token is None:
                            #await syn.get_sub_accounts()
                            log.debug("Successfully authenticated WebSocket Connection")

                        else:
                            log.info(
                                "Successfully refreshed the authentication of the WebSocket Connection"
                            )

                        self.refresh_token = message["result"]["refresh_token"]

                        # Refresh Authentication well before the required datetime
                        if message["testnet"]:
                            expires_in: int = 300
                        else:
                            expires_in: int = message["result"]["expires_in"] - 240

                        self.refresh_token_expiry_time = datetime.utcnow() + timedelta(
                            seconds=expires_in
                        )

                    elif message["id"] == 8212:
                        # Avoid logging Heartbeat messages
                        continue

                elif "method" in list(message):
                    # Respond to Heartbeat Message
                    if message["method"] == "heartbeat":
                        await self.heartbeat_response()

                if "params" in list(message):
                    if message["method"] != "heartbeat":
                        message_channel = message["params"]["channel"]
                        log.critical (message_channel)

                        data_orders: list = message["params"]["data"]
                        #log.info (data_orders)
                        currency: str = string_modification.extract_currency_from_text(
                            message_channel
                        )

                        if message_channel == f"user.portfolio.{currency.lower()}":
                            my_path_portfolio = system_tools.provide_path_for_file(
                                "portfolio", currency
                            )
                            pickling.replace_data(my_path_portfolio, data_orders)
                            
                        if (
                            message_channel
                            == f"user.changes.any.{currency.upper()}.raw"
                        ):
                            #log.info(data_orders)
                            positions = data_orders["positions"]
                            trades = data_orders["trades"]
                            orders = data_orders["orders"]
                            #private_data = await self.get_private_data(currency)
                            #result_open_orders: dict =  await private_data.get_open_orders_byCurrency()
                            #log.error (result_open_orders)
                            #! ###########################################################
                            open_orders_sqlite = await sqlite_management.executing_label_and_size_query ('orders_all_json')
                            len_open_orders_sqlite_list_data = len([o  for o in open_orders_sqlite])
                            log.warning (f' order sqlite BEFORE {len_open_orders_sqlite_list_data} {open_orders_sqlite}')
                            
                            open_trades_sqlite = await sqlite_management.executing_label_and_size_query ('my_trades_all_json')
                            len_open_trades_sqlite = len([o  for o in open_trades_sqlite])
                            log.debug (f' trade sqlite BEFORE {len_open_trades_sqlite}')
                            #! ###########################################################

                            if trades:
                                for trade in trades:
                                        
                                    log.info (f'trade {trade}')
                                    my_trades = myTrades_management.MyTrades(trade)
                                    
                                    await sqlite_management.insert_tables('my_trades_all_json',trade)
                                    my_trades.distribute_trade_transactions(currency)

                                    #my_trades_path_all = system_tools.provide_path_for_file(
                                    "my_trades", currency, "all"
                                #)
                                #    self. appending_data (trade, my_trades_path_all)

                            if orders:
                                #my_orders = open_orders_management.MyOrders(orders)
                                #log.debug (f'my_orders {my_orders}')
                               
                                for order in orders: 
                                    log.warning (f'order {order}')
                                    #log.error ("trade_seq" not in order)
                                    #log.error ("trade_seq" in order)
                                        
                                    if "trade_seq" not in order:
                                        # get the order state
                                        order_state = order["order_state"]

                                    if "trade_seq" in order:

                                        # get the order state
                                        order_state = order["state"]

                                    log.error (f'ORDER STATE {order_state}')
                                    
                                    if order_state == 'cancelled' \
                                        or order_state == 'filled'\
                                            or order_state == 'triggered':
                                                
                                        #! EXAMPLES of order id state
                                        # untriggered: insert
                                        # {'web': False, 'triggered': False, 'trigger_price': 1874.0, 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'take_limit', 'order_state': 'untriggered', 'order_id': 'ETH-TPTB-5703081', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768062826, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768062826, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}   
                                           
                                        # triggered: cancel untrigger, insert trigger
                                        # {'web': False, 'triggered': True, 'trigger_price': 1874.0, 'trigger_order_id': 'ETH-TPTB-5703081', 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'stop_order_id': 'ETH-TPTB-5703081', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'take_limit', 'order_state': 'triggered', 'order_id': 'ETH-TPTB-5703081', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768062826, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768062826, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}], 'instrument_name': 'ETH-PERPETUAL'}    
                                         
                                        # open: cancel trigger insert open
                                        # {'web': False, 'triggered': True, 'trigger_price': 1874.0, 'trigger_order_id': 'ETH-TPTB-5703081', 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'stop_order_id': 'ETH-TPTB-5703081', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-32754477205', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768064536, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768064536, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}], 'instrument_name': 'ETH-PERPETUAL'}       
                                                
                                        order_id = order["order_id"] if order_state !='triggered' else ["stop_order_id'"]

                                        #open_orders_sqlite =  await syn.querying_all('orders_all_json')
                                        open_orders_sqlite = await sqlite_management.executing_label_and_size_query ('orders_all_json')
                                        #open_orders_sqlite_list_data =  open_orders_sqlite['list_data_only']

                                        is_order_id_in_active_orders = ([o for o in open_orders_sqlite if o['order_id']== order_id])

                                        where_filter = f"order_id"
                                        if is_order_id_in_active_orders== []:
                                            order_id = order["label"] 
                                            where_filter = f"label_main"
                                        
                                        log.critical (f' deleting {order_id}')
                                        await sqlite_management.deleting_row('orders_all_json', 
                                                                            "databases/trading.sqlite3",
                                                                            where_filter,
                                                                            "=",
                                                                            order_id)
                                        
                                    if order_state == 'open' \
                                        or order_state == 'untriggered'\
                                            or order_state == 'triggered':
                                        
                                        await sqlite_management.insert_tables('orders_all_json', order)
                        
                                        #orders_path_all = system_tools.provide_path_for_file(
                                        #orders", currency, "all")
                                        
                                        #self. appending_data (order, orders_path_all)
                                        
                                        #my_orders.distribute_order_transactions(currency)
                            
                            #! ###########################################################
                            open_orders_sqlite = await sqlite_management.executing_label_and_size_query ('orders_all_json')
                            len_open_orders_sqlite_list_data = len([o  for o in open_orders_sqlite])
                            log.critical (f' order sqlite AFTER {len_open_orders_sqlite_list_data} {open_orders_sqlite}')
                            
                            open_trades_sqlite = await sqlite_management.executing_label_and_size_query ('my_trades_all_json')
                            len_open_trades_sqlite = len([o  for o in open_trades_sqlite])
                            log.debug (f' trade sqlite AFTER {len_open_trades_sqlite} ')
                            #! ###########################################################

                            if positions:
                                #log.error (f'positions {positions}')

                                my_path_position = system_tools.provide_path_for_file(
                                    "positions", currency
                                )
                                pickling.replace_data(my_path_position, positions)
                                
            else:
                log.info("WebSocket connection has broken.")
                await system_tools.raise_error_message(
                    "error-WebSocket connection EXCHANGE has broken",
                    0.1,
                    "WebSocket connection EXCHANGE has broken",
                )
                
    async def get_private_data(self, currency) -> list:
        """
        Provide class object to access private get API
        """
        import deribit_get
        
        return deribit_get.GetPrivateData(
                self.connection_url, self.client_id, self.client_secret, currency
            )

    async def deleting_cancel_order(self, table: list, 
                           database: str ,
                           data,
                           cancelled_order
                           ) -> list:
        """ """
        result = await sqlite_management.deleting_row (table, 
                                                         database,
                                                         data,
                                                         '=',
                                                         cancelled_order
                                                         ) 
        return  (result)   
    
    def appending_data(self, data: dict, my_path_all: str) -> None:
        """
        """
        
        if isinstance(data, list):
            for dt in data:
                pickling.append_data(my_path_all, dt, True)
        else:
            pickling.append_data(my_path_all, data, True)

    async def establish_heartbeat(self) -> None:
        """
        Requests DBT's `public/set_heartbeat` to
        establish a heartbeat connection.
        """
        msg: dict = {
            "jsonrpc": "2.0",
            "id": 9098,
            "method": "public/set_heartbeat",
            "params": {"interval": 10},
        }

        try:
            await self.websocket_client.send(json.dumps(msg))
        except Exception as error:
            log.warning(error)

    async def heartbeat_response(self) -> None:
        """
        Sends the required WebSocket response to
        the Deribit API Heartbeat message.
        """
        msg: dict = {
            "jsonrpc": "2.0",
            "id": 8212,
            "method": "public/test",
            "params": {},
        }

        try:
            await self.websocket_client.send(json.dumps(msg))

        except Exception as error:
            log.warning(error)

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
                "client_secret": self.client_secret,
            },
        }

        await self.websocket_client.send(json.dumps(msg))

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
                            "refresh_token": self.refresh_token,
                        },
                    }

                    await self.websocket_client.send(json.dumps(msg))

            await asyncio.sleep(150)

    async def ws_operation(
        self, operation: str, ws_channel: str, id: int = 100
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
            "params": {"channels": [ws_channel]},
        }

        log.warning(msg)
        await self.websocket_client.send(json.dumps(msg))

def main():
    sub_account = "deribit-147691"
    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]

    try:
        StreamAccountData(client_id=client_id, client_secret=client_secret)

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save EXCHANGE data from deribit"
        )

if __name__ == "__main__":
    try:
        main()

    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save EXCHANGE data from deribit"
        )
