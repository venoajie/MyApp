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
    """ """
    system_tools.catch_error_message(error, idle)

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)

@dataclass(unsafe_hash=True, slots=True)
class ApplyHedgingSpot:

    """ """

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
        """ """

        try:
            private_data = await self.get_private_data()
            result: dict = await private_data.get_subaccounts()
            return result["result"]

        except Exception as error:
            catch_error(error)

    async def get_open_orders_from_exchange(self) -> list:
        """ """

        private_data = await self.get_private_data()
        open_ordersREST: dict = await private_data.get_open_orders_byCurrency()
        return open_ordersREST["result"]

    async def open_orders_from_exchange(self) -> object:
        """ """
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

    async def get_account_summary(self) -> list:
        """ """

        private_data = await self.get_private_data()

        account_summary: dict = await private_data.get_account_summary()

        return account_summary["result"]

    async def get_positions(self) -> list:
        """ """

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
        """ """

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
        """ """

        private_data = await self.get_private_data()
        await private_data.send_triple_orders(params)

    async def compute_notional_value(self, index_price: float, equity: float) -> float:
        """ """
        return index_price * equity

    def compute_position_leverage_and_delta(
        self, notional: float, my_trades_open: float
    ) -> float:
        total_long = (
            0
            if my_trades_open == []
            else sum([o["amount"] for o in my_trades_open if o["direction"] == "buy"])
        )

        total_short = (
            0
            if my_trades_open == []
            else sum([o["amount"] for o in my_trades_open if o["direction"] == "sell"])
            * -1
        )

        return {
            "delta": position_sizing.compute_delta(notional, total_long, total_short),
            "leverage": position_sizing.compute_leverage(
                notional, total_long, total_short
            ),
        }

    async def reading_from_db(
        self, end_point, instrument: str = None, status: str = None
    ) -> float:
        """ """
        return pickling.read_data(
            system_tools.provide_path_for_file(end_point, instrument, status)
        )

    #! ########### will be deleted ##############################################################################
    async def reading_from_database(self, instrument: str = None) -> float:
        """ """

        path_sub_accounts: str = system_tools.provide_path_for_file(
            "sub_accounts", self.currency
        )

        path_orders_open: str = system_tools.provide_path_for_file(
            "orders", self.currency, "open"
        )

        path_portfolio: str = system_tools.provide_path_for_file(
            "portfolio", self.currency
        )

        ticker_perpetual: list = await self.reading_from_db(
            "ticker", f"{(self.currency).upper()}-PERPETUAL"
        )
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
            "open_orders_open_byAPI": pickling.read_data(path_orders_open),
            "positions": positions,
            "positions_from_sub_account": positions_from_sub_account,
            "open_orders_from_sub_account": open_orders_from_sub_account,
            "portfolio": portfolio,
            "ticker_perpetual": ticker_perpetual[0],
        }

    #! ########### end of will be deleted ##############################################################################

    async def current_server_time(self) -> float:
        """ """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time["result"]

    async def cancel_redundant_orders_in_same_labels(self, label_for_filter) -> None:
        """ """
        open_order_mgt = await self.open_orders_from_exchange()

        len_current_open_orders = (
            open_order_mgt.open_orders_api_basedOn_label_items_qty(label_for_filter)
        )

        if len_current_open_orders != []:
            if len_current_open_orders > 1:
                open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_max_id(
                    label_for_filter
                )

                cancel = await self.cancel_by_order_id(open_order_id)

                return cancel

    async def cancel_redundant_orders_in_same_labels_closed_hedge(self) -> None:
        """ """
        label_for_filter = "hedgingSpot-closed"

        cancel = await self.cancel_redundant_orders_in_same_labels(label_for_filter)
        # log.critical(f'{cancel=}')
        return cancel

    async def cancel_orders_hedging_spot_based_on_time_threshold(
        self, server_time, label
    ) -> float:
        """ """
        one_minute = 60000

        three_minute = one_minute * 3

        open_orders_from_exch = await self.get_open_orders_from_exchange()
        open_order_mgt = open_orders_management.MyOrders(open_orders_from_exch)
        open_order_label = open_order_mgt.open_orders_api_basedOn_label(label)
        open_order_mgt = open_orders_management.MyOrders(open_order_label)

        try:
            open_orders_lastUpdateTStamps: list = (
                open_order_mgt.open_orders_api_last_update_timestamps()
            )
        except:
            open_orders_lastUpdateTStamps: list = []

        if open_orders_lastUpdateTStamps != []:
            open_orders_lastUpdateTStamps: list = (
                open_order_mgt.open_orders_api_last_update_timestamps()
            )
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
                is_closed_label_exist = (
                    my_trades_open_mgt.closed_open_order_label_in_my_trades_open(
                        label_closed
                    )
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
        
        open_order_mgt_sub_account = open_orders_management.MyOrders(
            open_orders_from_sub_account_get
        )
        orders_per_db_equivalent_orders_fr_sub_account = (
            open_order_mgt_sub_account.compare_open_order_per_db_vs_get(
                open_orders_open_byAPI
            )
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
        log.critical(start_timestamp)

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
        """ """

        private_data = await self.get_private_data()
        await private_data.send_market_order(params)

    def optimising_exit_price(
        self, side, best_bid_prc: float, best_ask_prc: float, exit_price: float = None
    ) -> None:
        """ """

        if exit_price != None:
            if side == "buy":
                price = min(exit_price, best_bid_prc)
            if side == "sell":
                price = max(exit_price, best_ask_prc)
        else:
            if side == "buy":
                price = best_bid_prc
            if side == "sell":
                price = best_ask_prc
        return price

    async def send_limit_order(self, params) -> None:
        """ """

        private_data = await self.get_private_data()
        await private_data.send_limit_order(params)

    async def is_send_exit_or_additional_order_allowed(
        self,
        label,
        open_trade_strategy: list,
        open_orders: object,
        strategy_attr: list,
        min_position_size: float,
    ) -> None:
        """ 
        To settled transactions that have taken place
        """

        # formatting label: strategy & int. Result example: 'hedgingSpot'/'supplyDemandShort60'
        #log.warning(f'label {label}')
        #log.warning(f'open_trade_strategy {open_trade_strategy}')
        strategy_label = str_mod.get_strings_before_character(label, "-", 0)
        log.warning(f'strategy_label {strategy_label}')
        
        try:
            strategy_label_int = str_mod.get_strings_before_character(label, "-", 1)
        except:
            strategy_label_int = None
        
       # open_trade_strategy = ([o  for o in open_trade if strategy_label in o['label'] ])
        
        # get net buy-sell position
        net_sum_current_position = 0 if open_trade_strategy == [] else open_orders.net_sum_order_size(open_trade_strategy)
        
        open_orders_strategy= open_orders.open_orders_api_basedOn_label(strategy_label)
            
        # get net buy-sell order limit
        open_orders_strategy_limit =  [o for o in open_orders_strategy if 'limit' in o["order_type"] ]        
        net_sum_open_orders_strategy_limit = 0 if open_orders_strategy_limit == [] else open_orders.net_sum_order_size(open_orders_strategy_limit)        
        len_transactions_open_orders_strategy_limit =  0 if open_orders_strategy_limit == [] else len (open_orders_strategy_limit)
        
        # get net buy-sell order market
        open_orders_strategy_market = [o for o in open_orders_strategy if 'market' in o["order_type"] ]   
        net_sum_open_orders_strategy_market =   0 if open_orders_strategy_market == [] else open_orders.net_sum_order_size(open_orders_strategy_market)      
        len_transactions_open_orders_strategy_market =   0 if open_orders_strategy_market == [] else len (open_orders_strategy_market)
        log.info (open_orders_strategy)
        log.info (open_orders_strategy_limit)
        log.info (open_orders_strategy_market)
        
        # get default side from the strategy configuration
        side_main = strategy_attr["side"]
        
        log.warning(f'side_main {side_main} net_sum_current_position {net_sum_current_position} net_sum_open_orders_strategy_limit {net_sum_open_orders_strategy_limit} net_sum_open_orders_strategy_market {net_sum_open_orders_strategy_market}')
        log.warning(f'min_position_size {min_position_size} len_transactions_open_orders_strategy_market {len_transactions_open_orders_strategy_market} len_transactions_open_orders_strategy_limit {len_transactions_open_orders_strategy_limit}')
        
        determine_size_and_side = (
                open_orders.calculate_order_size_and_side_for_outstanding_transactions(
                    label, 
                    side_main, 
                    net_sum_current_position,
                    net_sum_open_orders_strategy_limit,
                    net_sum_open_orders_strategy_market,
                    min_position_size
                )
            )
        
        log.warning(f'net_sum_current_position {net_sum_current_position}')
        log.warning(f'strategy_label_int {strategy_label_int}')
        log.critical(f'len_transactions_open_orders_strategy_limit {len_transactions_open_orders_strategy_limit}')
        log.critical(f'len_transactions_open_orders_strategy_market {len_transactions_open_orders_strategy_market}')
        determine_size_and_side['len_order_market']= len_transactions_open_orders_strategy_limit
        determine_size_and_side['len_order_limit']= len_transactions_open_orders_strategy_market
        
        if net_sum_current_position== 0:            
            # determine position sizing-hedging
            pass
            
        # the strategy has outstanding position
        if net_sum_current_position !=0 and strategy_label_int != None:
            label_closed = f"{strategy_label}-closed-{strategy_label_int}"     
            
            determine_size_and_side['label_closed'] = label_closed
            
            #the strategy has outstanding position
            if open_trade_strategy !=[]:
                log.warning(f'strategy_label_int {strategy_label_int}')
                #log.warning(f'open_trade_strategy {open_trade_strategy}')
                    
                size_as_per_label = [o['amount'] for o in open_trade_strategy if strategy_label_int in o['label'] ][0]
                log.warning(f'size_as_per_label {size_as_per_label}')
                
                open_trade_hedging_price_max = max([o['price'] for o in open_trade_strategy  ])
                open_trade_hedging_selected = ([o  for o in open_trade_strategy if o['price'] == open_trade_hedging_price_max])
                
                if strategy_label_int in [o['label'] for o in open_trade_hedging_selected ][0]:
                    
                    #log.info (open_trade_hedging_selected)
                    determine_size_and_side['exit_orders_limit_qty'] = size_as_per_label

                else:
                    determine_size_and_side['exit_orders_limit_qty'] = 0
            
            return determine_size_and_side

    async def is_send_main_order_allowed(
        self,
        strategy: dict,
        index_price: float,
        my_trades_open: list,
        open_orders: list,
        notional
    ) -> bool:
        
        """ 
        """
        # log.error (strategy)
        strategy_label = strategy["strategy"]
        entry_price = strategy["entry_price"]
        side = strategy["side"]
        invalidation_price = strategy["invalidation_entry_price"]

        none_data = [None, 0, []]

        # prepare default result to avoid unassociated value
        order_and_position_buy_ok = False
        market_buy_ok = False
        order_and_position_sell_ok = False
        market_sell_ok = False
        
        my_trades_open_mgt: object = myTrades_management.MyTrades(
                    my_trades_open
                )

        if side == "buy":
            
            order_buy_open_strategy_label = []
            my_trade_buy_open_strategy_label = []

            if my_trades_open not in none_data:
                my_trade_buy_open_strategy_label = my_trades_open_mgt.transactions_same_side_and_label (side,strategy_label) ['my_trade_side_strategy_label']

            if open_orders not in none_data:
                order_buy_open_strategy_label = my_trades_open_mgt.transactions_same_side_and_label (side,strategy_label,open_orders) ['my_trade_side_strategy_label']

            order_and_position_buy_ok = (
                my_trade_buy_open_strategy_label in none_data
                and order_buy_open_strategy_label in none_data
            )
            market_buy_ok = (
                index_price < entry_price and index_price > invalidation_price
            )

        if side == "sell":
            order_sell_open_strategy_label = []
            my_trade_sell_open_strategy_label = []

            if open_orders not in none_data:
                order_sell_open_strategy_label = my_trades_open_mgt.transactions_same_side_and_label (side,strategy_label,open_orders) ['my_trade_side_strategy_label']
                # log.warning (order_sell_open_strategy_label)
            if my_trades_open not in none_data:
                my_trade_sell_open_strategy_label = my_trades_open_mgt.transactions_same_side_and_label (side,strategy_label) ['my_trade_side_strategy_label']
                net_sum_my_trade_side_strategy_label = my_trades_open_mgt.transactions_same_side_and_label (side,strategy_label) ['net_sum_my_trade_side_strategy_label']

            if "hedgingSpot" in strategy_label:
                actual_hedging_size = net_sum_my_trade_side_strategy_label
                min_hedging_size = - notional
                net_hedge = actual_hedging_size - min_hedging_size
                log.critical("HEDGING SPOT MAIN ORDER")
                log.critical(
                    f"strategy_label {side} {strategy_label} min_hedging_size {min_hedging_size} net_hedge {net_hedge} net_hedge > 0 {net_hedge > 0}"
                )
                log.critical(
                    f"net_sum_my_trade_side_strategy_label {net_sum_my_trade_side_strategy_label}"
                )

            order_and_position_sell_ok = (
                my_trade_sell_open_strategy_label in none_data
                and order_sell_open_strategy_label in none_data
            )
            market_sell_ok = (
                False
                if "hedgingSpot" in strategy_label
                else index_price > entry_price and index_price < invalidation_price
            )

        return {
            "send_buy_order_allowed": net_hedge > 0 if strategy_label =='hedgingSpot' and order_sell_open_strategy_label in none_data \
                else order_and_position_buy_ok and market_buy_ok,
            "send_sell_order_allowed": order_and_position_sell_ok and market_sell_ok,
        }

    async def running_strategy(self, server_time) -> float:
        """ """

        try:
            # gathering basic data
            # ?############################# gathering basic data ######################################

            reading_from_database: dict = await self.reading_from_database()

            # get portfolio data
            portfolio: list = reading_from_database["portfolio"]

            # to avoid error if index price/portfolio = []/None
            if portfolio:
                one_minute: int = 60000  # one minute in millisecond
                none_data: None = [0, None, []]  # to capture none

                # fetch positions for all instruments
                positions: list = reading_from_database["positions_from_sub_account"]

                # my trades data
                my_trades_open: list = await self.reading_from_db(
                    "myTrades", self.currency, "open"
                )
                #og.debug (my_trades_open)

                # instruments_kind: list =  [o  for o in instruments if o['kind'] == 'future']

                # fetch instruments data
                instruments = await self.reading_from_db("instruments", self.currency)
                # futs_analysis = await self.reading_from_db ('futures_analysis',  self.currency )

                # instruments future
                # instruments_future = [o for o in instruments if o["kind"] == "future"]

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

                # log.critical (open_orders_from_sub_account_get)
                # ?################################## end of gathering basic data #####################################

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

                # fetch strategies attributes
                strategies = entries_exits.strategies

                # fetch label for outstanding trade position/orders
                strategy_labels = str_mod.remove_redundant_elements(
                    [
                        str_mod.get_strings_before_character(o["label"])
                        for o in my_trades_open
                    ]
                )

                # when there are some positions/order, check their appropriateness to the established standard
                if strategy_labels != []:
                    
                    # result example: 'hedgingSpot-1678610144572'/'supplyDemandShort60-1678753445244'
                    for label in strategy_labels:
                        #log.critical (f'label {label}')
                        
                        # result example: 'hedgingSpot'/'supplyDemandShort60'
                        strategy_label = str_mod.get_strings_before_character(label, "-", 0)
                        
                        open_order_label = open_order_mgt.open_orders_api_basedOn_label(strategy_label)
                        
                        open_order_label_short = [
                            o for o in open_order_label if o["direction"] == 'sell'
                        ]
                        open_order_label_long = [
                            o for o in open_order_label if o["direction"] == 'buy'
                        ]
                        log.warning(f' open_order_label {open_order_label}')
                        log.error(f' open_order_label_short {open_order_label_short}')

                        # result example: 'hedgingSpot'/'supplyDemandShort60'
                        strategy_label = str_mod.get_strings_before_character(label, "-", 0)
                        strategy_label_int = str_mod.get_strings_before_character(label, "-", 1)

                        # get startegy details
                        strategy_attr = [
                            o for o in strategies if o["strategy"] == strategy_label
                        ][0]
                        
                        log.critical (f' {label}')
                        #log.critical (f'strategy_label {strategy_label}')
                        
                        open_trade_strategy = ([o  for o in my_trades_open if strategy_label in o['label'] ])
                        open_trade_strategy_label = ([o  for o in open_trade_strategy if strategy_label_int in o['label'] ])
                        #log.critical (f'open_trade_strategy {open_trade_strategy}')

                        instrument = [
                            o["instrument_name"]
                            for o in open_trade_strategy_label
                        ][0]
                        log.critical (f'instrument {instrument}')

                        ticker = await self.reading_from_db("ticker", instrument)

                        # index price
                        index_price: float = ticker[0]["index_price"]

                        # get bid and ask price
                        best_bid_prc = ticker[0]["best_bid_price"]
                        best_ask_prc = ticker[0]["best_ask_price"]

                        # obtain spot equity
                        equity: float = portfolio[0]["equity"]

                        # compute notional value
                        notional: float = await self.compute_notional_value(
                            index_price, equity
                        )

                        # leverage_and_delta = self.compute_position_leverage_and_delta (notional, my_trades_open)
                        # log.warning (leverage_and_delta)

                        #! get instrument attributes detail
                        instrument_data: dict = [
                            o for o in instruments if o["instrument_name"] == instrument
                        ][0]

                        # instrument minimum order
                        min_trade_amount = instrument_data["min_trade_amount"]

                        # instrument contract size
                        contract_size = instrument_data["contract_size"]

                        # determine position sizing-general strategy
                        min_position_size: float = position_sizing.pos_sizing(
                            strategy_attr["take_profit_usd"],
                            strategy_attr["entry_price"],
                            notional,
                            strategy_attr["equity_risked_pct"],
                        )

                        # Creating an instance of the spot hedging class
                        spot_hedged = spot_hedging.SpotHedging(
                            strategy_attr["strategy"], my_trades_open
                        )

                        check_spot_hedging = spot_hedged.is_spot_hedged_properly(
                            notional,
                            min_trade_amount,
                            contract_size,
                            strategy_attr["quantity_discrete"],
                        )

                        # determine position sizing-hedging
                        if "hedgingSpot" in strategy_attr["strategy"]:
                            min_position_size = - notional
                        # log.error(f'min_position_size {min_position_size}')
                        # log.error(strategy_attr["strategy"])

                        exit_order_allowed = (
                            await self.is_send_exit_or_additional_order_allowed(
                                label,
                                open_trade_strategy,
                                open_order_mgt,
                                strategy_attr,
                                min_position_size,
                            )
                        )
                        exit_order_allowed['instrument'] = instrument
                        
                        log.warning(f'exit_order_allowed {exit_order_allowed}')
                        log.warning( "hedgingSpot" in strategy_attr["strategy"])
                        if exit_order_allowed ['exit_orders_limit_qty'] not in none_data:
                        
                            len_open_order_label_short = 0 if open_order_label_short == [] else len (open_order_label_short)
                            len_open_order_label_long = 0 if open_order_label_long == [] else len (open_order_label_long)
                                                            
                            if "hedgingSpot" in strategy_attr["strategy"]:
                                
                                time_threshold: float = (
                            strategy_attr["halt_minute_before_reorder"] * one_minute
                        )
                                open_trade_strategy_max_attr = my_trades_open_mgt.my_trades_max_price_attributes_filteredBy_label(open_trade_strategy)
                                #log.error (f'open_trade_strategy_max_attr {open_trade_strategy_max_attr}')
                                delta_time: int = server_time - open_trade_strategy_max_attr ['timestamp'] 
                                exceed_threshold_time: int = delta_time > time_threshold
                                open_trade_strategy_max_attr_price = open_trade_strategy_max_attr ['max_price']
                                
                                pct_prc = open_trade_strategy_max_attr_price * strategy_attr['cut_loss_pct']
                                tp_price = open_trade_strategy_max_attr_price - pct_prc
                                resupply_price = open_trade_strategy_max_attr_price + pct_prc
                                #log.warning(f'tp_price {tp_price} resupply_price {resupply_price} ')
                                
                                # closing order
                                if best_bid_prc < tp_price and len_open_order_label_long < 1:
                                    exit_order_allowed['entry_price'] = best_bid_prc
                                    exit_order_allowed['label'] = exit_order_allowed ['label_closed']
                                    exit_order_allowed['side'] = exit_order_allowed ['exit_orders_limit_side']
                                    exit_order_allowed['size'] = exit_order_allowed ['exit_orders_limit_qty']
                                    exit_order_allowed['type'] = exit_order_allowed ['exit_orders_limit_type']
                                    await self.send_limit_order (exit_order_allowed)
                                    
                                # new order           
                                if best_ask_prc > resupply_price and exceed_threshold_time and len_open_order_label_short < 1:                                    
                                    
                                    exit_order_allowed['entry_price'] = best_ask_prc
                                    exit_order_allowed['take_profit_usd'] = best_ask_prc
                                    exit_order_allowed['side'] = 'sell'
                                    exit_order_allowed['type'] = 'limit'
                                    exit_order_allowed['size'] = int(max (notional * 10/100, 2))
                                    exit_order_allowed['label'] = label_numbering.labelling(
                                    "open", strategy_label
                                )
                                    await self.send_limit_order (exit_order_allowed)
                            else :
                                                              
                                exit_order_allowed['label'] = exit_order_allowed ['label_closed']
                                exit_order_allowed['side'] = exit_order_allowed ['exit_orders_limit_side']
                                
                                if 'limit' in exit_order_allowed ['exit_orders_limit_type'] \
                                    and exit_order_allowed ['len_order_limit'] == 0:
                                    exit_order_allowed['type'] = exit_order_allowed ['exit_orders_limit_type']
                                    exit_order_allowed['take_profit_usd'] = strategy_attr ['take_profit_usd'] 
                                    exit_order_allowed['size'] = exit_order_allowed ['exit_orders_limit_qty']
                                    await self.send_limit_order (exit_order_allowed)

                                log.warning(f"exit_order_allowed limit {exit_order_allowed}")
                                
                                if 'stop_market' in exit_order_allowed ['exit_orders_market_type']\
                                    and exit_order_allowed ['len_order_market'] == 0:
                                    exit_order_allowed['cut_loss_usd'] = strategy_attr ['cut_loss_usd']  
                                    exit_order_allowed['type'] = exit_order_allowed ['exit_orders_market_type']
                                    exit_order_allowed['size'] = exit_order_allowed ['exit_orders_market_qty']
                                    await self.send_market_order (exit_order_allowed)
                                
                                log.error(f"exit_order_allowed stop_market {exit_order_allowed}")
                                
                        if exit_order_allowed ['exit_orders_market_qty'] != 0:
                            log.debug(f"exit_orders_market_type")

                for instrument in instrument_transactions:
                    #log.critical(f"{instrument}")

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
                    log.debug (strategies)

                    # execute each strategy
                    for strategy_attr in strategies:
                        # result example: 'hedgingSpot'
                        strategy_label = strategy_attr["strategy"]
                        time_threshold: float = (
                            strategy_attr["halt_minute_before_reorder"] * one_minute
                        )
                        time_threshold_avg_up: float = time_threshold * 12 * 4

                        remain_unhedged = check_spot_hedging["remain_unhedged_size"]


                        label_closed: str = f"{strategy_label}-closed"

                        # determine position sizing-general strategy
                        min_position_size: float = position_sizing.pos_sizing(
                            strategy_attr["take_profit_usd"],
                            strategy_attr["entry_price"],
                            notional,
                            strategy_attr["equity_risked_pct"],
                        )

                        # determine position sizing-hedging
                        if "hedgingSpot" in strategy_attr["strategy"]:
                            min_position_size = check_spot_hedging["all_hedging_size"]
                        log.error(f" strategy_label  {strategy_label}")
                        open_trade_strategy = ([o  for o in my_trades_open if strategy_label in o['label'] ])

                        open_order_allowed = (
                            await self.is_send_exit_or_additional_order_allowed(
                                strategy_label,
                                open_trade_strategy,
                                open_order_mgt,
                                strategy_attr,
                                min_position_size,
                            )
                        )
                        log.error(f" {strategy_attr} send_main_order_allowed  {open_order_allowed}")
                        
                        # add some extra params to strategy
                        strategy_attr.update(
                            {
                                "instrument": instrument,
                                "size": min_position_size,
                                "label_numbered": label_numbering.labelling(
                                    "open", strategy_label
                                ),
                                "label_closed_numbered": label_numbering.labelling(
                                    "closed", strategy_label
                                ),
                            }
                        )


        except Exception as error:
            catch_error(error, 30)

    async def will_new_open_order_create_over_hedge(
        self, label, actual_hedging_size: float, min_position_size: float
    ) -> None:
        """ """

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
            current_open_orders_size = (
                open_order_mgt.open_orders_api_basedOn_label_items_size(label_open)
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

    except KeyboardInterrupt:
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 30)
