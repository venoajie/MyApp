# built ins
import asyncio
from typing import Dict

# installed
from dataclassy import dataclass 

# import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from loguru import logger as log

# user defined formula
from configuration import id_numbering, config

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


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


@dataclass(unsafe_hash=True, slots=True)
class SendApiRequest:
    """ """

    sub_account: str
    currency: str
    

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
