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
from configuration import  label_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def telegram_bot_sendtext(bot_message, purpose) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

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
        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, self.client_id, self.client_secret, currency)
        open_ordersREST: list = open_ordersREST ['result']
                        
        return open_orders_management.MyOrders (open_ordersREST)
    
    async def get_account_summary (self, currency: str) -> list:
        """
        """
        account_summary: list = await deribit_get.get_account_summary (self.connection_url, self.client_id, self.client_secret, currency)
                        
        return account_summary ['result']
    
    async def get_instruments (self, currency: str) -> list:
        """
        """
    
        endpoint=(f'public/get_instruments?currency={currency}&expired=false&kind=future')
        result: list = await deribit_get.get_unauthenticated(self.connection_url, endpoint)
        return result ['result']
    
    async def get_index (self, currency: str) -> float:
        """
        """
            
        endpoint: str = f'public/get_index?currency={currency.upper()}'
        result: list = await deribit_get.get_unauthenticated(self.connection_url, endpoint)
        
        return result ['result'] [currency.upper()]
    
    async def send_orders (self, side: str, instrument: str, prc: float, size: float, label: str = None) -> None:
        """
        """

        try:
            await deribit_get.send_order_limit (self.connection_url,
                                                self.client_id, 
                                                self.client_secret, 
                                                side, 
                                                instrument, 
                                                size, 
                                                prc,
                                                label
                                                )
            
            info= (f'SEND ORDER {label} {instrument} {size} \n ')
            telegram_bot_sendtext(info,'success_order')
            
        except Exception as e:
            log.error (e)
            
    async def compute_notional_value (self, index_price: float, equity: float) -> float:
        """
        """
        return index_price * equity  
    
    async def cancel_orders_hedging_spot_based_on_time_threshold (self, currency) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3
        current_time = await deribit_get.get_server_time(self.connection_url)
        current_server_time = current_time ['result']
        open_order_mgt = await self.open_orders (currency)
        if open_order_mgt !=[]:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime : int = current_server_time - open_orders_lastUpdateTStamp_min                       

            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')                        
            if open_orders_deltaTime > three_minute:
                await deribit_get.get_cancel_order_byOrderId(self.connection_url, self.client_id, self.client_secret, open_order_id)    
    
    async def reading_from_database (self, currency: str) -> float:
        """
        """
        my_trades_path_open : str = system_tools.provide_path_for_file ('myTrades', currency, 'open')
        my_trades_open : list = pickling.read_data(my_trades_path_open) 
        
        my_path_orders_open : str = system_tools.provide_path_for_file ('orders', currency, 'open')
        open_orders_open_byAPI : list = pickling.read_data(my_path_orders_open)
        
        my_path_portfolio : str = system_tools.provide_path_for_file ('portfolio', currency.lower())                                                                                     
        portfolio = pickling.read_data(my_path_portfolio)
        
        my_path_instruments : str = system_tools.provide_path_for_file ('instruments',  currency)          
        instruments = pickling.read_data (my_path_instruments)
                   
        symbol_index : str = f'{currency}_usd'
        my_path_index : str = system_tools.provide_path_for_file ('index',  symbol_index)  
        index_price : list = pickling.read_data(my_path_index) 
        index_price : float= index_price [0]['price']
        
        return {'my_trades_open': my_trades_open,
                'open_orders_open_byAPI': open_orders_open_byAPI,
                'portfolio': portfolio,
                'index_price': index_price,
                'instruments': instruments}
    
    async def running_strategy (self, currency) -> float:
        """
        source data: loaded from database app
        """

        reading_from_database = await self.reading_from_database (currency)
        my_trades_open : list = reading_from_database ['my_trades_open']
        open_orders_open_byAPI : list = reading_from_database ['open_orders_open_byAPI']
        portfolio = reading_from_database ['portfolio']
        instruments = reading_from_database ['instruments']
        index_price : float= reading_from_database['index_price']
        
        instruments_name : list = [] if instruments == [] else [o['instrument_name'] for o in instruments] 
        
        for instrument in instruments_name:

            my_path_ordBook : str = system_tools.provide_path_for_file ('ordBook', instrument) 
            
            ordBook = pickling.read_data(my_path_ordBook)
            
            if  index_price and portfolio and ordBook  :
                
                equity = portfolio [0]['equity']
                notional =  await self.compute_notional_value (index_price, equity)
    
                if 'PERPETUAL' in instrument:
                    instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 

                    min_trade_amount = instrument_data ['min_trade_amount']
                    contract_size = instrument_data ['contract_size']
                                    
                    max_time_stamp_ordBook = max ([o['timestamp'] for o in ordBook ])
                    most_current_ordBook = [o for o in ordBook if o['timestamp'] == max_time_stamp_ordBook ]

                    best_bid_prc= most_current_ordBook[0]['bids'][0][0]
                    best_ask_prc= most_current_ordBook[0]['asks'][0][0]

                    #check under hedging
                    label_hedging = 'hedging spot'
                    spot_hedged = spot_hedging.SpotHedging (label_hedging,
                                                            my_trades_open
                                                            )
                    
                    check_spot_hedging = spot_hedged.is_spot_hedged_properly (open_orders_open_byAPI, 
                                                                            notional, 
                                                                            min_trade_amount,
                                                                            contract_size
                                                                            ) 
                    spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']
                    label: str = label_numbering.labelling ('open', label_hedging)

                    if spot_was_unhedged:
                        log.warning(f'{instrument=} {best_ask_prc=} {spot_hedged=} {label=}')
                    
                        await self.send_orders ('sell', 
                                                instrument, 
                                                best_ask_prc,
                                                check_spot_hedging ['hedging_size'], 
                                                label
                                                )
                                        
    async def check_if_new_order_will_create_over_hedged (self, currency, label_hedging)-> list:
        
        '''
        source data: fetch independently from exchange through get protocol
        '''   
        label_open = 'hedging spot-open'
        open_orders_from_exchange = await self.open_orders(currency)
        open_orders_label = open_orders_from_exchange.my_orders_api_basedOn_label(label_open)

        index_price = await self.get_index (currency)
        instruments = await self.get_instruments (currency)
        instruments_name =  [o['instrument_name'] for o in instruments] 

        portfolio = await self.get_account_summary (currency)

        equity = portfolio  ['equity']
        notional = await self.compute_notional_value (index_price, equity)

        for instrument in instruments_name:
            if 'PERPETUAL' in instrument:

                log.debug (instruments_name)
                instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]  [0] 
                min_trade_amount = instrument_data ['min_trade_amount']
                contract_size = instrument_data ['contract_size']  
                spot_hedged = spot_hedging.SpotHedging ('hedging spot')
            
                check_spot_hedging = spot_hedged.is_spot_hedged_properly (open_orders_label,
                                                                          notional,
                                                                          min_trade_amount,
                                                                          contract_size
                                                                          ) 

                if  spot_hedged.is_over_hedged (open_orders_label, check_spot_hedging ['hedging_size']):
                    open_order_id: list = open_orders_from_exchange.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')
                    
                    info= (f'CANCEL ORDER {instrument} \n ')
                    telegram_bot_sendtext(info,'failed_order')
                    await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                                  client_id,
                                                                  client_secret, 
                                                                  open_order_id
                                                                  )
async def main ():
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    connection_url: str = 'https://test.deribit.com/api/v2/'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    
    try:

        syn = SynchronizingFiles (
        connection_url=connection_url,
        client_id=client_id,
        client_secret= client_secret
        )
        label_hedging = 'spot hedging'

        info= (f'RUNNING ORDER \n ')
        telegram_bot_sendtext(info,'general_error')
        await syn.running_strategy ('eth')
        await syn.check_if_new_order_will_create_over_hedged ('eth', label_hedging)
        await syn.cancel_orders_hedging_spot_based_on_time_threshold ('eth')
                
         
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
        asyncio.get_event_loop().run_until_complete(main())
    
        log.info ('SLEEP 30')
        #formula.sleep_and_restart_program (30)
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
