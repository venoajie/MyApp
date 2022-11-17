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
            return response

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
    
    result_example = {
        'jsonrpc': '2.0', 
        'id': 1, 
        'result': [
            {'total_profit_loss': -0.000200432, 'size_currency': 0.113925747, 'size': 136.0, 'settlement_price': 1204.67, 'realized_profit_loss': -6.91e-06, 'realized_funding': -7e-06, 'open_orders_margin': 6.5233e-05, 'mark_price': 1193.76, 'maintenance_margin': 0.001139309, 'leverage': 50, 'kind': 'future', 'interest_value': 1.546050465478317, 'instrument_name': 'ETH-PERPETUAL', 'initial_margin': 0.002278567, 'index_price': 1194.59, 'floating_profit_loss': 1.8074e-05, 'estimated_liquidation_price': None, 'direction': 'buy', 'delta': 0.113925747, 'average_price': 1195.86
             }
            ], 
        'usIn': 1668690571373149, 
        'usOut': 1668690571373488, 
        'usDiff': 339, 
        'testnet': True
        }
    return await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )['result']
        
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
    