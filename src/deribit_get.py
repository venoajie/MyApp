# built ins
from typing import Dict

# installed
import asyncio

from dataclassy import dataclass#import websockets
#import json, orjson
import aiohttp
from aiohttp.helpers import BasicAuth
from dotenv import load_dotenv
from os.path import join, dirname

# user defined formula
from configuration import id_numbering, config

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

params_coinGlass = {
            "accept": "application/json",
            "coinglassSecret": "877ad9af931048aab7e468bda134942e"
        }


async def main(
    endpoint: str,
    params: str,
    connection_url: str,
    client_id: str =None,
    client_secret: str=None,
        ) -> None:

    id = id_numbering.id(endpoint, 
                         endpoint
                         )
    
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

@dataclass(unsafe_hash=True, slots=True)
class GetPrivateData ():
    
    '''
    '''       
    
    connection_url: str
    client_id: str
    client_secret: str
    currency: str
        
    async def get_subaccounts (self):
            
        # Set endpoint
        endpoint: str = 'private/get_subaccounts_details'

        params =  {"currency": self.currency,
                "with_open_orders": True}
        
        result = await main(
                endpoint=endpoint,
                params=params,
                connection_url=self.connection_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                )
        
        return result #['result']

            
    async def get_account_summary (self):
            
        params =  {"currency": self.currency,
                   "extended": True
                   }

        # Set endpoint
        endpoint: str = 'private/get_account_summary'
        
        result = await main(
                endpoint=endpoint,
                params=params,
                connection_url=self.connection_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                )
        
        return result #['result']
        
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
                    "price": price,
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
                    "label": label,
                    "price": price,
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
    
    
async def send_order_market (connection_url: str,
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

    # Set endpoint based on side
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

async def  get_open_orders_byInstruments (connection_url, 
                                          client_id, client_secret,
                                          instrument, 
                                          type
                                          ):
    endpoint_open_orders: str = f'private/get_open_orders_by_instrument'
    params =  {
                "instrument_name": instrument.upper(),
                "type": type,
                }
    
    result = await main(
            endpoint=endpoint_open_orders,
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
    
    # Set endpoint
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
    
    # Set endpoint
    endpoint_get_user_trades: str = f'private/get_user_trades_by_currency'

    params =  {
                "currency": currency.upper(),
                "kind": 'any',
                "count": count
                }
    
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
                                          instrument_name: str, 
                                          count: int =1000
                                          ):
    
    # Set endpoint
    endpoint_get_user_trades: str = f'private/get_user_trades_by_instrument'
    
    params =  {
                "instrument_name": instrument_name.upper(),
                "count": count
                }

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
    
    # Set endpoint
    endpoint_get_user_trades: str = f'private/get_user_trades_by_currency_and_time'

    params =  {
                "currency": currency.upper(),
                "kind": "any",
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "count": count,
                "include_old": include_old
                }

    result = await main(
            endpoint= endpoint_get_user_trades,
            params= params,
            connection_url= connection_url,
            client_id= client_id,
            client_secret= client_secret,
            )

    return result 

async def  get_order_history_by_instrument (connection_url, 
                                            client_id, 
                                            client_secret, 
                                            instrument_name,
                                            count: int = 100
                                            ):

    
    # Set endpoint
    endpoint_get_order_history: str = f"private/get_order_history_by_instrument"

    params =  {
                "instrument_name": instrument_name.upper(),
                "include_old": True,
                "include_unfilled": True,
                "count": count
                }

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
    # Set endpoint
    endpoint: str = 'private/cancel'

    params =  {
                "order_id": order_id
                }
        
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result     

async def get_positions (connection_url: str, 
                         client_id, 
                         client_secret, 
                         currency):

    # Set endpoint
    endpoint: str = 'private/get_positions'
        
    params =  {"currency": currency}

    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            )
    return result #['result']

async def  get_server_time (connection_url: str):

    """
    Returning server time
    """
    # Set endpoint
    endpoint: str = 'public/get_time?'
    
    # Set the parameters  
    params = {}
    
    # Get result
    result = await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )
    
    return result  

async def  get_index (connection_url: str,
                      currency
                      ):
    
    # Set endpoint
    endpoint: str = f'public/get_index?currency={currency.upper()}'
    params =  {}
    
    return await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )     
    
async def  get_instruments (connection_url: str,
                      currency
                      ):
    
    # Set endpoint
    endpoint: str = f'public/get_instruments?currency={currency.upper()}'
    params =  {}
    
    return await main(
            endpoint=endpoint,
            params=params,
            connection_url=connection_url
            )     
    
async def  get_currencies (
                            connection_url: str
                           )->list:
    
    # Set endpoint
    endpoint: str = f'public/get_currencies?'
    params =  {}
    
    return await main (
                        endpoint=endpoint,
                        params=params,
                        connection_url=connection_url
                        )     
    
    
async def  get_ohlc (
                    connection_url: str,
                    instrument_name,
                    resolution,
                    qty_candles,
                           )->list:
    
    from datetime import datetime
    from utilities import time_modification
    
    now_utc = datetime.now()
    now_unix = time_modification.convert_time_to_unix (now_utc)
    start_timestamp = now_unix - 60000 * qty_candles
    params = {}

    # Set endpoint
    endpoint: str = f'public/get_tradingview_chart_data?end_timestamp={now_unix}&instrument_name={instrument_name.upper()}&resolution={resolution}&start_timestamp={start_timestamp}'

    return await main (
                        endpoint=endpoint,
                        params=params,
                        connection_url=connection_url
                        )     

async def  get_open_interest_aggregated_ohlc (
                                            connection_url: str,
                                            currency,
                                            resolution
                                            )->list:
    
    '''
    interval = m1 m5 m15 h1 h4 h12 all

    '''       
    # Set endpoint
    endpoint: str = f'indicator/open_interest_aggregated_ohlc?symbol={currency}&interval={resolution}'

    try:
        return await main (
                        endpoint=endpoint,
                        params={},
                        connection_url=connection_url
                        )     
    
    except:
        return await main (
                        endpoint=endpoint,
                        params=params_coinGlass,
                        connection_url=connection_url
                        )     
    

async def  get_open_interest_historical (
                                            connection_url: str,
                                            currency,
                                            resolution
                                            )->list:

    '''
    time_frame = m1 m5 m15 h1 h4 h12 all
    currency = USD or symbol

    '''       
    # Set endpoint
    endpoint: str = f'open_interest_history?symbol={currency}&time_type={resolution}&currency={currency}'

    try:
        return await main (
                        endpoint=endpoint,
                        params={},
                        connection_url=connection_url
                        )     
    
    except:
        return await main (
                        endpoint=endpoint,
                        params=params_coinGlass,
                        connection_url=connection_url
                        )     
    

async def  get_open_interest_symbol (
                                            connection_url: str,
                                            currency
                                            )->list:

    # Set endpoint
    endpoint: str = f'open_interest?symbol={currency}'
    try:
        return await main (
                        endpoint=endpoint,
                        params={},
                        connection_url=connection_url
                        )     
    
    except:
        return await main (
                        endpoint=endpoint,
                        params=params_coinGlass,
                        connection_url=connection_url
                        )     
    
async def  telegram_bot_sendtext (
                            bot_message: str, 
                            purpose: str = 'general_error'
                            ) -> str:
    
    """
    # simple telegram
    #https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
    """

    tel = (config.main_dotenv ('telegram-failed_order'))

    try:
        bot_token   = config.main_dotenv ('telegram-failed_order')['bot_token']
    
    except:
        bot_token   = config.main_dotenv ('telegram-failed_order')['BOT_TOKEN']
    
    if purpose == 'failed_order':
        
        try:
            bot_chatID  = config.main_dotenv ('telegram-failed_order')['BOT_CHATID_FAILED_ORDER']
        except:
            bot_chatID  = config.main_dotenv ('telegram-failed_order')['bot_chatid']
        
    if purpose == 'general_error':
        try:
            bot_chatID  = config.main_dotenv ('telegram-general_error')['bot_chatid']

        except:
            bot_chatID  = config.main_dotenv ('telegram-general_error')['BOT_CHATID_GENERAL_ERROR']
    connection_url   = 'https://api.telegram.org/bot'
    endpoint   = bot_token + ('/sendMessage?chat_id=') + bot_chatID + (
							        '&parse_mode=HTML&text=') + bot_message
        

    try:
        return await main (
                        endpoint=endpoint,
                        params={},
                        connection_url=connection_url
                        )     
    
    except:
        return await main (
                        endpoint=endpoint,
                        params=params_coinGlass,
                        connection_url=connection_url
                        )     
    
