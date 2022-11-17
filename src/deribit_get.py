"""
Description:
    Deribit RESToverHTTP [POST] Asyncio Example.
    - Authenticated request.
Usage:
    python3.9 dbt-post-authenticated-example.py
Requirements:
    - aiohttp >= 3.8.1
"""

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


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


async def main(
    endpoint: str,
    params: str,
    client_id: str,
    client_secret: str,
        ) -> None:

    # DBT LIVE RESToverHTTP Connection URL
    # connection_url: str = 'https://www.deribit.com/api/v2/'
    # DBT TEST RESToverHTTP Connection URL
    connection_url: str = 'https://test.deribit.com/api/v2/'

    # DBT [POST] RESToverHTTP Payload
    payload: Dict = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": f"{endpoint}",
                    "params": params
                    }    

    async with aiohttp.ClientSession() as session:
        async with session.post(
            connection_url+endpoint,
            auth=BasicAuth(client_id, client_secret),
            json=payload
                ) as response:
            # RESToverHTTP Status Code
            status_code: int = response.status

            # RESToverHTTP Response Content
            response: Dict = await response.json()
            logging.info(f'Response Content: {response}')

def send_order (client_id, client_secret, endpoint, instrument, type, amount, label: str =None):
        
    params =  {
                "instrument_name": instrument,
                "amount": amount,
                "type": type,
                "label": label
                }
    
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
        )
async def get_position (client_id, client_secret, endpoint, currency):
        
    params =  {
                "currency": currency
                }
    
    return await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
        
def get_position_ (client_id, client_secret, endpoint, currency):
        
    params =  {
                "currency": currency
                }
    
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
        )

if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level='INFO'.upper(),
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )

    # DBT RESToverHTTP Endpoint + Query String Parameter(s)
    endpoint: str = 'private/buy'

    # DBT Client ID
    client_id: str = os.environ.get("client_id")
    # DBT Client Secret
    client_secret: str = os.environ.get("client_secret")
    send_order(client_id, client_secret, endpoint, "ETH-PERPETUAL", 'market', 10,)

    endpoint: str = 'private/get_positions'
    get_position(client_id, client_secret, endpoint, "ETH")
    