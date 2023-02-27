#!/usr/bin/python3

# built ins

# installed
from dataclassy import dataclass
from loguru import logger as log
import asyncio

# user defined formula 
from portfolio.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools#, number_modification, string_modification
import deribit_get
from risk_management import spot_hedging, check_data_integrity#, position_sizing
from configuration import  label_numbering, config
from strategies import entries_exits, trading_strategies
from market_understanding import futures_analysis

async def telegram_bot_sendtext (bot_message, 
                           purpose: str = 'general_error'
                           ) -> None:

    return await deribit_get.telegram_bot_sendtext (bot_message,
                                 purpose
                                 )
def catch_error (error, 
                 idle: int = None
                 ) -> list:
    """
    """
    system_tools.catch_error_message(error, 
                                     idle
                                     )

def parse_dotenv(sub_account)->dict:    
    return config.main_dotenv (sub_account)                                                         

@dataclass(unsafe_hash=True, slots=True)
class ApplyHedgingSpot ():
    
    '''
    '''       
    
    connection_url: str
    client_id: str
    client_secret: str
    currency: str
        
    async def get_private_data(self) -> list:
        """
        Provide class object to access private get API
        """
        
        try:
            
            return deribit_get.GetPrivateData (self.connection_url, 
                                               self.client_id,
                                               self.client_secret,
                                               self.currency
                                               )
        except Exception as error:
            catch_error (error)
        
    async def get_sub_accounts(self) -> list:
        """
        """
        
        try:
            private_data = await self. get_private_data()
            result: dict =  await private_data.get_subaccounts()
            return result ['result'] 
    
        except Exception as error:
            catch_error (error)
    
    async def get_open_orders_from_exchange (self) -> list:
        """
        """
    
        private_data = await self. get_private_data()
        open_ordersREST: dict =  await private_data.get_open_orders_byCurrency()         
        return open_ordersREST ['result']
        
    async def open_orders_from_exchange (self) -> object:
        """
        """
        open_ordersREST: list = await self.get_open_orders_from_exchange()
                        
        return open_orders_management.MyOrders (open_ordersREST)
        
    async def my_trades_time_constrained (self, 
                                        start_timestamp: int, 
                                        end_timestamp: int
                                        ) -> list:
        """
        basis to recover data
        """
        
        private_data = await self. get_private_data()
        trades: dict =  await private_data.get_user_trades_by_currency_and_time( 
                                                                               start_timestamp,
                                                                               end_timestamp
                                                                               )     
                     
        try:
            result = [] if trades == [] else trades ['result'] ['trades']
        
            path_trades_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                            self.currency,
                                                                            'all-recovery-point'
                                                                            )          
            pickling.replace_data (path_trades_open_recovery, 
                                    result, 
                                    True
                                    )
        except:
            result =   trades ['error'] ['data'] ['reason']
            if result  == 'timestamp_of_archived_trade':
                log.critical(result)
            
        return result
    
    async def get_my_trades_from_exchange (self, 
                                           count: int = 1000
                                           ) -> list:
        """
        """
        private_data = await self. get_private_data()
        trades: list = await private_data.get_user_trades_by_currency (count)
                        
        return [] if trades == [] else trades ['result'] ['trades']
        
    async def get_account_summary (self) -> list:
        """
        """
    
        private_data = await self. get_private_data()

        account_summary: dict =  await private_data.get_account_summary()
            
        return account_summary ['result']
    
    async def get_positions (self) -> list:
        """
        """
        
        private_data = await self. get_private_data()

        result: dict =  await private_data.get_positions()
        
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
            private_data = await self. get_private_data()
            
            if 'market' in type:
                result =  (await private_data.send_order (                                                
                                                side, 
                                                instrument, 
                                                size, 
                                                label,
                                                None,
                                                type,
                                                trigger_price
                                                ))
            else:
                result =  (await private_data.send_order ( 
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
    
    async def reading_from_db (self, 
                               end_point,
                               instrument: str = None, 
                               status: str =None
                               ) -> float:
        """
        """
        return pickling.read_data (system_tools.provide_path_for_file (end_point,
                                                                       instrument,
                                                                       status
                                                                       ) 
                                   )
                
    async def reading_from_database (self, instrument: str = None) -> float:
        """
        """
        
        path_sub_accounts: str = system_tools.provide_path_for_file ('sub_accounts', 
                                                                     self.currency
                                                                     )  
                     
        path_trades_open: str = system_tools.provide_path_for_file ('myTrades', 
                                                                    self.currency, 
                                                                    'open'
                                                                    )   
                    
        my_trades_open: str = pickling.read_data(path_trades_open)   
        
        path_orders_open: str = system_tools.provide_path_for_file ('orders', 
                                                                    self.currency, 
                                                                    'open'
                                                                    )
        
        path_orders_filled: str = system_tools.provide_path_for_file ('orders', 
                                                                      self.currency, 
                                                                      'filled'
                                                                      )
        
        path_portfolio: str = system_tools.provide_path_for_file ('portfolio', 
                                                                  self.currency
                                                                  ) 
                
        symbol_index: str = f'{self.currency}_usd'
        path_index: str = system_tools.provide_path_for_file ('index',  
                                                              symbol_index
                                                              )  
        ticker_perpetual: list = await self.reading_from_db ('ticker', 
                                                         f'{(self.currency).upper()}-PERPETUAL'
                                                         )
        symbol_index: str = f'{self.currency}_usd'
        path_index: str = system_tools.provide_path_for_file ('index', 
                                                              symbol_index
                                                              )  
        index_price: list = pickling.read_data(path_index)
        path_positions: str = system_tools.provide_path_for_file ('positions', 
                                                                  self.currency
                                                                  ) 
        positions = pickling.read_data(path_positions)
        sub_account = pickling.read_data(path_sub_accounts)
        positions_from_sub_account = sub_account [0] ['positions']
        open_orders_from_sub_account = sub_account [0] ['open_orders']
        portfolio = pickling.read_data(path_portfolio)
        #log.error (open_order)
        none_data = [None, [], 0]
        
        # at start, usually position == None
        if positions in none_data:
            positions = positions_from_sub_account#await self.get_positions ()
            pickling.replace_data (path_positions, positions)  
            
        #log.debug (my_trades_open)
        if portfolio in none_data:
            portfolio = await self.get_account_summary()
            pickling.replace_data (path_portfolio, portfolio) 
            portfolio = pickling.read_data(path_portfolio)       
        
        return {'my_trades_open': [] if my_trades_open in none_data else my_trades_open,
                'open_orders_open_byAPI': pickling.read_data(path_orders_open),
                'open_orders_filled_byAPI': pickling.read_data(path_orders_filled),
                'positions': positions,
                'positions_from_sub_account': positions_from_sub_account,
                'open_orders_from_sub_account': open_orders_from_sub_account,
                'portfolio': portfolio,
                'ticker_perpetual': ticker_perpetual[0],
                'index_price': index_price [0]['price'],
                'price_index': ticker_perpetual[0]}
    
    async def position_per_instrument (self, 
                                       positions, 
                                       instrument: str
                                       ) -> list:
        """
        """
        try:
            position  = [o for o in positions if o['instrument_name'] == instrument] 
            if position:
                position  = position  [0]
            #log.warning (position)
        except:
            path_positions: str = system_tools.provide_path_for_file ('positions', self.currency) 
            log.debug (path_positions)
            positions = await self.get_positions ()
            pickling.replace_data (path_positions, positions)   
            position = await self.reading_from_database ()   
            position = position ['positions']  
            log.warning (position)
            position  = [o for o in positions if o['instrument_name'] == instrument]  [0]
        return position
                
    async def current_server_time (self) -> float:
        """
        """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time   ['result']
    
    async def cancel_redundant_orders_in_same_labels (self,  
                                                      label_for_filter
                                                      ) -> None:
        """
        """
        open_order_mgt = await self.open_orders_from_exchange ()
        
        len_current_open_orders = open_order_mgt.open_orders_api_basedOn_label_items_qty(label_for_filter)
        
        if len_current_open_orders != [] :
            if len_current_open_orders > 1 :
                #log.critical(f'{len_current_open_orders > 1=}')
                
                open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_max_id (label_for_filter) 
                
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
        
    async def cancel_orders_hedging_spot_based_on_time_threshold (self, 
                                                                  server_time, label
                                                                  ) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3
        
        open_orders_from_exch = await self.get_open_orders_from_exchange ()
        open_order_mgt = open_orders_management.MyOrders (open_orders_from_exch)
        open_order_label = open_order_mgt.open_orders_api_basedOn_label(label)
        open_order_mgt = open_orders_management.MyOrders (open_order_label)

        try:
            open_orders_lastUpdateTStamps: list = open_order_mgt.open_orders_api_last_update_timestamps()
        except:
            open_orders_lastUpdateTStamps: list = []    
            
        if open_orders_lastUpdateTStamps !=[]:
            open_orders_lastUpdateTStamps: list = open_order_mgt.open_orders_api_last_update_timestamps()
            #log.critical (open_orders_lastUpdateTStamps)
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = server_time - open_orders_lastUpdateTStamp_min                       

            open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_min_id (label)    
                                
            if open_orders_deltaTime > three_minute:
                await self.cancel_by_order_id (open_order_id)    
    
    async def cancel_by_order_id (self, open_order_id) -> None:
        
        await deribit_get.get_cancel_order_byOrderId (
                                                        self.connection_url, 
                                                        self.client_id, 
                                                        self.client_secret, 
                                                        open_order_id
                                                      )  
            
    async def check_open_orders_integrity (
                                            self, 
                                            open_orders_from_sub_account_get,
                                            open_orders_open_byAPI
                                           ) -> None:

        #log.warning (open_orders_open_byAPI)
        #log.critical (open_orders_from_sub_account_get)
        open_order_mgt_sub_account = open_orders_management.MyOrders (open_orders_from_sub_account_get)
        orders_per_db_equivalent_orders_fr_sub_account =  open_order_mgt_sub_account.compare_open_order_per_db_vs_get(open_orders_open_byAPI)
        
        log.info (f"{orders_per_db_equivalent_orders_fr_sub_account=}")

        if orders_per_db_equivalent_orders_fr_sub_account == False:
            # update open order at db with open orders at sub account
            my_path_orders_open = system_tools.provide_path_for_file ('orders', 
                                                                  self.currency, 
                                                                  'open'
                                                                  )
            
            pickling.replace_data (my_path_orders_open, 
                                   open_orders_from_sub_account_get,
                                   True
                                   )
                                      
            catch_error ('update open order at db with open orders at sub account', 
                         idle = .1
                         ) 
       
    async def check_myTrade_integrity (
                                        self, 
                                        positions_from_get: float, 
                                        my_trades_open_from_db: list, 
                                        server_time: int
                                        ) -> None:
        
        '''
        Ensure record in db summary from get = db from transactions 
        
        Args:
            positions_from_get (float): Total outstanding position
            my_trades_open_from_db (list): List of active trading positions
            server_time (int): Server time from exchange in UNIX format
            
        Returns:
            None:
        '''
                    
        #! yes, it seems circular. But its okay for now. FIxed it later
        myTrades_from_db = await check_data_integrity.myTrades_originally_from_db (self.currency)
        
        # get the earliest transaction time stamp
        start_timestamp = myTrades_from_db ['time_stamp_to_recover']
        
        my_selected_trades_open_from_system =[]
        if start_timestamp:
            
            # use the earliest time stamp to fetch data from exchange
            my_selected_trades_open_from_system = await self.my_trades_time_constrained (
                                                                                        start_timestamp, 
                                                                                         server_time
                                                                                         )
        
        await check_data_integrity.main_enforce_my_trade_db_integrity (
                                                                        self.currency,
                                                                        positions_from_get,
                                                                        my_trades_open_from_db,
                                                                        my_selected_trades_open_from_system
                                                                        )
                    
    async def running_strategy (self, 
                                server_time
                                ) -> float:
        """
        """

        try:
            
            # gathering basic data
            #!############################# gathering basic data ######################################

            reading_from_database: dict = await self.reading_from_database ()
            
            # portfolio data
            portfolio: list = reading_from_database ['portfolio']
            #log.warning (portfolio)
            
            # obtain spot equity
            equity: float = portfolio [0]['equity']
            
            # index price
            index_price: float= reading_from_database ['index_price']
            #log.critical (index_price)

            # compute notional value
            notional: float =  await self.compute_notional_value (index_price, 
                                                                  equity
                                                                  )
                               
            # to avoid error if index price/portfolio = []/None
            if  index_price and portfolio :                
                
                one_minute: int = 60000 # one minute in millisecond
                none_data: None = [0, None, []] # to capture none 
                
                # fetch positions for all instruments
                positions: list = reading_from_database ['positions_from_sub_account']
                #log.error (positions)
            
                # my trades data
                my_trades_open: list = reading_from_database ['my_trades_open']
                
                #my_trades_open_mgt: list = myTrades_management.MyTrades (my_trades_open)
                #log.info (my_trades_open)
                
                #instruments_kind: list =  [o  for o in instruments if o['kind'] == 'future']
                
                # fetch instruments data                
                instruments = await self.reading_from_db ('instruments', 
                                                            self.currency
                                                            )
                #futs_analysis = await self.reading_from_db ('futures_analysis',  self.currency )

                # instruments future
                instruments_future = [o for o in instruments if o['kind'] == 'future']

                # obtain instruments future relevant to strategies
                #instrument_transactions = [o['instrument_name'] for o in instruments_future \
                #    if o['instrument_name']   in [f'{self.currency.upper()}-PERPETUAL' , rebates['instrument_name']] ]
                instrument_transactions = [f'{self.currency.upper()}-PERPETUAL']

                # open orders data
                open_orders_open_byAPI: list = reading_from_database ['open_orders_open_byAPI']
                open_orders_from_sub_account_get = reading_from_database ['open_orders_from_sub_account']
                open_orders_filled_byAPI: list = reading_from_database ['open_orders_filled_byAPI']

                #!################################## end of gathering basic data #####################################
                
                #! CHECK BALANCE AND TRANSACTIONS INTEGRITY. IF NOT PASSED, RESTART PROGRAM TO FIX IT
                
                # open order integrity
                await self.check_open_orders_integrity (open_orders_from_sub_account_get,
                                                        open_orders_open_byAPI                                                        
                                                        )

                # open trade integrity
                await self.check_myTrade_integrity (positions,
                                                    my_trades_open, 
                                                    server_time
                                                    )
                
                # prepare open order class object
                open_order_mgt = open_orders_management.MyOrders (open_orders_open_byAPI)

                open_order_mgt_filed = open_orders_management.MyOrders (open_orders_filled_byAPI)
                
                open_order_mgt_filed_status_filed = open_order_mgt_filed.open_orders_status ('filled')
                
                my_trades_open: list = reading_from_database ['my_trades_open']
                
                for instrument in instrument_transactions:

                    log.critical (f'{instrument}') 
                    
                    ticker = await self.reading_from_db ('ticker', 
                                                         instrument
                                                         )
                    # get bid and ask price
                    best_bid_prc= ticker [0]['best_bid_price']
                    best_ask_prc= ticker [0] ['best_ask_price']
    
                    #! get instrument attributes detail
                    instrument_data:dict = [o for o in instruments if o['instrument_name'] == instrument]   [0] 

                    # instrument minimum order
                    min_trade_amount = instrument_data ['min_trade_amount']
                    
                    # instrument contract size
                    contract_size = instrument_data ['contract_size']
                    
                    open_order_mgt_from_exchange = await self.open_orders_from_exchange()
                    #log.warning (f'open_order_mgt_from_exchange {open_order_mgt_from_exchange}') 
                    
                    # fetch strategies 
                    strategies = entries_exits.strategies
            
                    for strategy in strategies:
                                                                
                        pct_threshold_TP: float = strategy ['take_profit_pct']  
                        pct_threshold_avg: float = strategy ['averaging']  
                        quantity_discrete: float = strategy ['quantity_discrete']  
                        time_threshold: float = strategy ['halt_minute_before_reorder']  * one_minute 
                        time_threshold_avg_up: float = strategy ['halt_minute_before_reorder']  * one_minute * 12 * 4
                        #log.error (f'time_threshold {time_threshold}') 
                                              
                        label:str = strategy ['strategy']
                        label_numbered: str = label_numbering.labelling ('open', label)
                        label_closed:str = f'{label}-closed'

                        net_open_orders_open_byAPI_system: int = open_order_mgt_from_exchange.open_orders_api_basedOn_label_items_net (label_numbered)
                        log.warning (f'net_open_orders_open_byAPI_system {net_open_orders_open_byAPI_system}') 
                        
                        # check for any order outstanding as per label filter
                        net_open_orders_open_byAPI_db: int = open_order_mgt.open_orders_api_basedOn_label_items_net (label_numbered)
                        #log.debug (f'open_order_mgt  {open_order_mgt}') 
                        log.error (f'net_open_orders_open_byAPI_db {net_open_orders_open_byAPI_db}') 
                    
                        # create my order mgt template based on strategies
                        my_orders_api_basedOn_label_strategy: list = open_order_mgt.open_orders_api_basedOn_label (label)
                        #log.warning (my_orders_api_basedOn_label_strategy)
                        
                        #! hedging spot: part of risk management, not strategies
                        if 'hedgingSpot' not in strategy['strategy']:
                            #log.debug(f'{label=} {my_orders_api_basedOn_label_strategy=}')
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
                            
                            if open_str_sell!= None and open_str_sell ['send_order'] :
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

                            if closed_str!= None and closed_str ['send_order'] :
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
                                                        
                        if 'hedgingSpot' in strategy['strategy']:
                            
                            if open_order_mgt_filed_status_filed != []: 
                                open_order_filled_latest_timeStamp = max([o['last_update_timestamp'] for o in open_order_mgt_filed_status_filed] )
                                filled_order_deltaTime: int = server_time - open_order_filled_latest_timeStamp  
                                                                   
                            last_time_order_filled_exceed_threshold = True if open_order_mgt_filed_status_filed == [] \
                                else filled_order_deltaTime > time_threshold   
                            
                            if 'PERPETUAL' in instrument :
                                if last_time_order_filled_exceed_threshold:
                                    #log.error (label)

                                    #check under hedging
                                    spot_hedged = spot_hedging.SpotHedging (label,
                                                                            my_trades_open
                                                                            )
                                    
                                    check_spot_hedging = spot_hedged.is_spot_hedged_properly (notional, 
                                                                                              min_trade_amount,
                                                                                              contract_size,
                                                                                              quantity_discrete
                                                                                              ) 
                                    
                                    remain_unhedged = check_spot_hedging ['remain_unhedged_size']
                                    
                                    min_hedging_size = check_spot_hedging ['all_hedging_size']

                                    spot_was_unhedged = check_spot_hedging ['spot_was_unhedged']

                                    actual_hedging_size = spot_hedged.compute_actual_hedging_size()
                                    
                                    label_open_for_filter = f'{label}-open'

                                    log.debug(f'{label=} {label_open_for_filter=}')
                                    
                                    # check for any order outstanding as per label filter
                                    net_open_orders_open_byAPI_db: int = open_order_mgt.open_orders_api_basedOn_label_items_net (label)
                                    log.warning(f'{spot_was_unhedged=} \
                                        {actual_hedging_size=}  \
                                            {net_open_orders_open_byAPI_db=} \
                                                {last_time_order_filled_exceed_threshold=}')
                                    
                                    await self.will_new_open_order_create_over_hedge (label,
                                                                                      actual_hedging_size,
                                                                                      min_hedging_size
                                                                                      )
                                    
                                    # send sell order if spot still unhedged and no current open orders 
                                    if spot_was_unhedged \
                                        and net_open_orders_open_byAPI_db == 0 \
                                            and  last_time_order_filled_exceed_threshold:
                                    
                                        order_result = await self.send_orders ('sell', 
                                                                instrument, 
                                                                abs(check_spot_hedging ['hedging_size']), 
                                                                label_numbered,
                                                                best_ask_prc
                                                                )
                                        log.warning (order_result)
                                        
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
                                        last_time_order_filled_exceed_threshold_avg_up = True if open_order_mgt_filed_status_filed == [] \
                                            else filled_order_deltaTime > time_threshold_avg_up
                                            
                                        log.info(f' {label_numbered=} {bid_prc_is_lower_than_buy_price=} \
                                            {best_bid_prc=} {ask_prc_is_higher_than_sell_price=} \
                                                {best_ask_prc=}')
                                            
                                        log.warning(f' {last_time_order_filled_exceed_threshold_avg_up=}')
                                                
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
                                            and ask_prc_is_higher_than_sell_price\
                                                and last_time_order_filled_exceed_threshold_avg_up:
                                            
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
            current_open_orders_size = open_order_mgt.open_orders_api_basedOn_label_items_size(label_open)
            current_open_orders_size = 0 if current_open_orders_size ==[] else current_open_orders_size

            is_over_hedged = actual_hedging_size + current_open_orders_size < min_hedging_size
            log.info(f'{is_over_hedged=} {actual_hedging_size=} {current_open_orders_size=} {min_hedging_size=}')
            
            if  is_over_hedged:
                open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_max_id (label_open)
                log.critical(f'{open_order_id=}')
                
                sleep (2)
                
                await self.cancel_by_order_id (open_order_id)
            
        except Exception as error:
            catch_error (error)
                
    async def read_data_from_db (self, path) -> list:
        """
        """    
        read = pickling.read_data (self, path)
        return read
    

async def main ():

    connection_url: str = 'https://test.deribit.com/api/v2/'
    
    currency: str = 'ETH'
    sub_account = 'deribit-147691'
    
    client_id: str = parse_dotenv(sub_account) ['client_id']
    client_secret: str = parse_dotenv(sub_account) ['client_secret']
    
    connection_url: str = 'https://www.deribit.com/api/v2/'
    #
    try:

        syn = ApplyHedgingSpot (
                                connection_url=connection_url,
                                client_id=client_id,
                                client_secret= client_secret,
                                currency = currency
        )
        
        # get deribit server timr
        server_time = await syn.current_server_time ()
        
        # resupply sub account db
        sub_accounts = await syn.get_sub_accounts()
    
        my_path_sub_account = system_tools.provide_path_for_file ('sub_accounts', 
                                                                    currency
                                                                    )
        pickling.replace_data(my_path_sub_account, 
                                sub_accounts
                                )
        
        # execute strategy
        await syn.running_strategy (server_time)
        
        # hedging: check for over hedged and over-bought        
        label_hedging = 'hedgingSpot'
        
        await syn.cancel_orders_hedging_spot_based_on_time_threshold (server_time, 
                                                                      label_hedging
                                                                      )
        await syn.cancel_redundant_orders_in_same_labels_closed_hedge ()  
              
        #open_orders_from_exchange = await syn.open_orders_from_exchange ()        
         
    except Exception as error:
        catch_error (error, 30)
    
if __name__ == "__main__":

    try:
        
        asyncio.get_event_loop().run_until_complete(main())
        
        # only one file is allowed to running
        is_running = system_tools.is_current_file_running ('apply_strategies.py')
        
        if is_running:
            catch_error (is_running)
        
        system_tools.sleep_and_restart_program (30)

    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 30)
