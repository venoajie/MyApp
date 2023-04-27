# built ins
import asyncio
from typing import Dict

# installed
from dataclassy import dataclass  # import websockets

# import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from loguru import logger as log
# user defined formula
from configuration import id_numbering, config

headers = {
    "accept": "application/json",
    "coinglassSecret": "877ad9af931048aab7e468bda134942e",
}

async def telegram_bot_sendtext(
    bot_message: str, purpose: str = "general_error"
) -> str:
    """
    # simple telegram
    #https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
    """

    try:
        bot_token = config.main_dotenv("telegram-failed_order")["bot_token"]

    except:
        bot_token = config.main_dotenv("telegram-failed_order")["BOT_TOKEN"]

    if purpose == "failed_order":
        try:
            try:
                bot_chatID = config.main_dotenv("telegram-failed_order")[
                "BOT_CHATID_FAILED_ORDER"
            ]
            except:
                bot_chatID = config.main_dotenv("telegram-failed_order")["bot_chatID"]
        except:
            bot_chatID = config.main_dotenv("telegram-failed_order")["bot_chatid"]

    if purpose == "general_error":
        try:
            try:
                bot_chatID = config.main_dotenv("telegram-general_error")["bot_chatid"]
            except:
                bot_chatID = config.main_dotenv("telegram-general_error")["bot_chatID"]
        except:
            bot_chatID = config.main_dotenv("telegram-general_error")[
                "BOT_CHATID_GENERAL_ERROR"
                ]
            
    connection_url = "https://api.telegram.org/bot"
    
    endpoint = (
        bot_token
        + ("/sendMessage?chat_id=")
        + bot_chatID
        + ("&parse_mode=HTML&text=")
        + bot_message
    )

    try:
        return await main(endpoint=endpoint, params={}, connection_url=connection_url)

    except:
        return await main(
            endpoint=endpoint, params=params_coinGlass, connection_url=connection_url
        )

async def main_coinGlass() -> None:
        
    session = aiohttp.ClientSession()
        
    symbol = 'BTC'
    currency = 'USD'
    headers = {
"accept": "application/json",
"coinglassSecret": "877ad9af931048aab7e468bda134942e",
}
    url = f"https://open-api.coinglass.com/public/v2/?symbol={symbol}&time_type=all&currency={currency}"
                    
    print (url)
    print (headers)
    async with session.get(
        url,headers=headers 
    ) as response:
        print(await response.text())
        # RESToverHTTP Status Code
        status_code: int = response.status

        # RESToverHTTP Response Content
        response: Dict = await response.json()

    return response

        
async def main(
    endpoint: str,
    params: str,
    connection_url: str,
    client_id: str = None,
    client_secret: str = None,
) -> None:
    
    id = id_numbering.id(endpoint, endpoint)

    payload: Dict = {
        "jsonrpc": "2.0",
        "id": id,
        "method": f"{endpoint}",
        "params": params,
    }
    
    if 'open_interest_history' in endpoint :
        
        async with aiohttp.ClientSession() as session:
            
            symbol = 'BTC'
            currency = 'USD'
            url = f"https://open-api.coinglass.com/public/v2/?symbol={symbol}&time_type=all&currency={currency}"
            headers = {
    "accept": "application/json",
    "coinglassSecret": "877ad9af931048aab7e468bda134942e",
}
                            
            print (connection_url + endpoint)
            async with session.get(
                url,headers=headers 
            ) as response:
                # RESToverHTTP Status Code
                status_code: int = response.status

                # RESToverHTTP Response Content
                response: Dict = await response.json()

            return response
        
    if client_id == None:
        async with aiohttp.ClientSession() as session:
            async with session.get(connection_url + endpoint) as response:
                # RESToverHTTP Status Code
                status_code: int = response.status

                # RESToverHTTP Response Content
                response: Dict = await response.json()

            return response

    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                connection_url + endpoint,
                auth=BasicAuth(client_id, client_secret),
                json=payload,
            ) as response:
                # RESToverHTTP Status Code
                status_code: int = response.status

                # RESToverHTTP Response Content
                response: Dict = await response.json()

            return response


@dataclass(unsafe_hash=True, slots=True)
class GetPrivateData:

    """ """

    connection_url: str
    client_id: str
    client_secret: str
    currency: str

    async def parse_main(self, endpoint: str, params: dict):
        result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=self.connection_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        return result

    async def get_subaccounts(self):
        # Set endpoint
        endpoint: str = "private/get_subaccounts_details"

        params = {"currency": self.currency, "with_open_orders": True}
        log.error ('get_subaccounts')

        return await self.parse_main(endpoint=endpoint, params=params)

    async def get_account_summary(self):
        params = {"currency": self.currency, "extended": True}
        log.error ('get_account_summary')

        # Set endpoint
        endpoint: str = "private/get_account_summary"

        return await self.parse_main(endpoint=endpoint, params=params)

    async def get_positions(self):
        
        # Set endpoint
        endpoint: str = "private/get_positions"
        log.error ('get_positions')

        params = {"currency": self.currency}

        return await self.parse_main(endpoint=endpoint, params=params)

    async def get_open_orders_byCurrency(self) -> list:
        params = {"currency": self.currency}

        # Set endpoint
        endpoint: str = f"private/get_open_orders_by_currency"

        return await self.parse_main(endpoint=endpoint, params=params)

    async def get_user_trades_by_currency_and_time(
        self,
        start_timestamp: int,
        end_timestamp: int,
        count: int = 1000,
        include_old: bool = True,
    ) -> list:
        
        # Set endpoint
        endpoint: str = f"private/get_user_trades_by_currency_and_time"

        params = {
            "currency": self.currency.upper(),
            "kind": "any",
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "count": count,
            "include_old": include_old,
        }

        return await self.parse_main(endpoint=endpoint, params=params)

    async def get_user_trades_by_currency(self, count: int = 1000) -> list:
        
        # Set endpoint
        endpoint: str = f"private/get_user_trades_by_currency"

        params = {"currency": self.currency.upper(), "kind": "any", "count": count}

        return await self.parse_main(endpoint=endpoint, params=params)

    async def edit_order(
        self,
        instrument,
        order_id,
        amount,
        label: str = None,
        price: float = None,
        trigger_price: float = None,
        trigger: str = "last_price",
        time_in_force: str = "fill_or_kill",
        reduce_only: bool = False,
        valid_until: int = False,
        post_only: bool = True,
        reject_post_only: bool = False,
    ):
        if valid_until == False:
            if trigger_price == None:
                if "market" in type:
                    params = {
                        "instrument_name": instrument,
                        "order_id": order_id,
                        "amount": amount,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "reduce_only": reduce_only,
                    }
                else:
                    params = {
                        "instrument_name": instrument,
                        "order_id": order_id,
                        "amount": amount,
                        "price": price,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "reduce_only": reduce_only,
                        "post_only": post_only,
                        "reject_post_only": reject_post_only,
                    }
            else:
                if "market" in type:
                    params = {
                        "instrument_name": instrument,
                        "order_id": order_id,
                        "amount": amount,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "trigger": trigger,
                        "trigger_price": trigger_price,
                        "reduce_only": reduce_only,
                    }
                else:
                    params = {
                        "instrument_name": instrument,
                        "order_id": order_id,
                        "amount": amount,
                        "price": price,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "trigger": trigger,
                        "trigger_price": trigger_price,
                        "reduce_only": reduce_only,
                        "post_only": post_only,
                        "reject_post_only": reject_post_only,
                    }
        else:
            params = {
                "instrument_name": instrument,
                "order_id": order_id,
                "amount": amount,
                "price": price,
                "valid_until": valid_until,
                # "time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only,
            }

        endpoint: str = "edit"

        result = await self.parse_main(endpoint=endpoint, params=params)
        return result

    async def send_order(
        self,
        side: str,
        instrument,
        amount,
        label: str = None,
        price: float = None,
        type: str = "limit",
        trigger_price: float = None,
        trigger: str = "last_price",
        time_in_force: str = "fill_or_kill",
        reduce_only: bool = False,
        valid_until: int = False,
        post_only: bool = True,
        reject_post_only: bool = False,
    ):

        if valid_until == False:
            if trigger_price == None:
                if "market" in type:
                    params = {
                        "instrument_name": instrument,
                        "amount": amount,
                        "label": label,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "type": type,
                        "reduce_only": reduce_only,
                    }
                else:
                    params = {
                        "instrument_name": instrument,
                        "amount": amount,
                        "label": label,
                        "price": price,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "type": type,
                        "reduce_only": reduce_only,
                        "post_only": post_only,
                        "reject_post_only": reject_post_only,
                    }
            else:
                if "market" in type:
                    params = {
                        "instrument_name": instrument,
                        "amount": amount,
                        "label": label,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "type": type,
                        "trigger": trigger,
                        "trigger_price": trigger_price,
                        "reduce_only": reduce_only,
                    }
                else:

                    params = {
                        "instrument_name": instrument,
                        "amount": amount,
                        "label": label,
                        "price": price,
                        # "time_in_force": time_in_force, fik can not apply to post only
                        "type": type,
                        "trigger": trigger,
                        "trigger_price": trigger_price,
                        "reduce_only": reduce_only,
                        "post_only": post_only,
                        "reject_post_only": reject_post_only,
                    }
        else:
            params = {
                "instrument_name": instrument,
                "amount": amount,
                "price": price,
                "label": label,
                "valid_until": valid_until,
                # "time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only,
            }

        result = None
        if side == "buy":
            endpoint: str = "private/buy"
        if side == "sell":
            endpoint: str = "private/sell"
        if side != None:
            result = await self.parse_main(endpoint=endpoint, params=params)
        return result

    async def send_limit_order(self, params) -> None:
        """ """
        from loguru import logger as log

        side = params["side"]
        instrument = params["instrument"]
        label_numbered = params["label"]
        size = params["size"]
        try:
            limit_prc = params["take_profit_usd"]
        except:
            limit_prc = params["entry_price"]
        type = params["type"]

        order_result = None

        if side != None:
            order_result = await self.send_order(
                side, instrument, size, label_numbered, limit_prc, type,
            )

        log.warning(f'side {side} instrument {instrument} label_numbered {label_numbered} size {size} type {type} limit_prc {limit_prc}')
        log.info(order_result)

        if order_result != None and "error" in order_result:
            await telegram_bot_sendtext("limit order failed")

    async def send_market_order(self, params) -> None:
        """ """
        from loguru import logger as log

        side = params["side"]
        type = params["type"]
        instrument = params["instrument"]
        label = params["label"]
        size = params["size"]
        cut_loss_usd = params["cut_loss_usd"]

        order_result = None
        if size != 0:
            order_result = await self.send_order(
                side, instrument, size, label, None, type, cut_loss_usd
            )
        log.info(order_result)

        if order_result != None and "error" in order_result:
            await telegram_bot_sendtext("market order failed")

    async def send_triple_orders(self, params) -> None:
        """
        triple orders:
            1 limit order
            1 SL market order
            1 TP limit order
        """
        from loguru import logger as log

        main_side = params["side"]
        instrument = params["instrument"]
        main_label = params["label_numbered"]
        closed_label = params["label_closed_numbered"]
        size = params["size"]
        main_prc = params["entry_price"]
        sl_prc = params["cut_loss_usd"]
        tp_prc = params["take_profit_usd"]

        order_result = await self.send_order(
            main_side, instrument, size, main_label, main_prc
        )
        log.info(order_result)

        order_result_id = order_result["result"]["order"]["order_id"]

        if "error" in order_result:
            await self.get_cancel_order_byOrderId(order_result_id)
            await telegram_bot_sendtext("combo order failed")
        else:
            if main_side == "buy":
                closed_side = "sell"
                trigger_prc = tp_prc - 1
            if main_side == "sell":
                closed_side = "buy"
                trigger_prc = tp_prc + 1

            order_result = await self.send_order(
                closed_side, instrument, size, closed_label, None, "stop_market", sl_prc
            )
            log.info(order_result)

            if "error" in order_result:
                await self.get_cancel_order_byOrderId(order_result_id)
                await telegram_bot_sendtext("combo order failed")

            order_result = await self.send_order(
                closed_side,
                instrument,
                size,
                closed_label,
                tp_prc,
                "take_limit",
                trigger_prc,
            )
            log.info(order_result)

            if "error" in order_result:
                await self.get_cancel_order_byOrderId(order_result_id)
                await telegram_bot_sendtext("combo order failed")

    async def get_cancel_order_byOrderId(self, order_id: int):
        # Set endpoint
        endpoint: str = "private/cancel"

        params = {"order_id": order_id}

        result = await self.parse_main(endpoint=endpoint, params=params)
        return result

async def send_order_market(
    connection_url: str,
    client_id,
    client_secret,
    side: str,
    instrument,
    amount,
    label: str,
    type: str = "market",
    time_in_force: str = "fill_or_kill",
    trigger: str = "last_price",
    trigger_price: float = None,
    reduce_only: bool = False,
    valid_until: int = False,
    post_only: bool = True,
    reject_post_only: bool = False,
):
    if valid_until == False:
        if trigger_price == None:
            params = {
                "instrument_name": instrument,
                "amount": amount,
                "label": label,
                # "time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only,
            }
        else:
            params = {
                "instrument_name": instrument,
                "amount": amount,
                "label": label,
                # "time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "trigger": trigger,
                "trigger_price": trigger_price,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only,
            }
    else:
        params = {
            "instrument_name": instrument,
            "amount": amount,
            "label": label,
            "valid_until": valid_until,
            # "time_in_force": time_in_force, fik can not apply to post only
            "type": type,
            "reduce_only": reduce_only,
            "post_only": post_only,
            "reject_post_only": reject_post_only,
        }

    # Set endpoint based on side
    if side == "buy":
        endpoint: str = "private/buy"
    if side == "sell":
        endpoint: str = "private/sell"

    result = await main(
        endpoint=endpoint,
        params=params,
        connection_url=connection_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    return result

async def get_server_time(connection_url: str) -> int:
    """
    Returning server time
    """
    # Set endpoint
    endpoint: str = "public/get_time?"

    # Set the parameters
    params = {}

    # Get result
    result = await main(endpoint=endpoint, params=params, connection_url=connection_url)

    return result

async def get_instruments(connection_url: str, currency):
    # Set endpoint
    endpoint: str = f"public/get_instruments?currency={currency.upper()}"
    params = {}

    return await main(endpoint=endpoint, params=params, connection_url=connection_url)

async def get_currencies(connection_url: str) -> list:
    # Set endpoint
    endpoint: str = f"public/get_currencies?"
    params = {}

    return await main(endpoint=endpoint, params=params, connection_url=connection_url)

async def get_ohlc(
    connection_url: str, instrument_name, resolution, qty_candles,
) -> list:
    from datetime import datetime
    from utilities import time_modification

    now_utc = datetime.now()
    now_unix = time_modification.convert_time_to_unix(now_utc)
    start_timestamp = now_unix - 60000 * qty_candles
    params = {}

    # Set endpoint
    endpoint: str = f"public/get_tradingview_chart_data?end_timestamp={now_unix}&instrument_name={instrument_name.upper()}&resolution={resolution}&start_timestamp={start_timestamp}"

    return await main(endpoint=endpoint, params=params, connection_url=connection_url)

async def get_open_interest_aggregated_ohlc(
    connection_url: str, currency, resolution
) -> list:
    """
    interval = m1 m5 m15 h1 h4 h12 all

    """
    # Set endpoint
    endpoint: str = f"indicator/open_interest_aggregated_ohlc?symbol={currency}&interval={resolution}"

    return await main(
            endpoint=endpoint, params=headers, connection_url=connection_url
        )

async def get_open_interest_historical() -> list:
    """
    time_frame = m1 m5 m15 h1 h4 h12 all
    currency = USD or symbol

    """
    
    symbol = 'BTC'
    currency = 'USD'
    resolution ='all'
    # Set endpoint
    url: str = f"https://open-api.coinglass.com/public/v2/?symbol={symbol}&time_type=all&currency={currency}"

    return await main_coinGlass()

async def get_open_interest_symbol(connection_url: str, currency) -> list:
    # Set endpoint
    endpoint: str = f"open_interest?symbol={currency}"
    return await main(
            endpoint=endpoint, params=headers, connection_url=connection_url
        )
