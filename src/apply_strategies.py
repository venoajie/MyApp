#!/usr/bin/python3

# built ins
import asyncio

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
from transaction_management.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools, string_modification as str_mod
import deribit_get
from risk_management import spot_hedging, check_data_integrity, position_sizing
from configuration import label_numbering, config
from strategies import entries_exits
# from market_understanding import futures_analysis

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)


def catch_error(error, idle: int = None) -> list:
    """
    """
    system_tools.catch_error_message(error, idle)


def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


@dataclass(unsafe_hash=True, slots=True)
class ApplyHedgingSpot:

    """
    """

    connection_url: str
    client_id: str
    client_secret: str
    currency: str

    async def get_private_data(self) -> list:
        """
        Provide class object to access private get API
        """

        try:

            return deribit_get.GetPrivateData(
                self.connection_url, self.client_id, self.client_secret, self.currency
            )
        except Exception as error:
            catch_error(error)

    async def get_sub_accounts(self) -> list:
        """
        """

        try:
            private_data = await self.get_private_data()
            result: dict = await private_data.get_subaccounts()
            return result["result"]

        except Exception as error:
            catch_error(error)

    async def get_open_orders_from_exchange(self) -> list:
        """
        """

        private_data = await self.get_private_data()
        open_ordersREST: dict = await private_data.get_open_orders_byCurrency()
        return open_ordersREST["result"]

    async def open_orders_from_exchange(self) -> object:
        """
        """
        open_ordersREST: list = await self.get_open_orders_from_exchange()

        return open_orders_management.MyOrders(open_ordersREST)

    async def my_trades_time_constrained(
        self, start_timestamp: int, end_timestamp: int
    ) -> list:
        """
        basis to recover data
        """

        private_data = await self.get_private_data()
        trades: dict = await private_data.get_user_trades_by_currency_and_time(
            start_timestamp, end_timestamp
        )

        try:
            result = [] if trades == [] else trades["result"]["trades"]

            path_trades_open_recovery = system_tools.provide_path_for_file(
                "myTrades", self.currency, "all-recovery-point"
            )
            pickling.replace_data(path_trades_open_recovery, result, True)
        except:
            result = trades["error"]["data"]["reason"]
            if result == "timestamp_of_archived_trade":
                log.critical(result)

        return result

    async def get_my_trades_from_exchange(self, count: int = 1000) -> list:
        """
        """
        private_data = await self.get_private_data()
        trades: list = await private_data.get_user_trades_by_currency(count)

        return [] if trades == [] else trades["result"]["trades"]

    async def get_account_summary(self) -> list:
        """
        """

        private_data = await self.get_private_data()

        account_summary: dict = await private_data.get_account_summary()

        return account_summary["result"]

    async def get_positions(self) -> list:
        """
        """

        private_data = await self.get_private_data()

        result: dict = await private_data.get_positions()

        return result["result"]

    async def send_orders(
        self,
        side: str,
        instrument: str,
        size: float = None,
        label: str = None,
        prc: float = None,
        type: str = "limit",
        trigger_price: float = None,
    ) -> None:
        """
        """

        try:
            private_data = await self.get_private_data()

            if "market" in type:
                result = await private_data.send_order(
                    side, instrument, size, label, None, type, trigger_price
                )
            else:
                if type == "limit":
                    result = await private_data.send_order(
                        side, instrument, size, label, prc
                    )
                else:
                    result = await private_data.send_order(
                        side, instrument, size, label, prc, type, trigger_price
                    )

            await self.cancel_redundant_orders_in_same_labels_closed_hedge()
            return result

        except Exception as error:
            log.error(error)

    async def send_combo_orders(self, params) -> None:
        """
        """

        private_data = await self.get_private_data()
        await private_data.send_triple_orders(params)

    async def compute_notional_value(self, index_price: float, equity: float) -> float:
        """
        """
        return index_price * equity
    
    async def reading_from_db(
        self, end_point, instrument: str = None, status: str = None
    ) -> float:
        """
        """
        return pickling.read_data(
            system_tools.provide_path_for_file(end_point, instrument, status)
        )

    #! ########### will be deleted ##############################################################################
    async def reading_from_database(self, instrument: str = None) -> float:
        """
        """

        path_sub_accounts: str = system_tools.provide_path_for_file(
            "sub_accounts", self.currency
        )

        path_trades_open: str = system_tools.provide_path_for_file(
            "myTrades", self.currency, "open"
        )

        my_trades_open: str = pickling.read_data(path_trades_open)

        path_orders_open: str = system_tools.provide_path_for_file(
            "orders", self.currency, "open"
        )

        path_orders_filled: str = system_tools.provide_path_for_file(
            "orders", self.currency, "filled"
        )

        path_portfolio: str = system_tools.provide_path_for_file(
            "portfolio", self.currency
        )

        symbol_index: str = f"{self.currency}_usd"
        path_index: str = system_tools.provide_path_for_file("index", symbol_index)
        ticker_perpetual: list = await self.reading_from_db(
            "ticker", f"{(self.currency).upper()}-PERPETUAL"
        )
        symbol_index: str = f"{self.currency}_usd"
        path_index: str = system_tools.provide_path_for_file("index", symbol_index)
        index_price: list = pickling.read_data(path_index)
        path_positions: str = system_tools.provide_path_for_file(
            "positions", self.currency
        )
        positions = pickling.read_data(path_positions)
        sub_account = pickling.read_data(path_sub_accounts)
        positions_from_sub_account = sub_account[0]["positions"]
        open_orders_from_sub_account = sub_account[0]["open_orders"]
        portfolio = pickling.read_data(path_portfolio)
        # log.error (open_order)
        none_data = [None, [], 0]

        # at start, usually position == None
        if positions in none_data:
            positions = positions_from_sub_account  # await self.get_positions ()
            pickling.replace_data(path_positions, positions)

        # log.debug (my_trades_open)
        if portfolio in none_data:
            portfolio = await self.get_account_summary()
            pickling.replace_data(path_portfolio, portfolio)
            portfolio = pickling.read_data(path_portfolio)

        return {
            "my_trades_open": [] if my_trades_open in none_data else my_trades_open,
            "open_orders_open_byAPI": pickling.read_data(path_orders_open),
            "open_orders_filled_byAPI": pickling.read_data(path_orders_filled),
            "positions": positions,
            "positions_from_sub_account": positions_from_sub_account,
            "open_orders_from_sub_account": open_orders_from_sub_account,
            "portfolio": portfolio,
            "ticker_perpetual": ticker_perpetual[0],
            "index_price": index_price[0]["price"],
            "price_index": ticker_perpetual[0],
        }

    #! ########### end of will be deleted ##############################################################################

    async def position_per_instrument(self, positions, instrument: str) -> list:
        """
        """
        try:
            position = [o for o in positions if o["instrument_name"] == instrument]
            if position:
                position = position[0]
            # log.warning (position)
        except:
            path_positions: str = system_tools.provide_path_for_file(
                "positions", self.currency
            )
            log.debug(path_positions)
            positions = await self.get_positions()
            pickling.replace_data(path_positions, positions)
            position = await self.reading_from_database()
            position = position["positions"]
            log.warning(position)
            position = [o for o in positions if o["instrument_name"] == instrument][0]
        return position

    async def current_server_time(self) -> float:
        """
        """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time["result"]

    async def cancel_redundant_orders_in_same_labels(self, label_for_filter) -> None:
        """
        """
        open_order_mgt = await self.open_orders_from_exchange()

        len_current_open_orders = open_order_mgt.open_orders_api_basedOn_label_items_qty(
            label_for_filter
        )

        if len_current_open_orders != []:
            if len_current_open_orders > 1:

                open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_max_id(
                    label_for_filter
                )

                cancel = await self.cancel_by_order_id(open_order_id)

                return cancel

    async def cancel_redundant_orders_in_same_labels_closed_hedge(self) -> None:
        """
        """
        label_for_filter = "hedgingSpot-closed"

        cancel = await self.cancel_redundant_orders_in_same_labels(label_for_filter)
        # log.critical(f'{cancel=}')
        return cancel

    async def cancel_orders_hedging_spot_based_on_time_threshold(
        self, server_time, label
    ) -> float:
        """
        """
        one_minute = 60000

        three_minute = one_minute * 3

        open_orders_from_exch = await self.get_open_orders_from_exchange()
        open_order_mgt = open_orders_management.MyOrders(open_orders_from_exch)
        open_order_label = open_order_mgt.open_orders_api_basedOn_label(label)
        open_order_mgt = open_orders_management.MyOrders(open_order_label)

        try:
            open_orders_lastUpdateTStamps: list = open_order_mgt.open_orders_api_last_update_timestamps()
        except:
            open_orders_lastUpdateTStamps: list = []

        if open_orders_lastUpdateTStamps != []:
            open_orders_lastUpdateTStamps: list = open_order_mgt.open_orders_api_last_update_timestamps()
            # log.critical (open_orders_lastUpdateTStamps)
            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = server_time - open_orders_lastUpdateTStamp_min

            open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_min_id(
                label
            )

            if open_orders_deltaTime > three_minute:
                await self.cancel_by_order_id(open_order_id)

    async def search_and_drop_orphan_closed_orders(
        self, open_order_mgt: object, my_trades_open_mgt: object
    ) -> None:

        """
        For every strategy, there are 1 SL and 1 TP. 
        When  1 of them was executed, the other should be cancelled
        
        closed-labelled open order, has:
        - open order that have not executed yet. This is ok
        - open trade waiting to close. This is ok
        - no open order nor open trade. . This is NOT ok. If it found, cancel it
        
        
        """
        open_orderLabelCLosed = open_order_mgt.open_orderLabelCLosed()

        if open_orderLabelCLosed != None:

            for label_closed in open_orderLabelCLosed:
                is_closed_label_exist = my_trades_open_mgt.closed_open_order_label_in_my_trades_open(
                    label_closed
                )

                if is_closed_label_exist == False:
                    open_orders = open_order_mgt.open_orders_api()
                    open_order_id = [
                        o["order_id"]
                        for o in open_orders
                        if str(label_closed)[-10:] in o["label"]
                    ][0]
                    await self.cancel_by_order_id(open_order_id)

    async def cancel_by_order_id(self, open_order_id) -> None:

        private_data = await self.get_private_data()

        result = await private_data.get_cancel_order_byOrderId(open_order_id)
        return result

    async def check_open_orders_integrity(
        self, open_orders_from_sub_account_get, open_orders_open_byAPI
    ) -> None:

        # log.warning (open_orders_open_byAPI)
        # log.critical (open_orders_from_sub_account_get)
        open_order_mgt_sub_account = open_orders_management.MyOrders(
            open_orders_from_sub_account_get
        )
        orders_per_db_equivalent_orders_fr_sub_account = open_order_mgt_sub_account.compare_open_order_per_db_vs_get(
            open_orders_open_byAPI
        )

        log.info(f"{orders_per_db_equivalent_orders_fr_sub_account=}")

        if orders_per_db_equivalent_orders_fr_sub_account == False:
            # update open order at db with open orders at sub account
            my_path_orders_open = system_tools.provide_path_for_file(
                "orders", self.currency, "open"
            )

            pickling.replace_data(
                my_path_orders_open, open_orders_from_sub_account_get, True
            )

            catch_error(
                "update open order at db with open orders at sub account", idle=0.1
            )

    async def check_myTrade_integrity(
        self, positions_from_get: float, my_trades_open_from_db: list, server_time: int
    ) -> None:

        """
        Ensure record in db summary from get = db from transactions 
        
        Args:
            positions_from_get (float): Total outstanding position
            my_trades_open_from_db (list): List of active trading positions
            server_time (int): Server time from exchange in UNIX format
            
        Returns:
            None:
        """

        #! yes, it seems circular. But its okay for now. FIxed it later
        myTrades_from_db = await check_data_integrity.myTrades_originally_from_db(
            self.currency
        )

        # get the earliest transaction time stamp
        start_timestamp = myTrades_from_db["time_stamp_to_recover"]
        log.critical (start_timestamp)

        my_selected_trades_open_from_system = []
        if start_timestamp:

            # use the earliest time stamp to fetch data from exchange
            my_selected_trades_open_from_system = await self.my_trades_time_constrained(
                start_timestamp, server_time
            )

        await check_data_integrity.main_enforce_my_trade_db_integrity(
            self.currency,
            positions_from_get,
            my_trades_open_from_db,
            my_selected_trades_open_from_system,
        )
        
    async def send_market_order(self, params) -> None:
        """
        """

        private_data = await self.get_private_data()
        await private_data.send_market_order(params)
        
    def optimising_exit_price (self, side, best_bid_prc: float, best_ask_prc: float, exit_price: float =None ) -> None:
        """
        """
        
        if exit_price != None:

            if side == 'buy':
                price = min (exit_price, best_bid_prc)
            if side == 'sell':
                price = max (exit_price, best_ask_prc)
        else:

            if side == 'buy':
                price = best_bid_prc
            if side == 'sell':
                price =  best_ask_prc
        return price
        
    async def send_limit_order(self, params) -> None:
        """
        """

        private_data = await self.get_private_data()
        await private_data.send_limit_order(params)
                    
    async def is_send_exit_or_additional_order_allowed (self, 
                                                            label,
                                                            open_trade: list, 
                                                            open_orders: object, 
                                                            strategy_attr, 
                                                            max_size,
                                                            best_bid_prc,
                                                            best_ask_prc
                                                            ) -> None:
        """
        """
        
        # formatting label: strategy & int
        strategy_label = str_mod.get_strings_before_character (label,'-', 0)
        log.error (strategy_attr)
        log.error (f'max_size {max_size}')
        get_strategy_int = str_mod.get_strings_before_character (label,'-', 1)            

        label_closed= f'{label}-closed-{get_strategy_int}'
            
        trade_based_on_label_strategy = open_orders.trade_based_on_label_strategy (open_trade, strategy_label)
        net_sum_current_position = trade_based_on_label_strategy ['net_sum_order_size']
        log.error (f'net_sum_current_position {net_sum_current_position}')

        determine_size_and_side = open_orders.determine_order_size_and_side_for_outstanding_transactions(
                                                                                                    max_size, 
                                                                                                    strategy_label, 
                                                                                                    net_sum_current_position
                                                                                                        )
        side = determine_size_and_side ['side']
        remain_main_orders = abs(determine_size_and_side ['remain_main_orders'])
        remain_exit_orders =  abs(determine_size_and_side ['remain_exit_orders'])
        no_limit_open_order_outstanding =  (determine_size_and_side ['no_limit_open_order_outstanding'])
        
        log.error (f'remain_exit_orders {remain_exit_orders}')
        log.warning (f'remain_main_orders {remain_main_orders}')
        
        if side !=None:
            price = self.optimising_exit_price (side, best_bid_prc, best_ask_prc, None )

        params_limit = {'instrument': trade_based_on_label_strategy['instrument'],
                        'side': side,
                        'type': 'limit'
                        }
    
        params_market = {'instrument': trade_based_on_label_strategy['instrument'],
                    'side': side,
                    'type': 'stop_market'
                    }
            
        if remain_exit_orders != 0:
            label_mod = str_mod.get_strings_before_character(label,'-', 0)
        
            # no order type market for hedging spot
            if "hedgingSpot" not in label_mod \
                and determine_size_and_side['order_type_market']:
                    
                params = {'instrument': trade_based_on_label_strategy['instrument'],
                'size': determine_size_and_side ['remain_exit_orders'],
                'label': label_closed,
                'take_profit_usd': strategy_attr ['take_profit_usd'],
                'type': 'stop_market'
                }
                await self.send_limit_order (params)
            
            if determine_size_and_side['order_type_limit']:
                
                params = {'instrument': trade_based_on_label_strategy['instrument'],
                        'size': determine_size_and_side ['remain_exit_orders'],
                        'take_profit_usd': strategy_attr ['take_profit_usd'],
                        'label': label_closed,
                        'type': 'limit'
                        }
                    
                if False and "hedgingSpot" in label_mod and no_limit_open_order_outstanding:
                    await self.send_limit_order (params_limit)
                    await self.will_new_open_order_create_over_hedge(
                                            strategy_label, net_sum_current_position, max_size
                                        )
            
        if remain_main_orders != 0:
            label_mod = str_mod.get_strings_before_character(label,'-', 0)
            params_limit.update(
                {'size': remain_main_orders,
                 'entry_price': price,
                 'label':label_numbering.labelling("open", strategy_label)
                 }
                )
            log.warning (params_limit)
            if "hedgingSpot" in label_mod and no_limit_open_order_outstanding:
                await self.send_limit_order (params_limit)
                await self.will_new_open_order_create_over_hedge(
                                        strategy_label, net_sum_current_position, max_size
                                    )
            
        return determine_size_and_side#               
                        
    async def is_open_main_order_allowed (self, 
                                     strategy: dict, 
                                     index_price: float, 
                                     my_trades_open: list, 
                                     open_orders: list) -> bool:
        """
        """
        log.error (strategy)
        label_strategy = strategy ['strategy']
        entry_price = strategy['entry_price'] 
        side = strategy['side'] 
        invalidation_price = strategy['invalidation_entry_price'] 
        
        none_data = [None, 0, []]
        
        # prepare default result to avoid unassociated value
        send_sell_order_allowed = False
        send_buy_order_allowed  = False
                
        if side == 'buy' \
            and index_price < entry_price \
                and index_price > invalidation_price:
                
                if open_orders  in none_data:
                    order_buy_open_label_strategy = [] 
                 
                if my_trades_open  in none_data:
                    my_trade_buy_open_label_strategy = [] 
                    
                if my_trades_open not in none_data:
                    my_trade_buy_open = [o  for o in my_trades_open if o['direction'] == 'buy'] 
                    my_trade_buy_open_label_strategy = [o  for o in my_trade_buy_open if label_strategy in o['label']] 
                
                if open_orders not in none_data:
                    order_buy_open = [o  for o in open_orders if o['direction'] == 'buy'] 
                    order_buy_open_label_strategy = [o  for o in order_buy_open if label_strategy in o['label']] 
                    
                send_buy_order_allowed =  my_trade_buy_open_label_strategy in none_data and order_buy_open_label_strategy  in none_data

        if side == 'sell':
            log.error (my_trades_open)
    
            order_sell_open_label_strategy = [] 
            my_trade_sell_open_label_strategy = [] 
            
            log.error (f'label_strategy {label_strategy}')
            log.error ('hedgingSpot' not in label_strategy)

            if 'hedgingSpot' not in label_strategy:
                if index_price > entry_price \
                    and index_price < invalidation_price:
                    
                    if my_trades_open not in none_data:
                        my_trade_sell_open =  [o  for o in my_trades_open if o['direction'] == 'sell'] 
                        my_trade_sell_open_label_strategy = [o  for o in my_trade_sell_open if label_strategy in o['label']] 

                    if open_orders not in none_data:
                        order_sell_open = [o  for o in open_orders if o['direction'] == 'sell'] 
                        order_sell_open_label_strategy = [o  for o in order_sell_open if label_strategy in o['label']] 
                    
            else:
                pass
            
            send_sell_order_allowed =  my_trade_sell_open_label_strategy in none_data and order_sell_open_label_strategy  in none_data

        return {'send_buy_order_allowed': send_buy_order_allowed,
                'send_sell_order_allowed': send_sell_order_allowed}
        
    async def running_strategy(self, server_time) -> float:
        """
        """

        try:

            # gathering basic data
            #!############################# gathering basic data ######################################

            reading_from_database: dict = await self.reading_from_database()

            # get portfolio data
            portfolio: list = reading_from_database["portfolio"]

            # obtain spot equity
            equity: float = portfolio[0]["equity"]

            # index price
            index_price: float = reading_from_database["index_price"]
            
            # compute notional value
            notional: float = await self.compute_notional_value(index_price, equity)

            # to avoid error if index price/portfolio = []/None
            if index_price and portfolio:

                one_minute: int = 60000  # one minute in millisecond
                none_data: None = [0, None, []]  # to capture none

                # fetch positions for all instruments
                positions: list = reading_from_database["positions_from_sub_account"]

                # my trades data
                my_trades_open: list = reading_from_database["my_trades_open"]
                #log.warning (my_trades_open)
                
                # instruments_kind: list =  [o  for o in instruments if o['kind'] == 'future']

                # fetch instruments data
                instruments = await self.reading_from_db("instruments", self.currency)
                # futs_analysis = await self.reading_from_db ('futures_analysis',  self.currency )

                # instruments future
                #instruments_future = [o for o in instruments if o["kind"] == "future"]

                # obtain instruments future relevant to strategies
                # instrument_transactions = [o['instrument_name'] for o in instruments_future \
                #    if o['instrument_name']   in [f'{self.currency.upper()}-PERPETUAL' , rebates['instrument_name']] ]
                instrument_transactions = [f"{self.currency.upper()}-PERPETUAL"]

                # open orders data
                open_orders_open_byAPI: list = reading_from_database[
                    "open_orders_open_byAPI"
                ]
                #log.critical (open_orders_open_byAPI)
                open_orders_from_sub_account_get = reading_from_database[
                    "open_orders_from_sub_account"
                ]
                open_orders_filled_byAPI: list = reading_from_database[
                    "open_orders_filled_byAPI"
                ]

                #log.critical (open_orders_from_sub_account_get)
                #!################################## end of gathering basic data #####################################

                # Creating an instance of the my-Trade class 
                my_trades_open_mgt: object = myTrades_management.MyTrades(
                    my_trades_open
                )

                # Creating an instance of the open order  class 
                open_order_mgt = open_orders_management.MyOrders(open_orders_open_byAPI)

                #! CHECK BALANCE AND TRANSACTIONS INTEGRITY. IF NOT PASSED, RESTART PROGRAM TO FIX IT

                # open order integrity
                await self.check_open_orders_integrity(
                    open_orders_from_sub_account_get, open_orders_open_byAPI
                )

                # open trade integrity
                await self.check_myTrade_integrity(
                    positions, my_trades_open, server_time
                )

                await self.search_and_drop_orphan_closed_orders(
                    open_order_mgt, my_trades_open_mgt
                )
                
                #! END OF CHECK BALANCE AND TRANSACTIONS INTEGRITY.

                # obtain all closed labels in open orders
                label_closed = open_order_mgt.open_orderLabelCLosed()

                open_order_mgt_filed = open_orders_management.MyOrders(
                    open_orders_filled_byAPI
                )

                open_order_mgt_filed_status_filed = open_order_mgt_filed.open_orders_status(
                    "filled"
                )
                
                # fetch strategies attributes
                strategies = entries_exits.strategies                
                
            
                # fetch label for outstanding trade position/orders
                strategy_labels =  str_mod.remove_redundant_elements(
                    [ str_mod.get_strings_before_character(o['label'])  for o in my_trades_open ]
                    ) 
                
                # when there are some positions/order, check their appropriateness to the established standard
                if strategy_labels != []:
                            
                    for label in strategy_labels:
                        
                        log.error (label)
                        label_mod = str_mod.get_strings_before_character(label,'-', 0)
                        
                        # get startegy details
                        strategy_attr = [o for o in strategies if o['strategy'] == label_mod][0]
                        
                        instrument = [
                            o["instrument_name"] for o in my_trades_open if str_mod.get_strings_before_character(o["label"],'-', 0)  == label_mod
                        ][0]
                        log.error (f'instrument AA {instrument}')
                            
                        ticker = await self.reading_from_db("ticker", instrument)
                        # get bid and ask price
                        best_bid_prc = ticker[0]["best_bid_price"]
                        best_ask_prc = ticker[0]["best_ask_price"]

                        #! get instrument attributes detail
                        instrument_data: dict = [
                            o for o in instruments if o["instrument_name"] == instrument
                        ][0]

                        # instrument minimum order
                        min_trade_amount = instrument_data["min_trade_amount"]

                        # instrument contract size
                        contract_size = instrument_data["contract_size"]
                        
                        
                        # determine position sizing-general strategy
                        min_position_size: float = position_sizing.pos_sizing (
                                                    strategy_attr ['take_profit_usd'],
                                                    strategy_attr ['entry_price'], 
                                                    notional, 
                                                    strategy_attr ['equity_risked_pct']
                                                    ) 
                
                        # Creating an instance of the spot hedging class 
                        spot_hedged = spot_hedging.SpotHedging(
                                        strategy_attr['strategy'], my_trades_open
                                    )
                        
                        check_spot_hedging = spot_hedged.is_spot_hedged_properly(
                            notional,
                            min_trade_amount,
                            contract_size,
                            strategy_attr['quantity_discrete']
                        )       
                                        
                        # determine position sizing-hedging
                        if "hedgingSpot" in strategy_attr["strategy"]:
                            min_position_size = check_spot_hedging[
                            "all_hedging_size"
                            ]
                        log.error(f'min_position_size {min_position_size}')
                        log.error(strategy_attr["strategy"])
                        
                        exit_order_allowed = await self.is_send_exit_or_additional_order_allowed (label,
                                                                                                my_trades_open, 
                                                                                                open_order_mgt, 
                                                                                                strategy_attr, 
                                                                                                min_position_size,
                                                                                                best_bid_prc,
                                                                                                best_ask_prc
                                                                                                )
                        log.error (f'exit_order_allowed {exit_order_allowed}' )    
                
                
                for instrument in instrument_transactions:

                    log.critical(f"{instrument}")

                    ticker = await self.reading_from_db("ticker", instrument)
                    # get bid and ask price
                    best_bid_prc = ticker[0]["best_bid_price"]
                    best_ask_prc = ticker[0]["best_ask_price"]

                    #! get instrument attributes detail
                    instrument_data: dict = [
                        o for o in instruments if o["instrument_name"] == instrument
                    ][0]

                    # instrument minimum order
                    min_trade_amount = instrument_data["min_trade_amount"]

                    # instrument contract size
                    contract_size = instrument_data["contract_size"]
                    

                    #execute each strategy
                    for strategy in strategies:

                        label_strategy = strategy ['strategy']
                        time_threshold: float = strategy["halt_minute_before_reorder"] * one_minute
                        time_threshold_avg_up: float = time_threshold * 12 * 4

                        remain_unhedged = check_spot_hedging[
                            "remain_unhedged_size"
                        ]         
                        
                        open_order_allowed = await self.is_open_main_order_allowed (strategy, 
                                                                                index_price, 
                                                                                my_trades_open,
                                                                                open_orders_open_byAPI
                                                                                )
                        log.error (f'open_order_allowed {open_order_allowed}' )
                         
                        label_closed: str = f"{label_strategy}-closed"
                        
                        # add some extra params to strategy
                        strategy.update(
                            {'instrument': instrument,
                             'size':min_position_size,
                             'label_numbered':label_numbering.labelling("open", 
                                                                        label_strategy
                                                                        ),
                             'label_closed_numbered': label_numbering.labelling ('closed', 
                                                                                 label_strategy
                                                                                             )
                                         }
                                        )
                                                
                        # check for any order outstanding as per label filter
                        net_open_orders_open_byAPI_db: int = open_order_mgt.open_orders_api_basedOn_label_items_net(
                            strategy['label_numbered']
                        )
                    
                        if "hedgingSpot" in strategy["strategy"]:

                            if open_order_mgt_filed_status_filed != []:
                                open_order_filled_latest_timeStamp = max(
                                    [
                                        o["last_update_timestamp"]
                                        for o in open_order_mgt_filed_status_filed
                                    ]
                                )
                                filled_order_deltaTime: int = server_time - open_order_filled_latest_timeStamp

                            last_time_order_filled_exceed_threshold = (
                                True
                                if open_order_mgt_filed_status_filed == []
                                else filled_order_deltaTime > time_threshold
                            )

                            if "PERPETUAL" in instrument:
                                if last_time_order_filled_exceed_threshold:
                                    # log.error (label)
                                    
                                    # check under hedging
                                    spot_hedged = spot_hedging.SpotHedging(
                                        label_strategy, my_trades_open
                                    )

                                    spot_was_unhedged = check_spot_hedging[
                                        "spot_was_unhedged"
                                    ]

                                    actual_hedging_size = (
                                        spot_hedged.compute_actual_hedging_size()
                                    )

                                    label_open_for_filter = f"{label_strategy}-open"

                                    log.debug(f"{label_strategy=} {label_open_for_filter=}")

                                    # check for any order outstanding as per label filter
                                    net_open_orders_open_byAPI_db: int = open_order_mgt.open_orders_api_basedOn_label_items_net(
                                        label_strategy
                                    )
                                    log.warning(
                                        f"{spot_was_unhedged=} \
                                        {actual_hedging_size=}  \
                                            {net_open_orders_open_byAPI_db=} \
                                                {last_time_order_filled_exceed_threshold=}"
                                    )

                                    new_open_order_create_over_hedge = await self.will_new_open_order_create_over_hedge(
                                        label_strategy, actual_hedging_size, min_position_size
                                    )
                                    
                                    # send sell order if spot still unhedged and no current open orders
                                    if (
                                        spot_was_unhedged
                                        and net_open_orders_open_byAPI_db == 0
                                        and last_time_order_filled_exceed_threshold
                                    ):

                                        order_result = await self.send_orders(
                                            "sell",
                                            instrument,
                                            abs(check_spot_hedging["hedging_size"]),
                                            strategy['label_numbered'],
                                            best_ask_prc,
                                        )
                                        log.warning(order_result)

                                        await self.cancel_redundant_orders_in_same_labels(
                                            label_open_for_filter
                                        )

                                        await self.will_new_open_order_create_over_hedge(
                                            label_strategy, actual_hedging_size, min_position_size
                                        )

                                    # if spot has hedged properly, check also for opportunity to get additional small profit
                                    if (
                                        spot_was_unhedged == False
                                        and remain_unhedged >= 0
                                        and net_open_orders_open_byAPI_db == 0
                                    ):

                                        adjusting_inventories = spot_hedged.adjusting_inventories(
                                            index_price,
                                            self.currency,
                                            strategy["take_profit_pct"],
                                            strategy["averaging"],
                                            label_open_for_filter,
                                        )
                                        bid_prc_is_lower_than_buy_price = (
                                            best_bid_prc
                                            < adjusting_inventories["buy_price"]
                                        )
                                        ask_prc_is_higher_than_sell_price = (
                                            best_ask_prc
                                            > adjusting_inventories["sell_price"]
                                        )
                                        last_time_order_filled_exceed_threshold_avg_up = (
                                            True
                                            if open_order_mgt_filed_status_filed == []
                                            else filled_order_deltaTime
                                            > time_threshold_avg_up
                                        )

                                        log.info(
                                            f" {strategy['label_numbered']=} {bid_prc_is_lower_than_buy_price=} \
                                            {best_bid_prc=} {ask_prc_is_higher_than_sell_price=} \
                                                {best_ask_prc=}"
                                        )

                                        log.warning(
                                            f" {last_time_order_filled_exceed_threshold_avg_up=}"
                                        )

                                        if (
                                            adjusting_inventories["take_profit"]
                                            and bid_prc_is_lower_than_buy_price
                                        ):

                                            order_result = await self.send_orders(
                                                "buy",
                                                instrument,
                                                abs(
                                                    adjusting_inventories[
                                                        "size_take_profit"
                                                    ]
                                                ),
                                                adjusting_inventories[
                                                    "label_take_profit"
                                                ],
                                                best_bid_prc,
                                            )
                                            log.warning(order_result)

                                            await self.cancel_redundant_orders_in_same_labels(
                                                label_closed
                                            )

                                        if (
                                            adjusting_inventories["average_up"]
                                            and ask_prc_is_higher_than_sell_price
                                            and last_time_order_filled_exceed_threshold_avg_up
                                        ):

                                            order_result = await self.send_orders(
                                                "sell",
                                                instrument,
                                                check_spot_hedging["average_up_size"],
                                                strategy['label_numbered'],
                                                best_ask_prc,
                                            )
                                            log.warning(order_result)

                                            await self.cancel_redundant_orders_in_same_labels(
                                                label_open_for_filter
                                            )

        except Exception as error:
            catch_error(error, 30)

    async def will_new_open_order_create_over_hedge(
        self, label, actual_hedging_size: float, min_position_size: float
    ) -> None:

        """
        """

        from time import sleep

        try:

            # refresh open orders
            reading_from_database: dict = await self.reading_from_database()
            open_orders_open_byAPI: list = reading_from_database[
                "open_orders_open_byAPI"
            ]

            # log.info(f'{open_orders_open_byAPI=}')
            open_order_mgt = open_orders_management.MyOrders(open_orders_open_byAPI)
            label_open = f"{label}-open"
            current_open_orders_size = open_order_mgt.open_orders_api_basedOn_label_items_size(
                label_open
            )
            current_open_orders_size = (
                0 if current_open_orders_size == [] else current_open_orders_size
            )

            is_over_hedged = (
                actual_hedging_size + current_open_orders_size < min_position_size
            )
            log.info(
                f"{is_over_hedged=} {actual_hedging_size=} {current_open_orders_size=} {min_position_size=}"
            )

            if is_over_hedged:
                open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_max_id(
                    label_open
                )
                log.critical(f"{open_order_id=}")

                await self.cancel_by_order_id(open_order_id)

        except Exception as error:
            catch_error(error)


async def main():

    connection_url: str = "https://test.deribit.com/api/v2/"

    currency: str = "ETH"
    sub_account = "deribit-147691"

    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]

    connection_url: str = "https://www.deribit.com/api/v2/"
    #
    try:

        syn = ApplyHedgingSpot(
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            currency=currency,
        )

        # get deribit server timr
        server_time = await syn.current_server_time()

        # resupply sub account db
        sub_accounts = await syn.get_sub_accounts()

        my_path_sub_account = system_tools.provide_path_for_file(
            "sub_accounts", currency
        )
        pickling.replace_data(my_path_sub_account, sub_accounts)

        # execute strategy
        await syn.running_strategy(server_time)

        # hedging: check for over hedged and over-bought
        label_hedging = "hedgingSpot"

        await syn.cancel_orders_hedging_spot_based_on_time_threshold(
            server_time, label_hedging
        )
        await syn.cancel_redundant_orders_in_same_labels_closed_hedge()

        # open_orders_from_exchange = await syn.open_orders_from_exchange ()

    except Exception as error:
        catch_error(error, 30)

if __name__ == "__main__":

    try:

        asyncio.get_event_loop().run_until_complete(main())

        # only one file is allowed to running
        is_running = system_tools.is_current_file_running("apply_strategies.py")

        if is_running:
            catch_error(is_running)

    except (KeyboardInterrupt):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 30)
