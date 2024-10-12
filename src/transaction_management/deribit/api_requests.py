# built ins
import asyncio
from typing import Dict

# installed
from dataclassy import dataclass, fields 

# import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from loguru import logger as log

# user defined formula
from configuration import id_numbering, config

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


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

    if client_id:
        
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
        
    else:

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
    
    
    async def get_subaccounts(self):
        # Set endpoint
        endpoint: str = "private/get_subaccounts_details"

        params = {"currency": self.currency, "with_open_orders": True}
    
        return await main(self.sub_account,
                               endpoint=endpoint, 
                               params=params,)
