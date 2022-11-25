
# built ins
import asyncio
import logging
from typing import Dict
import os

# installed
import aiohttp
from aiohttp.helpers import BasicAuth
from dotenv import load_dotenv
from os.path import join, dirname
from dataclassy import dataclass
from loguru import logger as log
# user defined formula

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


async def main(
    endpoint: str,
        ) -> None:

    connection_url: str = 'https://open-api.coinglass.com/public/v2/'
    
    headers: Dict = {
            "accept": "application/json",
            "coinglassSecret": "877ad9af931048aab7e468bda134942e"
        }  


    async with aiohttp.ClientSession() as session:
        async with session.post(
            connection_url+endpoint,
            json=headers
                ) as response:
            # RESToverHTTP Status Code
            status_code: int = response.status

            # RESToverHTTP Response Content
            response: Dict = await response.json()
            log.warning (connection_url+endpoint)
            log.warning (headers)
            log.warning (response)
        return response

def  open_interest_symbol (endpoint):
    
    log.error (endpoint)

    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            endpoint=endpoint,
            )
        )

if __name__ == "__main__":

    endpoint: str = 'open_interest?symbol=BTC'
    result = open_interest_symbol(endpoint)
    log.debug (result)
