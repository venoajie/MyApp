#!/usr/bin/python3

import os
from os.path import join, dirname

# installed
from dataclassy import dataclass
from loguru import logger as log
import asyncio
from dotenv import load_dotenv
from os.path import join, dirname
import requests

from portfolio.deribit import open_orders_management, myTrades_management
from utils import pickling, system_tools, telegram_app, formula
import deribit_get#,deribit_rest
from risk_management import spot_hedging

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id_test'),
            'client_secret': os.environ.get('client_secret_test')
            }
@dataclass(unsafe_hash=True, slots=True)
class SynchronizingFiles ():

    
    '''
    '''       
    
    
    connection_url: str
    client_id: str
    client_secret: str
        
    async def open_orders (self, currency) -> float:
        """
        """
        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, client_id, client_secret, currency)
        open_ordersREST: list = open_ordersREST ['result']
                        
        return open_orders_management.MyOrders (open_ordersREST)
    
    async def get_account_summary (self, currency) -> float:
        """
        """
        account_summary: list = await deribit_get.get_account_summary (self.connection_url, client_id, client_secret, currency)
                        
        return account_summary ['result']
    
    async def get_instruments (self, currency) -> float:
        """
        """
    
        end_point_all=(f' {self.connection_url}public/get_instruments?currency={currency}&expired=false&kind=future')
        return (requests.get(end_point_all).json()) ['result'] 
    
    async def get_index (self, currency) -> float:
        """
        """

        
        
        end_point_all=(f' {self.connection_url}public/get_index?currency={currency.upper()}')
        index=(requests.get(end_point_all).json()) ['result']  
        
        return index [currency.upper()]
    
    async def check_if_new_order_will_create_over_hedged (self, currency, label_hedging)-> list:
        
        '''
        '''   
        label_open = 'hedging spot-open'
        open_orders_from_exchange = await self.open_orders(currency)
        log.error (open_orders_from_exchange)
        open_orders_label = open_orders_from_exchange.my_orders_api_basedOn_label(label_open)
        log.error (open_orders_label)
        

        index_price = await self.get_index (currency)
        instruments = await self.get_instruments (currency)
        instruments_name =  [o['instrument_name'] for o in instruments] 

        portfolio = await self.get_account_summary (currency)
        log.debug (instruments)
        log.info (index_price)
        log.warning (portfolio)
        equity = portfolio  ['equity']
        notional = index_price * equity  
        log.warning (notional)
        for instrument in instruments_name:
            log.debug (instruments_name)
            instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]  [0]
            log.debug (instrument_data)
            min_trade_amount = instrument_data ['min_trade_amount']
            contract_size = instrument_data ['contract_size']  
            log.critical (instrument)
            log.critical ('perpetual' in instrument)
            spot_hedged = spot_hedging.SpotHedging ('hedging spot')
            
            if 'PERPETUAL' in instrument:
                check_spot_hedging = spot_hedged.is_spot_hedged_properly (open_orders_label,
                                                                                                notional, 
                                                                                                min_trade_amount,
                                                                                                contract_size
                                                                                                ) 

                if  spot_hedged.is_over_hedged (open_orders_label, check_spot_hedging ['hedging_size']):
                    open_order_id: list = open_orders_from_exchange.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')
                    #log.critical (open_orders_hedging_lastUpdate_tStamp_minId)
                    await deribit_get.get_cancel_order_byOrderId (
                                                                    self.connection_url, 
                                                                    client_id, 
                                                                client_secret, 
                                                                open_order_id
                                                            )


def main ():
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    connection_url: str = 'https://test.deribit.com/api/v2/'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
    try:

        syn=SynchronizingFiles (
        connection_url=connection_url,
        client_id=client_id,
        client_secret= client_secret
        )
                
        loop = asyncio.get_event_loop()
        loop.run_until_complete(syn.open_orders('eth'))
        label_hedging = 'spot hedging'
        
        loop.run_until_complete(syn.get_instruments('ETH'))
        loop.run_until_complete(syn.get_index('ETH'))
        loop.run_until_complete(syn.get_account_summary('ETH'))
        loop.run_until_complete(syn.check_if_new_order_will_create_over_hedged ('ETH', label_hedging))
         

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
    
if __name__ == "__main__":

    # DBT Client ID
    client_id: str = parse_dotenv() ['client_id']
    # DBT Client Secret
    client_secret: str = parse_dotenv() ['client_secret']
    config = {
    'client_id': 'client_id',
    'client_secret': 'client_secret'
}
    db_config = [{k: os.environ.get(v) for k, v in config.items()}]
    #log.error (db_config)
    db_config = [o  for o in db_config]
    #log.error (db_config)
    
    try:
        main()
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
