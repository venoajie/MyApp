# built ins
import asyncio
from datetime import datetime
from typing import Dict

# installed
from dataclassy import dataclass 

# import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from loguru import logger as log

# user defined formula
from configuration import id_numbering, config
from db_management import sqlite_management
from utilities import time_modification



def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


def get_now_unix() -> int:

    now_utc = datetime.now()
    
    return time_modification.convert_time_to_unix(now_utc)

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

    return await main(endpoint=endpoint, params={}, connection_url=connection_url)

async def main (sub_account: str,
                endpoint: str,
                params: str,
                connection_url: str = "https://www.deribit.com/api/v2/",
                ) -> None:

    id = id_numbering.id(endpoint, endpoint)
    
    payload: Dict = {
        "jsonrpc": "2.0",
        "id": id,
        "method": f"{endpoint}",
        "params": params,
    }

    try:
        
        client_id =  parse_dotenv(sub_account)["client_id"]
        client_secret =  parse_dotenv(sub_account)["client_secret"]
        
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
        
    except:

        async with aiohttp.ClientSession() as session:
            async with session.get(connection_url + endpoint) as response:

                # RESToverHTTP Response Content
                response: Dict = await response.json()

            return response

async def public_connection (endpoint: str,
                             connection_url: str = "https://www.deribit.com/api/v2/",
                             ) -> None:


    async with aiohttp.ClientSession() as session:
        async with session.get(connection_url + endpoint) as response:

            # RESToverHTTP Response Content
            response: Dict = await response.json()

        return response

async def get_currencies(connection_url: str) -> list:
    # Set endpoint
    endpoint: str = f"public/get_currencies?"

    return await public_connection(endpoint=endpoint)


async def get_server_time() -> int:
    """
    Returning server time
    """
    # Set endpoint
    endpoint: str = "public/get_time?"


    # Get result
    result = await public_connection(endpoint=endpoint)

    return result

async def get_instruments(currency):
    # Set endpoint
    endpoint: str = f"public/get_instruments?currency={currency.upper()}"
    
    return await public_connection (endpoint=endpoint)

def get_tickers(instrument_name: str) -> list:
    # Set endpoint
    
    import requests, json
    
    return requests.get(f"https://deribit.com/api/v2/public/ticker?instrument_name={instrument_name}").json()["result"] 

@dataclass(unsafe_hash=True, slots=True)
class SendApiRequest:
    """ """

    sub_account: str
    currency: str
    
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
            result = await main (self.sub_account,
                                 endpoint=endpoint, 
                                 params=params,
                                 )
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

        #log.info(
        #    f"""params {params}"""
        #)
        if side != None:
            order_result = await self.send_order(
                side,
                instrument,
                size,
                label_numbered,
                limit_prc,
                type,
            )

        log.warning(f'order_result {order_result}')

        if order_result != None and ("error" in order_result):
            error = order_result ["error"]
            message = error ["message"]
            data = error ["data"]
            await telegram_bot_sendtext(f"message: {message}, data: ({data}), (params: {params})")
    
    async def get_subaccounts(self):
        # Set endpoint
        endpoint: str = "private/get_subaccounts_details"

        params = {"currency": self.currency, 
                  "with_open_orders": True
                  }
    
        return await main (self.sub_account,
                           endpoint=endpoint, 
                           params=params,
                           )


    async def get_cancel_order_all(self):
        

        # Set endpoint
        endpoint: str = "private/cancel_all"

        params = {"detailed": False}

        result = await main(self.sub_account,
                           endpoint=endpoint, 
                           params=params,
                           )
        await sqlite_management.deleting_row("orders_all_json")

        return result


    async def get_transaction_log(
        self,
        start_timestamp: int,
        count: int = 1000,
    ) -> list:
        
        now_unix = get_now_unix()

        # Set endpoint
        endpoint: str = f"private/get_transaction_log"
        params = {
            "count": count,
            "currency": self.currency.upper(),
            "end_timestamp": now_unix,
            "start_timestamp": start_timestamp,
        }

        return await main (self.sub_account,
                           endpoint=endpoint, 
                           params=params,
                           )
