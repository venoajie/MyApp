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

# user defined formula
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


async def main(
    endpoint: str,
    params: str,
    client_id: str =None,
    client_secret: str=None,
        ) -> None:

    # DBT LIVE RESToverHTTP Connection URL
    # connection_url: str = 'https://www.deribit.com/api/v2/'
    # DBT TEST RESToverHTTP Connection URL
    connection_url: str = 'https://test.deribit.com/api/v2/'

    # DBT [POST] RESToverHTTP Payload
    id = id_numbering.id(endpoint, endpoint)
    payload: Dict = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "method": f"{endpoint}",
                    "params": params
                    }    


    if client_id == None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                connection_url+endpoint
                    ) as response:
                # RESToverHTTP Status Code
                status_code: int = response.status
                logging.info(f'Response Status Code: {status_code}')

                # RESToverHTTP Response Content
                response: Dict = await response.json()
                logging.info(f'Response Content: {response}')
                
    else:

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


async def send_order_limit (client_id, 
                      client_secret, 
                      endpoint, 
                      instrument, 
                      amount, 
                      price, 
                      label: str, 
                      type: str ='limit', 
                      reduce_only: bool = False, 
                      post_only: bool = True, 
                      reject_post_only: bool =True):
        
    params =  {
                "instrument_name": instrument,
                "amount": amount,
                "price": price,
                "label": label,
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only,
                }
    
    result = await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
        
    return result 
    
async def  get_open_orders_byInstruments (client_id, client_secret, endpoint, instrument, type):
    params =  {
                "instrument_name": instrument,
                "type": type,
                }
    
    result = await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result 

async def  get_index (index_name):
    params =  {
                "index_name": index_name,
                }
    print (params)
    endpoint = "public/get_index_price"
    result = await main(
            endpoint=endpoint,
            params=params,
            )
    return result 

async def  get_open_orders_byCurrency (client_id, client_secret, endpoint, currency):
    params =  {
                "currency": currency
                }
    
    result = await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result 
async def get_position (client_id, client_secret, endpoint, currency):
        
    params =  {"currency": currency}
    
    #result_example = {
    #    'jsonrpc': '2.0', 
    #    'id': 1, 
    #    'result': [
    #        {'total_profit_loss': -0.00045102, 'size_currency': 0.114176335, 'size': 136.0, 'settlement_price': 1204.67, 'realized_profit_loss': -6.593e-06, 
    #          realized_funding': -7e-06, 'open_orders_margin': 6.5233e-05, 'mark_price': 1191.14, 'maintenance_margin': 0.001141815, 'leverage': 50, 'kind': 'future',
    #          'interest_value': 1.4789043826111785, 'instrument_name': 'ETH-PERPETUAL', 'initial_margin': 0.002283579, 'index_price': 1191.91, 
    #          'floating_profit_loss': -0.000232514, 'estimated_liquidation_price': None, 'direction': 'buy', 'delta': 0.114176335, 'average_price': 1195.86}, 
    #        {'total_profit_loss': -7.62e-07, 'size_currency': -0.000839715, 'size': -1.0, 'settlement_price': 1202.17, 'realized_profit_loss': 0.0, 
    #        'open_orders_margin': 0.0, 'mark_price': 1190.88, 'maintenance_margin': 8.397e-06, 'leverage': 50, 'kind': 'future', 'instrument_name': 'ETH-18NOV22', #'initial_margin': 1.6794e-05, 'index_price': 1191.91, 'floating_profit_loss': -7.62e-07, 'estimated_liquidation_price': None, 'direction': 'sell', 'delta': -0.000839715, 'average_price': 1189.8}
    #        ], 
    #    'usIn': 1668690571373149, 
    #    'usOut': 1668690571373488, 
    #    'usDiff': 339, 
    #    'testnet': True
    #    }
    result = await main(
            endpoint=endpoint,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result ['result']
        
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
    