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

import apply_strategies
from db_management import sqlite_management
import ws_management   


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
        
            instruments_raw = pickling.read_data(my_path_instruments)
            instruments = instruments_raw[0]["result"]

            instruments_kind: list = [
                o for o in instruments if o["kind"] == "future"
            ]

            instruments_name: list = [
                o["instrument_name"] for o in instruments_kind
            ]
            # instruments_name: list =  [o['instrument_name'] for o in instruments if o['kind'] == 'future']

            for instrument in instruments_name:

                self.loop.create_task(
                    self.ws_operation(
                        operation="subscribe",
                        ws_channel=f"incremental_ticker.{instrument}",
                    )
                )

                if "PERPETUAL" in instrument:
                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"chart.trades.{instrument}.1",
                        )
                    )
                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"chart.trades.{instrument}.30",
                        )
                    )
                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"chart.trades.{instrument}.60",
                        )
                    )
                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"chart.trades.{instrument}.1D",
                        )
                    )
                    
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
                            currency,
                        )

                        if self.refresh_token is None:
                            # await syn.get_sub_accounts()
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
                        log.critical(message_channel)

                        data_orders: list = message["params"]["data"]
                        log.info(data_orders)
                        currency: str = string_modification.extract_currency_from_text(
                            message_channel
                        )
                        #! ########################################################################################################################
                        await ws_management.ws_manager_market (message_channel, data_orders, instruments_kind, currency, self.websocket_client)
                        await ws_management.ws_manager_exchange (message_channel, data_orders, currency)

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

    async def deleting_cancel_order(
        self, table: list, database: str, data, cancelled_order
    ) -> list:
        """ """
        result = await sqlite_management.deleting_row(
            table, database, data, "=", cancelled_order
        )
        return result

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
            "method": f"private/{operation}",
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
