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
from typing import Dict
# installed
import aiohttp
from aiohttp.helpers import BasicAuth
from dotenv import load_dotenv
from os.path import join, dirname

# user defined formula
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


async def main(
    endpoint: str,
    params: str,
    connection_url: str,
    client_id: str =None,
    client_secret: str=None,
        ) -> None:

    # DBT LIVE RESToverHTTP Connection URL
    # DBT TEST RESToverHTTP Connection URL
    #connection_url: str = 'https://www.deribit.com/api/v2/'
    #connection_url: str = 'https://test.deribit.com/api/v2/'

    # DBT [POST] RESToverHTTP Payload
    from loguru import logger as log
    id = id_numbering.id(endpoint, endpoint)
    payload: Dict = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "method": f"{endpoint}",
                    "params": params
                    }  
    log.warning (payload)  
    print (endpoint)  
    log.error (client_id)  
    log.debug (client_secret)  

    if client_id == None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                connection_url+endpoint
                    ) as response:
                # RESToverHTTP Status Code
                status_code: int = response.status

                # RESToverHTTP Response Content
                response: Dict = await response.json()

            return response
                
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


async def send_order_limit (connection_url: str,
                            client_id,
                            client_secret,
                            side: str, 
                            instrument, 
                            amount, 
                            price, 
                            label: str, 
                            valid_until: int = False,
                            type: str ='limit',
                            reduce_only: bool = False, 
                            post_only: bool = True, 
                            reject_post_only: bool =True
                            ):
        
        
    if valid_until == False:
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
    else:
        params =  {
                "instrument_name": instrument,
                "amount": amount,
                "price": price,
                "label": label,
                "valid_until": valid_until,
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only
                }

    #print (params)    
    if side == 'buy':
        endpoint: str = 'private/buy'
    if side == 'sell'  :
        endpoint: str = 'private/sell'
        
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
        
    return result 
    
async def  get_open_orders_byInstruments (connection_url, client_id, client_secret, endpoint, instrument, type):
    params =  {
                "instrument_name": instrument,
                "type": type,
                }
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result 


async def  get_open_orders_byCurrency (connection_url, client_id, client_secret, currency):
    params =  {
                "currency": currency
                }
    
    endpoint_open_orders_currency: str = f'private/get_open_orders_by_currency'
    result = await main(
            endpoint=endpoint_open_orders_currency,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result 


async def  get_cancel_order_byOrderId(connection_url: str,
                                      client_id: str, 
                                      client_secret: str, 
                                      order_id: int):
    params =  {
                "order_id": order_id
                }
    
    endpoint: str = 'private/cancel'
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result     


async def get_position (connection_url: str, client_id, client_secret, currency):
        
    params =  {"currency": currency}
    endpoint: str = 'private/get_positions'
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result #['result']
        
async def  get_server_time (connection_url: str):
    
    endpoint: str = 'public/get_time?'
    params = {}
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )
    return result     

if __name__ == "__main__":
    # Logging
    pass
    