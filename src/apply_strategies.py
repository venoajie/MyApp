#!/usr/bin/python3

# built ins
import os
from os.path import join, dirname

# installed
from dataclassy import dataclass
from loguru import logger as log
import asyncio
from dotenv import load_dotenv
from os.path import join, dirname

# user defined formula 
from portfolio.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools, number_modification, string_modification
import deribit_get
from risk_management import spot_hedging, check_data_integrity, position_sizing
from configuration import  label_numbering
from strategies import entries_exits, trading_strategies

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def telegram_bot_sendtext(bot_message, purpose: str = 'general_error') -> None:
    from utilities import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

def catch_error (error, idle: int = None) -> list:
    """
    """
    system_tools.catch_error_message(error, idle)

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
        
    async def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        return number_modification.net_position (selected_transactions)
    
    async def get_open_orders_from_exchange (self) -> list:
        """
        """
        open_ordersREST: list = await deribit_get.get_open_orders_byCurrency (self.connection_url, 
                                                                              self.client_id, 
                                                                              self.client_secret, 
                                                                              self.currency
                                                                              )                        
        return open_ordersREST ['result']
        
    async def open_orders_from_exchange (self) -> object:
        """
        """
        open_ordersREST: list = await self.get_open_orders_from_exchange()
                        
        return open_orders_management.MyOrders (open_ordersREST)
        
    async def check_open_orders_consistency (self, open_orders_from_exchange: list, 
                                             label: str = 'spot hedging', 
                                             status: str = 'open') -> list:
        """
        db vs exchange
        will be combined with check_my_orders_consistency
        """
        import synchronizing_files
        #
        get_id_for_cancel = await synchronizing_files.check_open_orders_consistency (self.currency, 
                                                                                     open_orders_from_exchange, 
                                                                                     label, 
                                                                                     status
                                                                                     )
        
        if get_id_for_cancel:
            
            for open_order_id in get_id_for_cancel:
                                
                await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                             self.client_id, 
                                                             self.client_secret, 
                                                             open_order_id
                                                             )    
        
    async def my_trades_time_constrained (self, 
                         start_timestamp: int, 
                         end_timestamp: int
                         ) -> list:
        """
        basis to recover data
        """
        trades: list = await deribit_get.get_user_trades_by_currency_and_time (self.connection_url, 
                                                                               self.client_id, 
                                                                               self.client_secret, 
                                                                              self.currency, 
                                                                               start_timestamp,
                                                                               end_timestamp
                                                                               )     
                     
        try:
            result = [] if trades == [] else trades ['result'] ['trades']
        
            my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                            self.currency,
                                                                            'all-recovery-point'
                                                                            )          
            pickling.replace_data (my_trades_path_open_recovery, 
                                    result, 
                                    True
                                    )
        except:
            result =   trades ['error'] ['data'] ['reason']
            if result  == 'timestamp_of_archived_trade':
                log.critical(result)
            
        return result
    
    async def get_my_trades_from_exchange (self, count: int = 1000) -> list:
        """
        """
        trades: list = await deribit_get.get_user_trades_by_currency (self.connection_url, 
                                                                      self.client_id, 
                                                                      self.client_secret, 
                                                                      self.currency, 
                                                                      count
                                                                      )
                        
        return [] if trades == [] else trades ['result'] ['trades']
        
    async def check_my_orders_consistency (self, 
                                           my_orders_from_db: list, 
                                           server_time: int
                                           ) -> list:
        """
        """
        from utilities import string_modification
        
        if my_orders_from_db:
            # get the earliest transaction time stamp
            my_orders_from_db_min_time_stamp = min ([o['creation_timestamp'] for o in my_orders_from_db ])
            
            # use the earliest time stamp to fetch data from exchange
            fetch_my_orders_from_system_from_min_time_stamp_to_now = await self.my_trades_time_constrained (my_orders_from_db_min_time_stamp, server_time)
            
            # compare data from exchanges. Pick only those have not recorded at system yet
            filtered_data_from_ = string_modification.find_unique_elements (fetch_my_orders_from_system_from_min_time_stamp_to_now, 
                                                                                                my_orders_from_db
                                                                                                )
            # redistribute the filtered data into db
            myorders = open_orders_management.MyOrders (filtered_data_from_)
            
            myorders.distribute_order_transactions (self.currency)
        else:
            myorders = open_orders_management.MyOrders ([])
            await myorders.distribute_order_transactions (self.currency)
        
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
    
    async def get_positions (self) -> list:
        """
        """
            
        result: dict =  await deribit_get.get_positions (self.connection_url, 
                                                         self.client_id,
                                                         self.client_secret, 
                                                         self.currency
                                                         )
        return result ['result'] 
    
    async def send_orders (self, 
                           side: str,
                           instrument: str, 
                           size: float = None, 
                           label: str = None,
                           prc: float = None, 
                           type: str = 'limit',
                           trigger_price: float = None
                           ) -> None:
        """
        """

        try:
            if 'market' in type:
                result =  (await deribit_get.send_order (self.connection_url,
                                                self.client_id, 
                                                self.client_secret, 
                                                side, 
                                                instrument, 
                                                size, 
                                                label,
                                                None,
                                                type,
                                                trigger_price
                                                ))
            else:
                result =  (await deribit_get.send_order (self.connection_url,
                                                self.client_id, 
                                                self.client_secret, 
                                                side, 
                                                instrument, 
                                                size, 
                                                label,
                                                prc
                                                ))
            
            await self.cancel_redundant_orders_in_same_labels_closed_hedge ()
            return result
            
        except Exception as e:
            log.error (e)
            
    async def compute_notional_value (self, 
                                      index_price: float, 
                                      equity: float
                                      ) -> float:
        """
        """
        return index_price * equity  
    
    async def reading_from_database (self, instrument: str = None) -> float:
        """
        """
        my_path_ordBook: str = system_tools.provide_path_for_file ('ordBook', instrument) 
            
        my_trades_path_open: str = system_tools.provide_path_for_file ('myTrades', self.currency, 'open')               
        my_trades_open: str = pickling.read_data(my_trades_path_open)               
        my_trades_path_closed: str = system_tools.provide_path_for_file ('myTrades', self.currency, 'closed')
        my_trades_closed: str = pickling.read_data(my_trades_path_closed)             
        
        my_path_orders_open: str = system_tools.provide_path_for_file ('orders', self.currency, 'open')
        my_path_orders_closed: str = system_tools.provide_path_for_file ('orders', self.currency, 'closed')
        my_path_orders_filled: str = system_tools.provide_path_for_file ('orders', self.currency, 'filled')
        
        my_path_portfolio: str = system_tools.provide_path_for_file ('portfolio', self.currency)      
        
        my_path_instruments: str = system_tools.provide_path_for_file ('instruments',  self.currency)          
                
        symbol_index: str = f'{self.currency}_usd'
        my_path_index: str = system_tools.provide_path_for_file ('index',  symbol_index)  
        index_price: list = pickling.read_data(my_path_index) 
        my_path_positions: str = system_tools.provide_path_for_file ('positions', self.currency) 
        positions = pickling.read_data(my_path_positions)
        portfolio = pickling.read_data(my_path_portfolio)
        open_order = pickling.read_data(my_path_orders_open)
        #log.error (open_order)
        none_data = [None, [], 0]
        
        # at start, usually position == None
        if positions in none_data:
            positions = await self.get_positions ()
            pickling.replace_data (my_path_positions, positions)  
            
        #log.debug (portfolio)
        if portfolio in none_data:
            portfolio = await self.get_account_summary(self.currency)
            pickling.replace_data (my_path_portfolio, portfolio) 
            portfolio = pickling.read_data(my_path_portfolio)       
        
        return {'my_trades_open': [] if my_trades_open in none_data else my_trades_open,
                'my_trades_closed': [] if my_trades_closed in none_data else my_trades_closed,
                'open_orders_open_byAPI': pickling.read_data(my_path_orders_open),
                'open_orders_closed_byAPI': pickling.read_data(my_path_orders_closed),
                'open_orders_filled_byAPI': pickling.read_data(my_path_orders_filled),
                'positions': positions,
                'ordBook': pickling.read_data(my_path_ordBook),
                'portfolio': portfolio,
                'index_price': index_price [0]['price'],
                'instruments': pickling.read_data (my_path_instruments)}
    
    async def position_per_instrument (self, positions, instrument: str) -> list:
        """
        """
        try:
            position  = [o for o in positions if o['instrument_name'] == instrument] 
            if position:
                position  = position  [0]
            #log.warning (position)
        except:
            my_path_positions: str = system_tools.provide_path_for_file ('positions', self.currency) 
            log.debug (my_path_positions)
            positions = await self.get_positions ()
            pickling.replace_data (my_path_positions, positions)   
            position = await self.reading_from_database ()   
            position = position ['positions']  
            log.warning (position)
            position  = [o for o in positions if o['instrument_name'] == instrument]  [0]
        return position
                
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
        #log.debug(f'{open_order_mgt=}')
        #log.debug(f'{len_current_open_orders=}')
        
        
        if len_current_open_orders != [] :
            if len_current_open_orders > 1 :
                #log.critical(f'{len_current_open_orders > 1=}')
                
                open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_max_id (label_for_filter) 
                
                cancel = await self.cancel_by_order_id (open_order_id)
                #log.critical(f'{cancel=}')
                return (cancel)
                
    async def cancel_redundant_orders_in_same_labels_closed_hedge (self) -> None:
        """
        """
        label_for_filter = 'hedgingSpot-closed'
    
        cancel = await self.cancel_redundant_orders_in_same_labels (label_for_filter) 
        #log.critical(f'{cancel=}')
        return (cancel)
        
    async def get_instruments_with_rebates (self, instruments, server_time) -> None:
        """
        """
        instruments_with_rebates = [o for o in instruments if o['maker_commission'] < 0 ]

        instruments_with_rebates_weekly = [o for o in instruments_with_rebates if o['settlement_period'] == 'week' ]

        instruments_with_rebates_weekly_longest_expiration = max([o['expiration_timestamp'] for o in instruments_with_rebates_weekly ])
        instruments_with_rebates_weekly_longest_expiration_ms_before_expiration = instruments_with_rebates_weekly_longest_expiration - server_time 
        instruments_with_rebates_weekly_longest_expiration_hours_before_expiration = (instruments_with_rebates_weekly_longest_expiration_ms_before_expiration/(60000))/60
        instruments_with_rebates_longest_expiration_days_before_expiration = instruments_with_rebates_weekly_longest_expiration_hours_before_expiration/24
    
        return {'instruments_with_rebates': instruments_with_rebates,
                'instruments_with_rebates_weekly': instruments_with_rebates_weekly,
                'instruments_with_rebates_weekly_longest_exp_days_before_expiration': instruments_with_rebates_longest_expiration_days_before_expiration,
                'instruments_with_rebates_weekly_longest_exp': [o for o in instruments_with_rebates if o['expiration_timestamp'] == instruments_with_rebates_weekly_longest_expiration ],
                }

    
    async def cancel_orders_hedging_spot_based_on_time_threshold (self, server_time, label) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3
        
        
        open_orders_from_exch = await self.get_open_orders_from_exchange ()
        open_order_mgt = open_orders_management.MyOrders (open_orders_from_exch)
        open_order_label = open_orders_management.my_orders_api_basedOn_label(label)
        open_order_mgt = open_orders_management.MyOrders (open_order_label)

        try:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
        except:
            open_orders_lastUpdateTStamps: list = []    
        if open_orders_lastUpdateTStamps !=[]:
            open_orders_lastUpdateTStamps: list = open_order_mgt.my_orders_api_last_update_timestamps()
            log.critical (open_orders_lastUpdateTStamps)
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = server_time - open_orders_lastUpdateTStamp_min                       

            open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_min_id (label)                        
            if open_orders_deltaTime > three_minute:
                log.critical (label)
                log.critical (open_orders_deltaTime)
                log.critical (f'{server_time}')
                log.critical (f'{open_orders_lastUpdateTStamp_min}')
                log.critical (f'{open_orders_deltaTime=} {server_time=} {open_orders_lastUpdateTStamp_min=}')
                
                await self.cancel_by_order_id (open_order_id)    
    
    async def cancel_by_order_id (self, open_order_id) -> None:
        
        await deribit_get.get_cancel_order_byOrderId (self.connection_url, 
                                                      self.client_id, 
                                                      self.client_secret, 
                                                      open_order_id
                                                      )  
    async def check_integrity (self, 
                               positions_from_get, 
                               my_trades_open_from_db, 
                               server_time
                               ) -> None:
        
        myTrades_from_db = await check_data_integrity.myTrades_originally_from_db(self.currency)
        
        # get the earliest transaction time stamp
        start_timestamp = myTrades_from_db['time_stamp_to_recover']
        #log.critical (positions_from_get)
        #log.info (my_trades_open_from_db)
        #log.critical (start_timestamp)
        
        my_selected_trades_open_from_system =[]
        if start_timestamp:
            
            # use the earliest time stamp to fetch data from exchange
            my_selected_trades_open_from_system = await self.my_trades_time_constrained (start_timestamp, server_time)
        
        data_integrity =  check_data_integrity.CheckDataIntegrity (self.currency,
                                                                       positions_from_get,
                                                                       my_trades_open_from_db,
                                                                       my_selected_trades_open_from_system
                                                                       )
        
        inventory_per_db_vs_system_comparation = await data_integrity.compare_inventory_per_db_vs_system ()
        log.critical (inventory_per_db_vs_system_comparation)
        #log.warning (my_trades_open_from_db)
        
        
        if inventory_per_db_vs_system_comparation != 0:
            log.info (inventory_per_db_vs_system_comparation)
            await data_integrity.rearrange_my_trades_consistency (server_time)
            
        if inventory_per_db_vs_system_comparation == 0:          
            
            my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                            self.currency,
                                                                            'open-recovery-point'
                                                                            )          
            pickling.replace_data (my_trades_path_open_recovery, 
                                    my_trades_open_from_db, 
                                    True
                                    )
            
        if start_timestamp:
            
            # use the earliest time stamp to fetch data from exchange
            my_trades_time_constrd = await self.my_trades_time_constrained (start_timestamp, server_time)
            
        
    async def running_strategy (self, server_time) -> float:
        """
        source data: loaded from database app
        len_current_open_orders = open_order_mgt.my_orders_api_basedOn_label_items_qty(label_for_filter)
        """

        #! fetch data ALL from db
        try:

            reading_from_database: dict = await self.reading_from_database ()
            
            #!
            # portfolio data
            portfolio: list = reading_from_database ['portfolio']
            #log.warning (portfolio)
            
            # obtain spot equity
            equity: float = portfolio [0]['equity']
            
            # index price
            index_price: float= reading_from_database['index_price']
        
            # compute notional value
            notional: float =  await self.compute_notional_value (index_price, equity)
                               
            if  index_price and portfolio :                
                
                one_minute: int = 60000 # one minute in millisecond
                none_data: None = [0, None, []] # to capture none 
                
                # fetch positions for all instruments
                positions: list = reading_from_database ['positions']
                #log.error (positions)
            
                # my trades data
                my_trades_open: list = reading_from_database ['my_trades_open']
                my_trades_open_mgt: list = myTrades_management.MyTrades (my_trades_open)
                #log.info (my_trades_open)
                
                # fetch instruments data
                instruments = reading_from_database ['instruments']

                # instruments future
                instruments_future = [o for o in instruments if o['kind'] == 'future']
                
                # obtain instruments future with rebates
                rebates = await self.get_instruments_with_rebates (instruments, server_time)
                rebates = rebates ['instruments_with_rebates_weekly_longest_exp'][0]

                # obtain instruments future relevant to strategies
                instrument_transactions = [o['instrument_name'] for o in instruments_future \
                    if o['instrument_name']   in [f'{self.currency.upper()}-PERPETUAL' , rebates['instrument_name']] ]
                instrument_transactions = [f'{self.currency.upper()}-PERPETUAL']

                # open orders data
                open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
                open_orders_filled_byAPI: list = reading_from_database ['open_orders_filled_byAPI']
                
                # prepare open order manipulation
                open_order_mgt = open_orders_management.MyOrders (open_orders_open_byAPI)
                log.info (open_order_mgt)
                open_order_mgt_filed = open_orders_management.MyOrders (open_orders_filled_byAPI)
                #log.warning (open_order_mgt_filed)
                
                open_order_mgt_filed_status_filed = open_order_mgt_filed.my_orders_status ('filled')
                
                await self.check_integrity (positions,
                                            my_trades_open, 
                                            server_time
                                            )
                
                for instrument in instrument_transactions:

                    log.critical (f'{instrument}') 
                    market_price = await self.market_price (instrument) 
                    
                    # get bid and ask price
                    best_bid_prc= market_price ['best_bid_prc']
                    best_ask_prc= market_price ['best_ask_prc']
                                        
                    notional =  await self.compute_notional_value (index_price, equity)
    
                    #! get instrument detaila
                    instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 

                    # instrument minimum order
                    min_trade_amount = instrument_data ['min_trade_amount']
                    
                    # instrument contract size
                    contract_size = instrument_data ['contract_size']
                    
                    open_order_mgt_from_exchange = await self.open_orders_from_exchange()
                    #log.warning (f'open_order_mgt_from_exchange {open_order_mgt_from_exchange}') 
                    my_orders_from_exchange = await self.get_open_orders_from_exchange()
                    log.debug (f'my_orders_from_exchange {my_orders_from_exchange}') 

                    net_open_orders_open_byAPI_system: int = open_order_mgt_from_exchange.my_orders_api_basedOn_label_items_net ()
                    log.warning (f'net_open_orders_open_byAPI_system {net_open_orders_open_byAPI_system}') 
                    
                    # check for any order outstanding as per label filter
                    net_open_orders_open_byAPI_db: int = open_order_mgt.my_orders_api_basedOn_label_items_net ()
                    log.error (f'net_open_orders_open_byAPI_db {net_open_orders_open_byAPI_db}') 
                
                                        
                    # fetch strategies 
                    strategies = entries_exits.strategies
            
                    for strategy in strategies:
                                                
                        #strategy_variables = [o for o in strategies if o['strategy'] == strategy] [0] 
                
                        pct_threshold_TP: float = strategy ['take_profit_pct']  
                        pct_threshold_avg: float = strategy ['averaging']  
                        time_threshold: float = strategy ['halt_minute_before_reorder']  * one_minute 
                        
                        label:str = strategy ['strategy']
                        label_numbered: str = label_numbering.labelling ('open', label)
                        label_closed:str = f'{label}-closed'
                        
                        # create my order mgt template based on strategies
                        my_orders_api_basedOn_label_strategy: list = open_order_mgt.my_orders_api_basedOn_label (label)
                        
                        #! hedging spot: part of risk management, not strategies
                        if 'hedgingSpot' not in strategy['strategy']:
                            log.debug(f'{label=} {my_orders_api_basedOn_label_strategy=}')
                            str = trading_strategies.main (strategy,
                                                index_price,
                                                my_trades_open,
                                                my_orders_api_basedOn_label_strategy,
                                                notional,
                                                instrument
                                                )
                            open_str_buy = str ['open_strategy_buy']
                            open_str_sell = str ['open_strategy_sell']
                            closed_str = str ['closed_strategy']
                                
                            log.warning (open_str_sell)
                            log.warning (open_str_buy)
                            
                            log.warning (closed_str)
                            
                            if open_str_sell!= None and open_str_sell ['send_order']:
                                side = open_str_sell['side']
                                log.info (open_str_sell['cl_price'])
                                order_result = await self.send_orders (side, 
                                                        open_str_sell['instrument'],
                                                        open_str_sell['size'], 
                                                        open_str_sell['label_numbered'],
                                                        open_str_sell['entry_price']
                                                        )
                                log.info (order_result)
                                log.info ('error' not in order_result)
                                order_result_id = order_result['result']['order']['order_id']
                                if 'error'  in order_result:   
                                    await self.cancel_by_order_id (order_result_id)
                                else:   
                                    order_result = await self.send_orders ('buy', 
                                                        open_str_sell['instrument'],
                                                        open_str_sell['size'], 
                                                        open_str_sell['label_closed_numbered'],
                                                        None,
                                                        'stop_market',
                                                        open_str_sell['cl_price']                                                        
                                                        )
                                    if 'error'  in order_result:   
                                        await self.cancel_by_order_id (order_result_id)
                                log.info (order_result)
                                
                            if open_str_buy!= None and open_str_buy ['send_order']:
                                side = open_str_buy['side']
                                log.info (open_str_buy['cl_price'])
                                order_result = await self.send_orders (side, 
                                                        open_str_buy['instrument'],
                                                        open_str_buy['size'], 
                                                        open_str_buy['label_numbered'],
                                                        open_str_buy['entry_price']
                                                        )
                                log.info (order_result)
                                order_result_id = order_result['result']['order']['order_id']
                                if 'error'  in order_result:   
                                    await self.cancel_by_order_id (order_result_id)
                                
                                if 'error' not in order_result:
                                    order_result = await self.send_orders ('sell', 
                                                        open_str_buy['instrument'],
                                                        open_str_buy['size'], 
                                                        open_str_buy['label_closed_numbered'],
                                                        None,
                                                        'stop_market',
                                                        open_str_buy['cl_price']
                                                        )
                                    if 'error'  in order_result:   
                                        await self.cancel_by_order_id (order_result_id)
                                    log.info (order_result)

                            if closed_str!= None and closed_str ['send_order']:
                                side = closed_str['side']
                                cut_loss = closed_str['cut_loss']
                                if cut_loss == True:
                                    pass
                                else:
                                    await self.send_orders  (side, 
                                                        closed_str['instrument'],
                                                        closed_str['size'], 
                                                        closed_str['label_numbered'],
                                                        best_ask_prc if side == 'sell' else best_bid_prc
                                                        )
                            
                        log.warning (strategy['strategy'])
                        #log.warning ('hedgingSpot' in strategy['strategy'])
                            
                        if 'hedgingSpot' in strategy['strategy']:
                                                
                            if net_open_orders_open_byAPI_system - net_open_orders_open_byAPI_db != 0:
                                await self.check_my_orders_consistency (my_orders_from_exchange, server_time)
                                
                                log.debug(f'{net_open_orders_open_byAPI_system=} {net_open_orders_open_byAPI_system - net_open_orders_open_byAPI_db =}')
                        
                            if open_order_mgt_filed_status_filed != []: 
                                open_order_filled_latest_timeStamp = max([o['last_update_timestamp'] for o in open_order_mgt_filed_status_filed] )
                                filled_order_deltaTime: int = server_time - open_order_filled_latest_timeStamp  
                                                                   
                            last_time_order_filled_exceed_threshold = True if open_order_mgt_filed_status_filed == [] \
                                else filled_order_deltaTime > time_threshold
                            
                            if 'PERPETUAL' in instrument :
                                if last_time_order_filled_exceed_threshold:

                                    #check under hedging
                                    spot_hedged = spot_hedging.SpotHedging (label,
                                                                            my_trades_open
                                                                            )
                                    
                                    check_spot_hedging = spot_hedged.is_spot_hedged_properly (notional, 
                                                                                              min_trade_amount,
                                                                                              contract_size
                                                                                              ) 
                                    
                                    remain_unhedged = check_spot_hedging ['remain_unhedged_size']
                                    
                                    min_hedging_size = check_spot_hedging ['all_hedging_size']

                                    spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']

                                    actual_hedging_size = spot_hedged.compute_actual_hedging_size()
                                    
                                    label_open_for_filter = f'{label}-open'

                                    log.debug(f'{label=} {label_open_for_filter=}')
                                    
                                    # check for any order outstanding as per label filter
                                    net_open_orders_open_byAPI_db: int = open_order_mgt.my_orders_api_basedOn_label_items_net (label)
                                    log.warning(f'{spot_was_unhedged=} {actual_hedging_size=}  {net_open_orders_open_byAPI_db=} {last_time_order_filled_exceed_threshold=}')
                                    
                                    await self.will_new_open_order_create_over_hedge (label,
                                                                                      actual_hedging_size,
                                                                                      min_hedging_size
                                                                                      )
                                    
                                    # send sell order if spot still unhedged and no current open orders 
                                    if spot_was_unhedged \
                                        and net_open_orders_open_byAPI_db == 0 \
                                            and  last_time_order_filled_exceed_threshold:
                                    
                                        await self.send_orders ('sell', 
                                                                instrument, 
                                                                abs(check_spot_hedging ['hedging_size']), 
                                                                label_numbered,
                                                                best_ask_prc
                                                                )
                                        #log.warning (order_result)
                                        
                                        await self.cancel_redundant_orders_in_same_labels (label_open_for_filter)
                                        
                                        await self.will_new_open_order_create_over_hedge (label,
                                                                                          actual_hedging_size,
                                                                                          min_hedging_size
                                                                                          )
                                    
                                    # if spot has hedged properly, check also for opportunity to get additional small profit    
                                    if spot_was_unhedged == False \
                                        and remain_unhedged >= 0 \
                                            and net_open_orders_open_byAPI_db == 0:

                                        adjusting_inventories = spot_hedged.adjusting_inventories (index_price, 
                                                                                                   self.currency, 
                                                                                                   pct_threshold_TP, 
                                                                                                   pct_threshold_avg, 
                                                                                                   label_open_for_filter
                                                                                                   )
                                        bid_prc_is_lower_than_buy_price = best_bid_prc < adjusting_inventories ['buy_price']
                                        ask_prc_is_higher_than_sell_price = best_ask_prc > adjusting_inventories ['sell_price']
                                        
                                        log.info(f' {label_numbered=} {bid_prc_is_lower_than_buy_price=} \
                                            {best_bid_prc=} {ask_prc_is_higher_than_sell_price=} \
                                                {best_ask_prc=}')
                                                
                                        if adjusting_inventories ['take_profit'] \
                                            and bid_prc_is_lower_than_buy_price:                                            
                                                    
                                            order_result = await self.send_orders ('buy', 
                                                                    instrument, 
                                                                    abs(adjusting_inventories ['size_take_profit']), 
                                                                    adjusting_inventories ['label_take_profit'],
                                                                    best_bid_prc
                                                                    )
                                            log.warning (order_result)
                                            
                                            await self.cancel_redundant_orders_in_same_labels (label_closed)
                                            
                                        if adjusting_inventories ['average_up'] \
                                            and ask_prc_is_higher_than_sell_price:
                                            
                                            order_result = await self.send_orders (
                                                                    'sell', 
                                                                    instrument,
                                                                    check_spot_hedging ['average_up_size'], 
                                                                    label_numbered,
                                                                    best_ask_prc
                                                                    )
                                            log.warning (order_result)
                                            
                                            await self.cancel_redundant_orders_in_same_labels (label_open_for_filter)
                                
        except Exception as error:
            catch_error (error, 30)

    async def will_new_open_order_create_over_hedge (self,  
                                                    label,
                                                    actual_hedging_size: float, 
                                                    min_hedging_size: float
                                                    )-> None:
        
        '''
        '''   
        
        from time import sleep
        
        try:
            
            #refresh open orders
            reading_from_database: dict = await self.reading_from_database ()
            open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
            
            #log.info(f'{open_orders_open_byAPI=}')
            open_order_mgt =  open_orders_management.MyOrders (open_orders_open_byAPI)
            label_open = f'{label}-open'
            current_open_orders_size = open_order_mgt.my_orders_api_basedOn_label_items_size(label_open)
            current_open_orders_size = 0 if current_open_orders_size ==[] else current_open_orders_size

            is_over_hedged = actual_hedging_size + current_open_orders_size < min_hedging_size
            log.info(f'{is_over_hedged=} {actual_hedging_size=} {current_open_orders_size=} {min_hedging_size=}')
            
            if  is_over_hedged:
                open_order_id: list = open_order_mgt.my_orders_api_basedOn_label_last_update_timestamps_max_id (label_open)
                log.critical(f'{open_order_id=}')
                
                sleep (2)
                
                await self.cancel_by_order_id (open_order_id)
            
        except Exception as error:
            catch_error (error)
            
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
        label_hedging = 'hedgingSpot'
        
        server_time = await syn.current_server_time ()
        #log.error (server_time+60000)
        await syn.running_strategy (server_time)
        #await syn.check_if_new_order_will_create_over_hedged ('eth', label_hedging)
        await syn.cancel_orders_hedging_spot_based_on_time_threshold (server_time, label_hedging)
        await syn.cancel_redundant_orders_in_same_labels_closed_hedge ()        
        #open_orders_from_exchange = await syn.open_orders_from_exchange ()        
        #await syn.check_open_orders_consistency (open_orders_from_exchange, label_hedging)
         
    except Exception as error:
        catch_error (error, 30)
    
if __name__ == "__main__":

    try:
        import synchronizing_files
        
        asyncio.get_event_loop().run_until_complete(main())
        
        synchronizing_files.main()
        
        # only one file is allowed to running
        is_running = system_tools.is_current_file_running ('apply_hedging_spot.py')
        
        if is_running:
            catch_error (is_running)
        
        system_tools.sleep_and_restart_program (30)

    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 30)
