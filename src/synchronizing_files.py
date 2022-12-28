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
from utils import pickling, system_tools, telegram_app, formula, string_modification
import deribit_get#,deribit_rest
from risk_management import spot_hedging
from configuration import  label_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def telegram_bot_sendtext(bot_message, purpose: str = 'general_error') -> None:
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
        
    async def open_orders (self, currency) -> list:
        """
        """
        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, self.client_id, self.client_secret, currency)
        open_ordersREST: list = open_ordersREST ['result']
                        
        return open_orders_management.MyOrders (open_ordersREST)
        
    async def my_trades (self, currency, start_timestamp: int, end_timestamp: int) -> list:
        """
        """
        trades: list = await deribit_get.get_user_trades_by_currency_and_time (self.connection_url, 
                                                                               self.client_id, 
                                                                               self.client_secret, 
                                                                               currency, 
                                                                               start_timestamp,
                                                                               end_timestamp)
        #trades: list = trades ['result']
                        
        return trades ['result'] ['trades']
        
        
        
    async def my_trades_api_basedon_label (self, currency, start_timestamp: int, end_timestamp: int, label: str) -> list:
        """
        """
        my = await self.my_trades (currency, 
                               start_timestamp,
                               end_timestamp)
        log.warning (my)
        return  self.my_trades (currency, 
                               start_timestamp,
                               end_timestamp). my_trades_api_basedOn_label (label
                               )
    
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
            telegram_bot_sendtext(info)
            
        except Exception as e:
            log.error (e)
            
    async def compute_notional_value (self, index_price: float, equity: float) -> float:
        """
        """
        return index_price * equity  
    
    
    async def reading_from_database (self, currency: str= None, instrument: str = None) -> float:
        """
        """
        my_path_ordBook: str = system_tools.provide_path_for_file ('ordBook', instrument) 
        if currency==None:
            return {'ordBook': pickling.read_data(my_path_ordBook)}
        else:
                
            my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', currency, 'open')
            my_trades_open: list = pickling.read_data(my_trades_path_open) 
            
            my_path_orders_open: str = system_tools.provide_path_for_file ('orders', currency, 'open')
            my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', currency, 'closed')
            
            my_path_portfolio: str = system_tools.provide_path_for_file ('portfolio', currency.lower())                                                                                     
            portfolio = pickling.read_data(my_path_portfolio)
            
            my_path_instruments: str = system_tools.provide_path_for_file ('instruments',  currency)          
            instruments = pickling.read_data (my_path_instruments)
                    
            symbol_index: str = f'{currency}_usd'
            my_path_index: str = system_tools.provide_path_for_file ('index',  symbol_index)  
            index_price: list = pickling.read_data(my_path_index) 
            index_price: float= index_price [0]['price']
            
            
            return {'my_trades_open': my_trades_open,
                    'open_orders_open_byAPI': pickling.read_data(my_path_orders_open),
                    'open_orders_closed_byAPI': pickling.read_data(my_path_orders_closed),
                    'portfolio': portfolio,
                    'index_price': index_price,
                    'instruments': instruments}
    
    async def market_price (self, instrument: str) -> list:
        """
        """

        ordBook = await self.reading_from_database (None, instrument)
        ordBook = ordBook ['ordBook']
            
        max_time_stamp_ordBook = max ([o['timestamp'] for o in ordBook ])
        most_current_ordBook = [o for o in ordBook if o['timestamp'] == max_time_stamp_ordBook ]

        best_bid_prc= most_current_ordBook[0]['bids'][0][0]
        best_ask_prc= most_current_ordBook[0]['asks'][0][0]

        return {'best_bid_prc': best_bid_prc,
                'best_ask_prc': best_ask_prc
                }
    
    async def current_server_time (self) -> float:
        """
        """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time   ['result']
    
    async def cancel_redundant_orders_in_same_labels (self, currency, label_for_filter) -> None:
        """
        """
    
        open_order_mgt = await self.open_orders (currency)
        len_current_open_orders = open_order_mgt.my_orders_api_basedOn_label_items_qty(label_for_filter)
    
        if len_current_open_orders != [] :
            if len_current_open_orders > 1 :
            
                info= (f'CANCEL ORDER  {label_for_filter} \n ')
                telegram_bot_sendtext(info,'failed_order')        
                
                open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_max_id (label_for_filter) 
                
                await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                                client_id,
                                                                client_secret, 
                                                                open_order_id
                                                                )
                    
    
    async def cancel_orders_hedging_spot_based_on_time_threshold (self, currency) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3
        current_time = await deribit_get.get_server_time(self.connection_url)
        current_server_time = current_time ['result']
        open_order_mgt = await self.open_orders (currency)
        log.critical (open_order_mgt)
        try:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
        except:
            open_orders_lastUpdateTStamps: list = []    
        if open_orders_lastUpdateTStamps !=[]:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = await self.current_server_time () - open_orders_lastUpdateTStamp_min                       

            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_min_id ('hedging spot-open')                        
            if open_orders_deltaTime > three_minute:
                
                info= (f'CANCEL ORDER  expired \n ')
                telegram_bot_sendtext(info,'failed_order')     
                await deribit_get.get_cancel_order_byOrderId(self.connection_url, self.client_id, self.client_secret, open_order_id)    
    
    async def price_averaging (self, myTrades: list, threshold, currency, index_price, size, label_open, best_bid_prc: float = None, best_ask_prc: float = None) -> float:
        """
        """
        
        if myTrades :
            my_trades_mgt = myTrades_management.MyTrades (myTrades)
            
            my_trades_max_price_attributes_filteredBy_label = my_trades_mgt.my_trades_max_price_attributes_filteredBy_label ('hedging spot-open')
            log.debug(f'{my_trades_max_price_attributes_filteredBy_label=}')
            myTrades_max_price = my_trades_max_price_attributes_filteredBy_label ['max_price']
            myTrades_max_price_pct_vs_threshold = myTrades_max_price * threshold
            myTrades_max_price_diff_with_index_price = abs (index_price - myTrades_max_price) > myTrades_max_price_pct_vs_threshold
            
            log.warning(f'{myTrades_max_price=} {myTrades_max_price_pct_vs_threshold=} {myTrades_max_price_diff_with_index_price=}')
            
            if myTrades_max_price_diff_with_index_price:
                myTrades_max_price_attributes_label = my_trades_max_price_attributes_filteredBy_label ['label']
                label_int = string_modification.extract_integers_from_text (myTrades_max_price_attributes_label)
                
                label_to_send = f'hedging spot-closed-{label_int}'
                label_closed_for_filter = 'hedging spot-closed'
                label_open_for_filter = 'hedging spot-open'
                
                current_open_orders =   await self.reading_from_database(currency) 
                current_open_orders =   current_open_orders ['open_orders_open_byAPI']
                current_open_orders_filtered_label_closed = [o for o in current_open_orders if label_closed_for_filter in o['label'] ] 
                current_open_orders_filtered_label_open = [o for o in current_open_orders if label_open_for_filter in o['label'] ] 
                
                log.warning(f'{myTrades_max_price_attributes_label=} {label_int=} {label_to_send=} {index_price < myTrades_max_price=} {index_price > myTrades_max_price}')
                log.error(f'{current_open_orders=}')
                log.debug(f'{current_open_orders_filtered_label_closed=}')
                log.error(f'{ current_open_orders_filtered_label_closed == []=}')
                log.debug(f'{current_open_orders_filtered_label_open=}')
                log.error(f'{ current_open_orders_filtered_label_open == []=}')
                
                instrument = my_trades_max_price_attributes_filteredBy_label ['instrument']
                log.error(f'{instrument=}')
                
                if index_price < myTrades_max_price and current_open_orders_filtered_label_closed == []:
                    if best_bid_prc == None:
                        best_bid_prc = self.market_price(instrument)
                    log.error(f'{best_bid_prc=}')
                    log.error(my_trades_max_price_attributes_filteredBy_label ['size'])

                    await self.send_orders (
                                            'buy', 
                                            instrument, 
                                            best_bid_prc, 
                                            my_trades_max_price_attributes_filteredBy_label ['size'], 
                                            label_to_send
                                            )
                    await self.cancel_redundant_orders_in_same_labels (currency, label_closed_for_filter)
                
                if index_price > myTrades_max_price and current_open_orders_filtered_label_open ==[]:
                    if best_ask_prc == None:
                        best_ask_prc = self.market_price(instrument)
                    log.error(f'{best_ask_prc=}')
                    log.error(my_trades_max_price_attributes_filteredBy_label ['size'])

                    await self.send_orders (
                                            'sell', 
                                            instrument, 
                                            best_ask_prc, 
                                            size, 
                                            label_open
                                            )
                    await self.cancel_redundant_orders_in_same_labels (currency, label_open_for_filter)
                    
    async def running_strategy (self, currency) -> float:
        """
        source data: loaded from database app
        """

        reading_from_database = await self.reading_from_database (currency)
        my_trades_open: list = reading_from_database ['my_trades_open']
        open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
        portfolio = reading_from_database ['portfolio']
        instruments = reading_from_database ['instruments']
        index_price: float= reading_from_database['index_price']
        
        instruments_name: list = [] if instruments == [] else [o['instrument_name'] for o in instruments] 
        
        for instrument in instruments_name: 
            
            if 'PERPETUAL' in instrument:
                market_price = await self.market_price (instrument) 
                log.info (market_price)
                
                if  index_price and portfolio and market_price:
                    
                    equity = portfolio [0]['equity']
                    notional =  await self.compute_notional_value (index_price, equity)
        
                    instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 

                    min_trade_amount = instrument_data ['min_trade_amount']
                    contract_size = instrument_data ['contract_size']

                    best_bid_prc= market_price ['best_bid_prc']
                    best_ask_prc= market_price ['best_ask_prc']

                    #check under hedging
                    label_hedging = 'hedging spot'
                    #log.info (my_trades_open)
                    spot_hedged = spot_hedging.SpotHedging (label_hedging,
                                                            my_trades_open
                                                            )
                    check_spot_hedging = spot_hedged.is_spot_hedged_properly (open_orders_open_byAPI, 
                                                                            notional, 
                                                                            min_trade_amount,
                                                                            contract_size
                                                                            ) 
                    remain_unhedged = spot_hedged.compute_remain_unhedged (notional,
                                                                                 min_trade_amount,
                                                                                 contract_size
                                                                                 ) 
                    spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']
                    label: str = label_numbering.labelling ('open', label_hedging)
                    
                    log.info(f'{spot_was_unhedged=} {remain_unhedged=}')

                    if spot_was_unhedged:
                        log.warning(f'{instrument=} {best_ask_prc=} {spot_hedged=} {label=}')
                    
                        await self.send_orders ('sell', 
                                                instrument, 
                                                best_ask_prc,
                                                check_spot_hedging ['hedging_size'], 
                                                label
                                                )
                        await self.cancel_redundant_orders_in_same_labels (currency, 'hedging spot-open')
                        
                    if spot_was_unhedged == False and remain_unhedged >= 0:
                        threshold = .025/100
                        label = f'hedging spot-closed'
                        await self.price_averaging (my_trades_open, threshold, currency, index_price, check_spot_hedging ['hedging_size'], label, best_bid_prc, best_ask_prc)
                                        
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
        
        one_minute = 60000
        one_hour = one_minute * 60

        for instrument in instruments_name:
            if 'PERPETUAL' in instrument:

                #log.debug (instruments_name)
                instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]  [0] 
                min_trade_amount = instrument_data ['min_trade_amount']
                contract_size = instrument_data ['contract_size']  
                current_server_time: int = await self.current_server_time ()
                start_timestamp: int = current_server_time -  one_hour
                
                my_trades = await self.my_trades (currency, start_timestamp, current_server_time)
                
                #! THE filters need to be more sophisticated
                # the time span is long enough? (hedging i prepared for long time)
                # how to distinguish open/closed transactions? (should be thae same as the hedging method)
                
                my_trades_mgt =  myTrades_management.MyTrades (my_trades)
                my_trades_api = my_trades_mgt.my_trades_api_basedOn_label ('hedging spot')
                log.info (my_trades_api)

                spot_hedged = spot_hedging.SpotHedging ('hedging spot', my_trades_api)
            
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

        #info= (f'RUNNING ORDER \n ')
        #telegram_bot_sendtext(info,'general_error')

        await syn.running_strategy ('eth')
        #await syn.check_if_new_order_will_create_over_hedged ('eth', label_hedging)
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
        #formula.sleep_and_restart_program (30)
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
