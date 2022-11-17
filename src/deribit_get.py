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
                    "params": {
                        "instrument_name": "ETH-PERPETUAL",
                        "amount": 10,
                        "type": "market",
                        "label": "tester"
                        }
                    }    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            connection_url+endpoint,
            auth=BasicAuth(client_id, client_secret),
            json=payload
                ) as response:
            # RESToverHTTP Status Code
            status_code: int = response.status
            logging.info(f'Response Status Code: {status_code}')

            # RESToverHTTP Response Content
            response: Dict = await response.json()
            logging.info(f'Response Content: {response}')

async def run_file():
        
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            endpoint=endpoint,
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
    run_file()
    
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            endpoint=endpoint,
            client_id=client_id,
            client_secret=client_secret,
            )
        )