# -*- coding: utf-8 -*-

# built ins
from typing import Dict

# installed
import aiohttp
from aiohttp.helpers import BasicAuth

# user defined formula
from configuration import id_numbering

async def main(
    endpoint: str,
    params: str,
    connection_url: str =None,
    client_id: str =None,
    client_secret: str=None,
        ) -> None:

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

async def send_order_limit (
                            connection_url: str,
                            client_id: str, 
                            client_secret: str, 
                            side: str, 
                            instrument: str, 
                            amount: float, 
                            price: float, 
                            label: str, 
                            type: str ='limit', 
                            reduce_only: bool = False, 
                            post_only: bool = True, 
                            reject_post_only: bool =True
                            ):
    
    
    if side == 'buy':
        endpoint: str = 'private/buy'
    if side == 'sell'  :
        endpoint: str = 'private/sell'
        
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
    
    try:
        
        print (params)
        print (endpoint)
        print (connection_url)
        print (client_id)        
        result = await main(
                endpoint=endpoint,
                params=params,
                connection_url=connection_url,
                client_id=client_id,
                client_secret=client_secret,
                )
    except Exception as error:
        print (error)
        
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


async def  get_server_time (connection_url: str):
    
    endpoint: str = 'public/get_time?'
    
    result = await main(
            endpoint=endpoint,
            connection_url=connection_url
            )
    return result     

async def get_position (connection_url: str, client_id, client_secret, currency):
        
    params =  {"currency": currency}
    endpoint: str = 'private/get_positions'
    
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
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result     
        

if __name__ == "__main__":
    # Logging
    pass
    