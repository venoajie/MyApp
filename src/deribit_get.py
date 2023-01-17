# built ins
from typing import Dict
# installed
import asyncio
import websockets
import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from dotenv import load_dotenv
from os.path import join, dirname

# user defined formula
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

async def get_unauthenticated(
    connection_url: str,
    endpoint: str
        ) -> None:

    async with aiohttp.ClientSession() as session:
        async with session.get(
            connection_url+endpoint
                ) as response:
            # RESToverHTTP Status Code
            status_code: int = response.status


            # RESToverHTTP Response Content
            response: Dict = await response.json()

            return response

async def main(
    endpoint: str,
    params: str,
    connection_url: str,
    client_id: str =None,
    client_secret: str=None,
        ) -> None:

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

async def send_order  (connection_url: str,
                            client_id,
                            client_secret,
                            side: str, 
                            instrument, 
                            amount, 
                            label: str = None, 
                            price: float = None, 
                            type: str ='limit',
                            trigger_price: float = None, 
                            trigger: str = 'last_price', 
                            time_in_force: str ='fill_or_kill',
                            reduce_only: bool = False, 
                            valid_until: int = False,
                            post_only: bool = True, 
                            reject_post_only: bool =False
                            ):
    print (f'{side=}')
    print (f'{instrument=}')
    print (f'{amount=}')
    print (f'{label=}')
    print (f'{price=}')
    print (f'{type=}')
    print (f'{time_in_force=}')
    print (f'{trigger=}')
    print (f'{reduce_only=}')
        
    if valid_until == False:
        if trigger_price == None:
            if 'market' in type:
                params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "reduce_only": reduce_only,
                    }
            else:
                params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "reduce_only": reduce_only,
                    "post_only": post_only,
                    "reject_post_only": reject_post_only,
                    }
        else:
            if 'market' in type :
                params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "trigger": trigger,
                    "trigger_price": trigger_price,
                    "reduce_only": reduce_only
                    }
            else:
                params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "price": price,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "trigger": trigger,
                    "trigger_price": trigger_price,
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
                #"time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only
                }

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
    
    
async def send_order_markett (connection_url: str,
                            client_id,
                            client_secret,
                            side: str, 
                            instrument, 
                            amount, 
                            label: str, 
                            type: str ='market',
                            time_in_force: str ='fill_or_kill',
                            trigger: str = 'last_price', 
                            trigger_price: float = None, 
                            reduce_only: bool = False, 
                            valid_until: int = False,
                            post_only: bool = True, 
                            reject_post_only: bool =False
                            ):
        
    if valid_until == False:
        if trigger_price == None:
            params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "reduce_only": reduce_only,
                    "post_only": post_only,
                    "reject_post_only": reject_post_only,
                    }
        else:
            params =  {
                    "instrument_name": instrument,
                    "amount": amount,
                    "label": label,
                    #"time_in_force": time_in_force, fik can not apply to post only
                    "type": type,
                    "trigger": trigger,
                    "trigger_price": trigger_price,
                    "reduce_only": reduce_only,
                    "post_only": post_only,
                    "reject_post_only": reject_post_only,
                    }
    else:
        params =  {
                "instrument_name": instrument,
                "amount": amount,
                "label": label,
                "valid_until": valid_until,
                #"time_in_force": time_in_force, fik can not apply to post only
                "type": type,
                "reduce_only": reduce_only,
                "post_only": post_only,
                "reject_post_only": reject_post_only
                }

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

async def  get_open_orders_byCurrency (connection_url, 
                                       client_id, 
                                       client_secret, 
                                       currency: str
                                       )-> list:
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

async def  get_user_trades_by_currency (connection_url, 
                                        client_id, 
                                        client_secret, 
                                        currency: str, 
                                        count: int =1000
                                        )-> list:
    params =  {
                "currency": currency.upper(),
                "kind": 'any',
                "count": count
                }
    
    endpoint_get_user_trades: str = f'private/get_user_trades_by_currency'
    result = await main(
            endpoint= endpoint_get_user_trades,
            params= params,
            connection_url= connection_url,
            client_id= client_id,
            client_secret= client_secret,
            )
    return result 

async def  get_user_trades_by_instrument (connection_url, 
                                          client_id, 
                                          client_secret, 
                                          currency: str, 
                                          count: int =1000
                                          ):
    
    params =  {
                "currency": currency.upper(),
                "kind": 'any',
                "count": count
                }
    
    endpoint_get_user_trades: str = f'private/get_user_trades_by_instrument'
    result = await main(
            endpoint= endpoint_get_user_trades,
            params= params,
            connection_url= connection_url,
            client_id= client_id,
            client_secret= client_secret,
            )
    return result 

async def  get_user_trades_by_currency_and_time (connection_url, 
                                                 client_id, 
                                                 client_secret, 
                                                 currency: str, 
                                                 start_timestamp: int, 
                                                 end_timestamp: int, 
                                                 count: int = 1000, 
                                                 include_old: bool = True
                                                 )-> list:
    params =  {
                "currency": currency.upper(),
                "kind": "any",
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "count": count,
                "include_old": include_old
                }
    
    endpoint_get_user_trades: str = f'private/get_user_trades_by_currency_and_time'
    result = await main(
            endpoint= endpoint_get_user_trades,
            params= params,
            connection_url= connection_url,
            client_id= client_id,
            client_secret= client_secret,
            )
    return result 

async def  get_order_history_by_instrument (connection_url, client_id, client_secret, instrument_name, count: int = 100):
    params =  {
                "instrument_name": instrument_name.upper(),
                "include_old": True,
                "include_unfilled": True,
                "count": count
                }
    
    endpoint_get_order_history: str = f"private/get_order_history_by_instrument"
    result = await main(
            endpoint= endpoint_get_order_history,
            params= params,
            connection_url= connection_url,
            client_id= client_id,
            client_secret= client_secret,
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

async def get_positions (connection_url: str, client_id, client_secret, currency):
        
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

async def get_account_summary (connection_url: str, client_id, client_secret, currency):
        
    params =  {"currency": currency,
    "extended": True}
    endpoint: str = 'private/get_account_summary'
    
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

async def  get_index (connection_url: str, currency):
    
    endpoint: str = 'public/get_index'
    params =  {"currency": 'ETH'}
    print (endpoint)
    print (params)
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )
    return result     

async def  get_instruments (connection_url: str, currency):
    
    endpoint: str = 'public/get_instruments'
    params =  {"currency": 'ETH',
    "kind": "future",
    "expired": False}
    
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )
    return result     

from utilities import system_tools, pickling
async def call_api(currency, msg):
   async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
            response = await websocket.recv()
            response: dict = orjson.loads(response)
            response_data: dict = response ['result']
            
            if response['id'] == 7617:
                my_path = system_tools.provide_path_for_file ('instruments', 'replace', currency.lower()) 
                print (my_path)
                pickling.replace_data(my_path, response_data)

if __name__ == "__main__":
    # Logging

    currencies = ['BTC', 'ETH']

    for curr in currencies:
                
        msg = \
        {
        "jsonrpc" : "2.0",
        "id" : 7617,
        "method" : "public/get_instruments",
        "params" : {
            "currency" : f"{curr}",
            "kind" : "future",
            "expired" : False
        }
        }

       
        asyncio.get_event_loop().run_until_complete(call_api(curr, json.dumps(msg)))
        