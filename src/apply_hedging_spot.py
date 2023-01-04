#!/usr/bin/python3

import os
from os.path import join, dirname

# installed
from dataclassy import dataclass
from loguru import logger as log
import asyncio
from dotenv import load_dotenv
from os.path import join, dirname

from portfolio.deribit import open_orders_management, myTrades_management
from utils import pickling, system_tools, formula
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
class ApplyHedgingSpot ():

    
    '''
    '''       
    
    
    connection_url: str
    client_id: str
    client_secret: str
    currency: str
        
    async def open_orders_from_exchange (self) -> list:
        """
        """
        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, self.client_id, self.client_secret, self.currency)
        open_ordersREST: list = open_ordersREST ['result']
                        
        return open_orders_management.MyOrders (open_ordersREST)
        
    async def check_open_orders_consistency (self, open_orders_from_exchange: list, label: str = 'spot hedging', status: str = 'open') -> list:
        """
        db vs exchange
        """
        import synchronizing_files
        #
        get_id_for_cancel = await synchronizing_files.check_open_orders_consistency(self.currency, open_orders_from_exchange, label, 'open')
        
        if get_id_for_cancel:
            
            for open_order_id in get_id_for_cancel:
                                
                await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                             self.client_id, 
                                                             self.client_secret, 
                                                             open_order_id
                                                             )    
        
    async def my_trades (self, start_timestamp: int, end_timestamp: int) -> list:
        """
        """
        trades: list = await deribit_get.get_user_trades_by_currency_and_time (self.connection_url, 
                                                                               self.client_id, 
                                                                               self.client_secret, 
                                                                              self.currency, 
                                                                               start_timestamp,
                                                                               end_timestamp)
        #trades: list = trades ['result']
                        
        return [] if trades == [] else trades ['result'] ['trades']
    
    async def check_my_trades_consistency (self, my_trades_from_db, server_time: int) -> list:
        """
        """
        from utils import string_modification
        
        log.info (my_trades_from_db)
        if my_trades_from_db:
            # get the earliest transaction time stamp
            my_trades_from_db_min_time_stamp = min ([o['timestamp'] for o in my_trades_from_db ])
            
            # use the earliest time stamp to fetch data from exchange
            fetch_my_trades_from_system_from_min_time_stamp_to_now = await self.my_trades (my_trades_from_db_min_time_stamp, server_time)
            # compare data from exchanges. Pick only those have not recorded at system yet
            log.debug (f'{my_trades_from_db_min_time_stamp=}')
            log.warning (f'{fetch_my_trades_from_system_from_min_time_stamp_to_now=}')
            filtered_data_from_my_trades_from_exchange = string_modification.find_unique_elements (fetch_my_trades_from_system_from_min_time_stamp_to_now, 
                                                                                                my_trades_from_db
                                                                                                )
            log.info (f'{my_trades_from_db=}')
            log.error (f'{filtered_data_from_my_trades_from_exchange=}')
            # redistribute the filtered data into db
            my_trades = myTrades_management.MyTrades (filtered_data_from_my_trades_from_exchange)
            
            my_trades.distribute_trade_transaction(self.currency)
            
        
    async def get_my_trades_from_exchange (self, count = 1000) -> list:
        """
        """
        trades: list = await deribit_get.get_user_trades_by_currency (self.connection_url, 
                                                                      self.client_id, 
                                                                      self.client_secret, 
                                                                      self.currency, 
                                                                      count
                                                                      )
                        
        return [] if trades == [] else trades ['result'] ['trades']
        
    async def get_order_history_by_instrument (self, instrument: str, count: str = 1000) -> list:
        """
        """
        order_history: list = await deribit_get.get_order_history_by_instrument (self.connection_url, 
                                                                               self.client_id, 
                                                                               self.client_secret, 
                                                                               instrument,
                                                                               count)                
        return [] if order_history ==[] else order_history ['result']
        
        
    async def get_account_summary (self, currency: str) -> list:
        """
        """
        account_summary: list = await deribit_get.get_account_summary (self.connection_url, self.client_id, self.client_secret, currency)
                        
        return account_summary ['result']
    
    async def get_instruments (self) -> list:
        """
        """
    
        endpoint=(f'public/get_instruments?currency={self.currency}&expired=false&kind=future')
        result: list = await deribit_get.get_unauthenticated(self.connection_url, endpoint)
        return result ['result']
    
    async def get_index (self) -> float:
        """
        """
            
        endpoint: str = f'public/get_index?currency={self.currency.upper()}'
        result: list = await deribit_get.get_unauthenticated(self.connection_url, endpoint)
        
        return result ['result'] [self.currency.upper()]
    
    async def get_positions (self) -> list:
        """
        """
            
        result: dict =  deribit_get.get_positions (self.connection_url, 
                                                         self.client_id,
                                                         self.client_secret, 
                                                         self.currency
                                                         )
        
        return result ['result'] 
    
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
            
            await self.cancel_redundant_orders_in_same_labels_closed_hedge ()
            
        except Exception as e:
            log.error (e)
            
    async def compute_notional_value (self, index_price: float, equity: float) -> float:
        """
        """
        return index_price * equity  
    
    
    async def reading_from_database (self, instrument: str = None) -> float:
        """
        """
        my_path_ordBook: str = system_tools.provide_path_for_file ('ordBook', instrument) 
            
        my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', self.currency, 'open')
        my_trades_open: list = pickling.read_data(my_trades_path_open)  
               
        my_trades_path_closed: str = system_tools.provide_path_for_file ('myTrades', self.currency, 'closed')
        my_trades_closed: list = pickling.read_data(my_trades_path_closed) 
        
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', self.currency, 'open')
        my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', self.currency, 'closed')
        my_path_orders_filled: str = system_tools.provide_path_for_file ('orders', self.currency, 'filled')
        
        my_path_portfolio: str = system_tools.provide_path_for_file ('portfolio', self.currency.lower())      
        #log.error (my_path_portfolio)                                                                               
        portfolio = pickling.read_data(my_path_portfolio)
        
        my_path_instruments: str = system_tools.provide_path_for_file ('instruments',  self.currency)          
        instruments = pickling.read_data (my_path_instruments)
                
        symbol_index: str = f'{self.currency}_usd'
        my_path_index: str = system_tools.provide_path_for_file ('index',  symbol_index)  
        index_price: list = pickling.read_data(my_path_index) 
        index_price: float= index_price [0]['price']
        my_path_positions: str = system_tools.provide_path_for_file ('positions', 'eth') 
        positions = pickling.read_data(my_path_positions)
        if positions == None:
            positions = await self.get_positions ()
        log.error (positions)
        
        
        return {'my_trades_open': my_trades_open,
                'my_trades_closed': my_trades_closed,
                'open_orders_open_byAPI': pickling.read_data(my_path_orders_open),
                'open_orders_closed_byAPI': pickling.read_data(my_path_orders_closed),
                'open_orders_filled_byAPI': pickling.read_data(my_path_orders_filled),
                'positions': positions,
                'ordBook': pickling.read_data(my_path_ordBook),
                'portfolio': portfolio,
                'index_price': index_price,
                'instruments': instruments}
    
    async def market_price (self, instrument: str) -> list:
        """
        """

        ordBook = await self.reading_from_database (instrument)
        ordBook = ordBook ['ordBook']
        
        best_bid_prc = []
        best_ask_prc = []
        
        if ordBook :
                
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
    
    async def cancel_redundant_orders_in_same_labels (self,  label_for_filter) -> None:
        """
        """
    
        open_order_mgt = await self.open_orders_from_exchange ()
        
        len_current_open_orders = open_order_mgt.my_orders_api_basedOn_label_items_qty( label_for_filter)
        
        if len_current_open_orders != [] :
            if len_current_open_orders > 1 :
                
                open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_max_id (label_for_filter) 
                
                await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                                self.client_id,
                                                                self.client_secret, 
                                                                open_order_id
                                                                )
    async def cancel_redundant_orders_in_same_labels_closed_hedge (self) -> None:
        """
        """
        label_for_filter = 'hedging spot-closed'
    
        await self.cancel_redundant_orders_in_same_labels (label_for_filter) 
                    
    
    async def cancel_orders_hedging_spot_based_on_time_threshold (self, server_time, label) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3
        
        open_order_mgt = await self.open_orders_from_exchange ()

        try:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
        except:
            open_orders_lastUpdateTStamps: list = []    
        if open_orders_lastUpdateTStamps !=[]:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = server_time - open_orders_lastUpdateTStamp_min                       

            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_min_id (label)                        
            if open_orders_deltaTime > three_minute:
                await deribit_get.get_cancel_order_byOrderId(self.connection_url, 
                                                             self.client_id, 
                                                             self.client_secret, 
                                                             open_order_id)    
    
    async def running_strategy (self, server_time) -> float:
        """
        source data: loaded from database app
        len_current_open_orders = open_order_mgt.my_orders_api_basedOn_label_items_qty(label_for_filter)
        """

        none_data = [[], None, 0]
        #! fetch data ALL from db
        reading_from_database = await self.reading_from_database ()
        
        #!
        my_trades_closed: list = reading_from_database ['my_trades_closed']
        #log.debug (my_trades_closed)
        
        #!
        # my trades data
        my_trades_open: list = reading_from_database ['my_trades_open']
        # open orders data
        open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
        open_orders_filled_byAPI: list = reading_from_database ['open_orders_filled_byAPI']
        
        log.warning (open_orders_open_byAPI)
        # portfolio data
        portfolio = reading_from_database ['portfolio']
        # instruments data
        instruments = reading_from_database ['instruments']
        # index price
        index_price: float= reading_from_database['index_price']
        
        # prepare open order manipulation
        open_order_mgt = open_orders_management.MyOrders (open_orders_open_byAPI)
        open_order_mgt_flled = open_orders_management.MyOrders (open_orders_filled_byAPI)
        
        open_order_filled = open_order_mgt_flled.my_orders_status ('filled')
        #log.info (open_order_filled)
        if open_order_filled != []: 
            open_order_filled_latest_timeStamp = max([o['last_update_timestamp'] for o in open_order_filled] )
            filled_order_deltaTime: int = server_time - open_order_filled_latest_timeStamp  
        
        one_minute = 60000
        last_time_order_filled_exceed_threshold = True if open_order_filled == [] else filled_order_deltaTime > one_minute
        log.info(f'{last_time_order_filled_exceed_threshold=}')
        
        if last_time_order_filled_exceed_threshold :
            
            # obtain all instrument names
            instruments_name: list = [] if instruments == [] else [o['instrument_name'] for o in instruments] 
            
            for instrument in instruments_name: 
                
                # for instrument assigned as hedginng instrument, do the following:
                if 'PERPETUAL' in instrument:
                    
                    #order_history  = await self. get_order_history_by_instrument (instrument)
                    #trade_history  = await self. get_my_trades_from_exchange ()
                        
                    # get ALL bids and asks
                    market_price = await self.market_price (instrument) 
                    
                    log.info(f'{index_price=} {market_price=} {portfolio=}')
                    # if none of the followings = []
                    if  index_price and portfolio and market_price:
                        
                        # obtain spot equity
                        equity = portfolio [0]['equity']
                        
                        # compute notional value
                        notional =  await self.compute_notional_value (index_price, equity)
            
                        #! get instrument detaila
                        instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 

                        # instrument minimum order
                        min_trade_amount = instrument_data ['min_trade_amount']
                        # instrument contract size
                        contract_size = instrument_data ['contract_size']

                        # get bid and ask price
                        best_bid_prc= market_price ['best_bid_prc']
                        best_ask_prc= market_price ['best_ask_prc']

                        label_hedging = 'hedging spot'

                        #check under hedging
                        spot_hedged = spot_hedging.SpotHedging (label_hedging,
                                                                my_trades_open
                                                                )
                        check_spot_hedging = spot_hedged.is_spot_hedged_properly ( 
                                                                                notional, 
                                                                                min_trade_amount,
                                                                                contract_size
                                                                                ) 
                        remain_unhedged = spot_hedged.compute_remain_unhedged (notional,
                                                                                    min_trade_amount,
                                                                                    contract_size
                                                                                    ) 
                        min_hedging_size = check_spot_hedging ['all_hedging_size']

                        spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']

                        actual_hedging_size = spot_hedged.compute_actual_hedging_size()
                        actual_hedging_size_system = reading_from_database ['positions']
                        log.warning (actual_hedging_size_system)
                        if actual_hedging_size_system:
                            actual_hedging_size_system =  [o for o in actual_hedging_size_system if o['instrument_name'] == instrument]  [0]
                        #log.error (actual_hedging_size_system)
                        
                        if actual_hedging_size_system:
                            actual_hedging_size_system = actual_hedging_size_system ['size']
                            if actual_hedging_size_system - actual_hedging_size != 0:
                                await self.check_my_trades_consistency(my_trades_open, server_time)
                        
                        #!                    
                                info= (f'SIZE DIFFERENT size per sistem {actual_hedging_size_system} size per db {actual_hedging_size} \n ')
                                telegram_bot_sendtext(info)
                                if actual_hedging_size_system != actual_hedging_size:
                                    formula.sleep_and_restart_program (60*30)
                                 #! 

                        label: str = label_numbering.labelling ('open', label_hedging)
                        
                        label_for_filter = 'hedging'
                        
                        # check for any order outstanding as per label filter
                        net_open_orders_open_byAPI: int = open_order_mgt.my_orders_api_basedOn_label_items_net (label_for_filter)
                        
                        log.info(f'{spot_was_unhedged=} {min_hedging_size=} {actual_hedging_size=} {actual_hedging_size_system=} {remain_unhedged=} {remain_unhedged>=0 =}  {net_open_orders_open_byAPI=}')

                        # send sell order if spot still unhedged and no current open orders 
                        if spot_was_unhedged and net_open_orders_open_byAPI == 0 and actual_hedging_size_system in none_data and actual_hedging_size in none_data:
                            log.warning(f'{instrument=} {best_ask_prc=} {label=}')
                        
                            await self.send_orders ('sell', 
                                                    instrument, 
                                                    best_ask_prc,
                                                    abs(check_spot_hedging ['hedging_size']), 
                                                    label
                                                    )
                            
                            await self.cancel_redundant_orders_in_same_labels ('hedging spot-open')
                            await self.check_if_new_opened_hedging_order_will_create_over_hedged (actual_hedging_size, min_hedging_size)
                        
                        # if spot has hedged properly, check also for opportunity to get additional small profit    
                        if spot_was_unhedged == False and remain_unhedged >= 0 and net_open_orders_open_byAPI == 0:
                            threshold = .025/100
                            adjusting_inventories = spot_hedged.adjusting_inventories (index_price, threshold, 'hedging spot-open')
                            bid_prc_is_lower_than_buy_price = best_bid_prc < adjusting_inventories ['buy_Price']
                            ask_prc_is_higher_than_sell_price = best_ask_prc > adjusting_inventories ['sell_price']
                            
                            log.info(f'{bid_prc_is_lower_than_buy_price=} {best_bid_prc=} {ask_prc_is_higher_than_sell_price=} {best_ask_prc=}')
                                    
                            if adjusting_inventories ['take_profit'] and bid_prc_is_lower_than_buy_price:
                                label_closed_for_filter = 'hedging spot-closed'
                                        
                                await self.send_orders (
                                                        'buy', 
                                                        instrument, 
                                                        best_bid_prc, 
                                                        abs(adjusting_inventories ['size_take_profit']), 
                                                        adjusting_inventories ['label_take_profit']
                                                        )
                                
                                await self.cancel_redundant_orders_in_same_labels (label_closed_for_filter)
                                
                            if adjusting_inventories ['average_up'] and ask_prc_is_higher_than_sell_price:
                                label_open_for_filter = 'hedging spot-open'
                                        
                                await self.send_orders (
                                                        'sell', 
                                                        instrument, 
                                                        best_ask_prc, 
                                                        check_spot_hedging ['average_up_size'], 
                                                        label
                                                        )
                                
                                await self.cancel_redundant_orders_in_same_labels (label_open_for_filter)
                            

    async def check_if_new_opened_hedging_order_will_create_over_hedged (self,  actual_hedging_size, min_hedging_size)-> None:
        
        '''
        '''   
        
        from time import sleep
        
        #refresh open orders
        reading_from_database = await self.reading_from_database ()
        open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
        log.info(f'{open_orders_open_byAPI=}')
        open_order_mgt =  open_orders_management.MyOrders (open_orders_open_byAPI)
        label_open = 'hedging spot-open'
        current_open_orders_size = open_order_mgt.my_orders_api_basedOn_label_items_size(label_open)
        current_open_orders_size = 0 if current_open_orders_size ==[] else current_open_orders_size

        is_over_hedged = actual_hedging_size + current_open_orders_size > min_hedging_size
        log.info(f'{is_over_hedged=} {actual_hedging_size=} {current_open_orders_size=} {min_hedging_size=}')
        
        if  is_over_hedged:
            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_max_id (label_open)
            
            sleep (2)
            
            await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                            self.client_id,
                                                            self. client_secret, 
                                                            open_order_id
                                                            )
async def main ():
    
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    connection_url: str = 'wss://www.deribit.com/ws/api/v2'
    
    connection_url: str = 'https://test.deribit.com/api/v2/'
    client_id: str = parse_dotenv() ['client_id']
    client_secret: str = parse_dotenv() ['client_secret']
    currency: str = 'ETH'
    
    try:

        syn = ApplyHedgingSpot (
        connection_url=connection_url,
        client_id=client_id,
        client_secret= client_secret,
        currency = currency
        )
        label_hedging = 'hedging spot'
        
        
        server_time = await syn.current_server_time ()
        await syn.running_strategy (server_time)
        #await syn.check_if_new_order_will_create_over_hedged ('eth', label_hedging)
        await syn.cancel_orders_hedging_spot_based_on_time_threshold (server_time, label_hedging)
        await syn.cancel_redundant_orders_in_same_labels_closed_hedge ()        
        open_orders_from_exchange = await syn.open_orders_from_exchange ()        
        await syn.check_open_orders_consistency (open_orders_from_exchange, label_hedging)
         
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
        import synchronizing_files
        asyncio.get_event_loop().run_until_complete(main())
        synchronizing_files.main()
        is_running = system_tools.is_current_file_running ('apply_hedging_spot.py')
        if is_running:
            import sys
            sys.exit()
        
        formula.sleep_and_restart_program (30)
        
    except (KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_until_complete(main().stop_ws())

    except Exception as error:
        formula.log_error('app','name-try2', error, 10)
