#!/usr/bin/python3
# -*- coding: utf-8 -*-

# built ins
from datetime import datetime, timedelta
import json

# installed
import websockets
import asyncio
import orjson
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools, string_modification
from configuration import id_numbering
from market_understanding import futures_analysis
from db_management import sqlite_management

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

class StreamMarketData:

    """

    +----------------------------------------------------------------------------------------------+
    #  References:
        + https://github.com/ElliotP123/crypto-exchange-code-samples/blob/master/deribit/websockets/dbt-ws-authenticated-example.py
    +----------------------------------------------------------------------------------------------+

    """

    def __init__(self, live=True) -> None:
        # Async Event Loop
        self.loop = (
            asyncio.get_event_loop()
        )  # https://stackoverflow.com/questions/65206110/when-to-use-asyncio-get-running-loop-or-asyncio-get-event-loop-in-python

        # Instance Variables

        if not live:
            self.ws_connection_url: str = "wss://test.deribit.com/ws/api/v2"
        elif live:
            self.ws_connection_url: str = "wss://www.deribit.com/ws/api/v2"
        else:
            raise Exception("live must be a bool, True=real, False=paper")

        self.connection_url: str = (
            "https://www.deribit.com/api/v2/"
            if "test" not in self.ws_connection_url
            else "https://test.deribit.com/api/v2/"
        )

        self.websocket_client: websockets.WebSocketClientProtocol = None
        self.refresh_token: str = None
        self.refresh_token_expiry_time: int = None

        # Start Primary Coroutine
        self.loop.run_until_complete(self.ws_manager())

    async def ws_manager(self) -> None:
        async with websockets.connect(
            self.ws_connection_url,
            ping_interval=None,
            compression=None,
            close_timeout=60,
        ) as self.websocket_client:
            try:

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
                instruments_raw = pickling.read_data(my_path_instruments)
                instruments = instruments_raw [0] ['result']

                instruments_kind: list = [o for o in instruments if o["kind"] == "future"]
                instruments_name: list = [o["instrument_name"] for o in instruments_kind]

                for instrument in instruments_name:

                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"incremental_ticker.{instrument}",
                        )
                    )

                    if 'PERPETUAL' in instrument:
                        self.loop.create_task(
                            self.ws_operation(
                                operation="subscribe",
                                ws_channel=f"chart.trades.{instrument}.1",
                        )
                    )

                while self.websocket_client.open:
                    # Receive WebSocket messages
                    message: bytes = await self.websocket_client.recv()
                    message: dict = orjson.loads(message)
                    message_channel: str = None
                    #log.warning(message)
                    if "id" in list(message):
                        if message["id"] == 9929:
                            if self.refresh_token is None:
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
                            #log.info (message_channel)

                            # one_minute: int = 60000
                            data_orders: list = message["params"]["data"]
                            #log.debug(data_orders)
                            currency: str = string_modification.extract_currency_from_text(
                                message_channel
                            )
                            
                            if message_channel == "chart.trades.ETH-PERPETUAL.1":
                                
                                last_tick_fr_sqlite= await sqlite_management.get_min_max_tick()
                                last_tick_fr_data_orders= data_orders['tick']
                                
                                if last_tick_fr_sqlite== None:
                                    from utilities import time_modification
                                    import requests
        
                                    resolution=1
                                    qty_candles=1
                                    now_utc = datetime.now()
                                    now_unix = time_modification.convert_time_to_unix (now_utc)
                                    start_timestamp = now_unix - 60000 * qty_candles
                                    
                                    ohlc_endPoint=  (f' https://deribit.com/api/v2/public/get_tradingview_chart_data?end_timestamp={now_unix}&instrument_name=ETH-PERPETUAL&resolution={resolution}&start_timestamp={start_timestamp}')
                                    try:            

                                        ohlc_request= requests.get(ohlc_endPoint).json()['result']
                                        log.warning (ohlc_request)
                                        result ={}
                                        
                                        for data in ohlc_request:
                                            item_data= ohlc_request[data]
                                            len_item_data= len(item_data)
                                            log.error (data)
                                            log.error (item_data)
                                            log.error (len_item_data)
                                            await sqlite_management.insert_tables('ohlc1_eth_perp_json',data)

                                    except Exception as error:
                                        system_tools.catch_error_message(error, 10,"WebSocket connection - failed to get ohlc",)
                                    
                                if last_tick_fr_sqlite!= None \
                                    and last_tick_fr_sqlite== last_tick_fr_data_orders:
                                        
                                    where_filter = f"tick"
                                    
                                    await sqlite_management.deleting_row('ohlc1_eth_perp_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            last_tick_fr_sqlite)
                                    
                                await sqlite_management.insert_tables('ohlc1_eth_perp_json',data_orders)

                            instrument_ticker = (message_channel)[19:]
                            if message_channel == f"incremental_ticker.{instrument_ticker}":
                                my_path_futures_analysis = system_tools.provide_path_for_file(
                                    "futures_analysis", currency
                                )
                                my_path_ticker = system_tools.provide_path_for_file(
                                    "ticker", instrument_ticker
                                )
                                try:
                                    await self.distribute_ticker_result_as_per_data_type(
                                        my_path_ticker, data_orders, instrument_ticker
                                    )

                                    symbol_index: str = f"{currency}_usd"
                                    my_path_index: str = system_tools.provide_path_for_file(
                                        "index", symbol_index
                                    )
                                    index_price: list = pickling.read_data(my_path_index)
                                    ticker_instrument: list = pickling.read_data(
                                        my_path_ticker
                                    )
                                    if ticker_instrument != []:
                                        # log.error(ticker_instrument)
                                        instrument_name = ticker_instrument[0][
                                            "instrument_name"
                                        ]
                                        instrument: list = [
                                            o
                                            for o in instruments_kind
                                            if o["instrument_name"] == instrument_name
                                        ][0]

                                        # combine analysis of each instrument futures result
                                        tickers = futures_analysis.combining_individual_futures_analysis(
                                            index_price[0]["price"],
                                            instrument,
                                            ticker_instrument[0],
                                        )
                                        ticker_all: list = pickling.read_data(
                                            my_path_futures_analysis
                                        )

                                        if ticker_all == None:
                                            pickling.replace_data(
                                                my_path_futures_analysis, ticker_all
                                            )
                                        else:
                                            ticker_all: list = [
                                                o
                                                for o in ticker_all
                                                if o["instrument_name"] != instrument_ticker
                                            ]

                                            #! double file operation. could be further improved
                                            pickling.replace_data(
                                                my_path_futures_analysis, ticker_all
                                            )

                                            pickling.append_and_replace_items_based_on_qty(
                                                my_path_futures_analysis, tickers, 100
                                            )

                                except Exception as error:
                                    system_tools.catch_error_message(error)
                                    system_tools.catch_error_message(
                                        "WebSocket connection - failed to process data"
                                    )

                                    continue

                else:
                    log.info("WebSocket connection has broken.")
                    system_tools.catch_error_message(
                        error, 0.1, "WebSocket connection MARKET has broken"
                    )

            except Exception as error:
                system_tools.catch_error_message(
                    error, 10,
                    "WebSocket connection - failed to capture market data from Deribit",
                )

    async def distribute_ticker_result_as_per_data_type(
        self, my_path_ticker, data_orders, instrument
    ) -> None:
        """ """

        try:
            # ticker: list = pickling.read_data(my_path_ticker)

            if data_orders["type"] == "snapshot":
                pickling.replace_data(my_path_ticker, data_orders)

                # ticker_fr_snapshot: list = pickling.read_data(my_path_ticker)

            else:
                ticker_change: list = pickling.read_data(my_path_ticker)
                if ticker_change != []:
                    # log.debug (ticker_change)

                    for item in data_orders:
                        ticker_change[0][item] = data_orders[item]
                        pickling.replace_data(my_path_ticker, ticker_change)
                        
        except Exception as error:
            system_tools.catch_error_message(
                error,
                "WebSocket connection - failed to distribute_incremental_ticker_result_as_per_data_type",
            )

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
    try:
        StreamMarketData()

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save MARKET data from deribit"
        )

if __name__ == "__main__":
    try:
        main()

    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        system_tools.catch_error_message(
            error, 10, "fetch and save MARKET data from deribit"
        )
