#!/usr/bin/python3

# built ins
import asyncio
from time import sleep
#import orjson

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
import deribit_get
from transaction_management.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools, string_modification as str_mod
from risk_management import  position_sizing
from configuration import label_numbering, config
from strategies import entries_exits, grid_perpetual as grid
from db_management import sqlite_management
# from market_understanding import futures_analysis

ONE_MINUTE: int = 60000
NONE_DATA: None = [0, None, []]

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
        return deribit_get.GetPrivateData(
                self.connection_url, self.client_id, self.client_secret, self.currency
            )

    async def get_sub_accounts(self) -> list:
        """ """

        try:
            private_data = await self.get_private_data()
            result: dict = await private_data.get_subaccounts()

        except Exception as error:
            catch_error(error)
        return result["result"]

    async def get_open_orders_from_exchange(self) -> list:
        """ """
        private_data = await self.get_private_data()
        open_ordersREST: dict = await private_data.get_open_orders_byCurrency()
        return open_ordersREST["result"]

    async def open_orders_from_exchange(self) -> object:
        """ """
        open_ordersREST: list = await self.get_open_orders_from_exchange()

        return open_orders_management.MyOrders(open_ordersREST)

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

    async def send_combo_orders(self, params) -> None:
        """ """

        private_data = await self.get_private_data()
        await private_data.send_triple_orders(params)

    async def compute_notional_value(self, index_price: float, equity: float) -> float:
        """ """
        return index_price * equity

    async def querying_all(self, table: list, 
                           database: str = "databases/trading.sqlite3") -> dict:
        """ """
        result = await sqlite_management.querying_table (table, 
                                                         database
                                                         ) 
        
        return  dict(
            all= [] if result in NONE_DATA \
                else (result),
            list_data_only= [] if result in NONE_DATA \
                else str_mod.parsing_sqlite_json_output([o['data'] for o in result])
                    )

    async def get_net_sum_strategy_super_main(self, my_trades_open_sqlite: list, 
                           label: str) -> float:
        """ """
        return  0 if my_trades_open_sqlite==[] \
                else sum([o['amount_dir'] for o in my_trades_open_sqlite['all'] \
                    if  str_mod.parsing_label(o['label_main'])['super_main'] == str_mod.parsing_label(label)['super_main']])

    def compute_position_leverage_and_delta(
        self, notional: float, my_trades_open: dict
    ) -> float:
        
        position_leverage_and_delta = position_sizing.compute_delta(notional, my_trades_open)
        return dict(
            delta= position_leverage_and_delta['delta'],
            leverage= position_leverage_and_delta['leverage'],
        )

    def reading_from_db(
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

        path_portfolio: str = system_tools.provide_path_for_file(
            "portfolio", self.currency
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

        # at start, usually position == None
        if positions in NONE_DATA:
            positions = positions_from_sub_account  # await self.get_positions ()
            pickling.replace_data(path_positions, positions)

        # log.debug (my_trades_open)
        if portfolio in NONE_DATA:
            portfolio = await self.get_account_summary()
            pickling.replace_data(path_portfolio, portfolio)
            portfolio = pickling.read_data(path_portfolio)

        return {
            "positions": positions,
            "positions_from_sub_account": positions_from_sub_account,
            "open_orders_from_sub_account": open_orders_from_sub_account,
            "portfolio": portfolio
        }

    #! ########### end of will be deleted ##############################################################################

    async def cancel_by_order_id(self, open_order_id) -> None:
        private_data = await self.get_private_data()

        result = await private_data.get_cancel_order_byOrderId(open_order_id)
        log.warning (f'CANCEL_by_order_id {result}')
        return result

    async def current_server_time(self) -> float:
        """ """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time["result"]

    async def cancel_orders_based_on_time_threshold(
        self, server_time, label, time_threshold: int= None
    ) -> float:
        """ """
        three_minute = ONE_MINUTE* 3

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

            open_orders_lastUpdateTStamp_min = min(open_orders_lastUpdateTStamps)
            open_orders_deltaTime: int = server_time - open_orders_lastUpdateTStamp_min

            open_order_id: list = open_order_mgt.open_orders_api_basedOn_label_last_update_timestamps_min_id(
                label
            )

            log.debug(f'open_orders_deltaTime {open_orders_deltaTime} {open_orders_deltaTime > three_minute} \
                open_orders_lastUpdateTStamps {open_orders_lastUpdateTStamps}')    

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
        log.error(f'open_orderLabelCLosed {open_orderLabelCLosed}')

        if open_orderLabelCLosed != None:
            for label_closed in open_orderLabelCLosed:
                is_closed_label_exist = my_trades_open_mgt.closed_open_order_label_in_my_trades_open(
                    label_closed
                )
                log.error(f'is_closed_label_exist {is_closed_label_exist}')

                if is_closed_label_exist == False:
                    open_orders = open_order_mgt.open_orders_api()
                    open_order_id = [
                        o["order_id"]
                        for o in open_orders
                        if str(label_closed)[-10:] in o["label"]
                    ][0]
                    log.critical(f'open_order_id {open_order_id}')
                    await self.cancel_by_order_id(open_order_id)

    async def is_size_consistent(self, sum_my_trades_open_sqlite_all_strategy, size_from_positions) -> bool:
        """ """

        log.warning (f' sum_my_trades_open_sqlite_all_strategy {sum_my_trades_open_sqlite_all_strategy}')
        log.warning (f' size_from_positions {size_from_positions}')
        return sum_my_trades_open_sqlite_all_strategy == size_from_positions

    async def is_open_orders_consistent(self, open_orders_from_sub_account_get, open_orders_open_from_db) -> bool:
        """ """

        len_open_orders_from_sub_account_get = len(open_orders_from_sub_account_get)
        
        len_open_orders_open_from_db = len(open_orders_open_from_db)
        
        return len_open_orders_from_sub_account_get == len_open_orders_open_from_db
        
    async def resolving_inconsistent_open_orders(self, open_orders_from_sub_account_get, open_orders_open_from_db) -> None:
        """ """

        if open_orders_open_from_db == []:
            for order in open_orders_from_sub_account_get:
                await sqlite_management.insert_tables('orders_all_json',order)  
    
        else:
            if open_orders_open_from_db != []:
                for order in open_orders_open_from_db:
                    log.error (order)
                    where_filter = f"order_id"
                    order_id = order['order_id']
                    await sqlite_management.deleting_row('orders_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            order_id)
                    
            for order in open_orders_from_sub_account_get:
                await sqlite_management.insert_tables('orders_all_json',order)    

        system_tools.sleep_and_restart_program(1)

    async def send_market_order(self, params) -> None:
        """ """

        private_data = await self.get_private_data()
        await private_data.send_market_order(params)

    async def send_limit_order(self, params) -> None:
        """ """

        private_data = await self.get_private_data()
        await private_data.send_limit_order(params)

    async def my_trades_open_sqlite_detailing (self, transactions, label, detail_level: str = None) -> list:
        """ 
        detail_level: main/individual
        """
        if detail_level== 'main':

            result = [] if transactions==[] \
                else ([o for o in transactions \
                    if  str_mod.parsing_label(o['label_main'])['main'] == str_mod.parsing_label(label)['main']])
            #log.warning(f'my_trades_open_sqlite_detailing {result}')
        if detail_level== 'individual':
            result = [] if transactions==[] else ([
            o for o in transactions if  str_mod.parsing_label(o['label_main'])['transaction_net'] == label
        ])
        if detail_level== None:
            result = [] if transactions==[] else transactions

        return   result

    async def sum_my_trades_open_sqlite (self, transactions, label, detail_level: str = None) -> None:
        """ 
        detail_level: main/individual
        """
        #log.error (transactions)
        
        if detail_level== 'main':
            result = 0 if transactions==[] else sum([
            o['amount_dir'] for o in await self.my_trades_open_sqlite_detailing (transactions, label, detail_level)])
        if detail_level== 'individual':
            result = 0 if transactions==[] else sum([
            o['amount_dir'] for o in await self.my_trades_open_sqlite_detailing (transactions, label, detail_level) ])

        if detail_level== None:
            result = 0 if transactions==[] else sum([
            o['amount_dir'] for o in await self.my_trades_open_sqlite_detailing (transactions, label) ])

        return   result

    async def clean_up_closed_transactions (self, transactions_all) -> None:
        """ 
        closed transactions: buy and sell in the same label id = 0. When flagged:
        1. remove them from db for open transactions/my_trades_all_json
        2. move them to table for closed transactions/my_trades_closed_json
        """
                
        #get_closed_labels
        
        if transactions_all !=[]:
            trades_with_closed_labels = [o for o in transactions_all if 'closed' in o['label_main'] ]
            log.warning (f'trades_with_closed_labels {trades_with_closed_labels}')
            
            for transaction in trades_with_closed_labels:            
                log.warning (transaction)
                message = f'closed trans {transaction}'
                log.warning (f'{message}')
                #await telegram_bot_sendtext(message, "general_error")

                # get label net
                label_net = str_mod.remove_redundant_elements(
                        [str_mod.parsing_label(o["label_main"])['transaction_net']
                            for o in [transaction]])[0]
                
                # get transactions net
                transactions_under_label_main = 0 \
                    if transaction== [] \
                        else ([o for o in transactions_all \
                            if str_mod.parsing_label(o['label_main'])['transaction_net'] == label_net])
                
                log.warning (transactions_under_label_main)
                # get net sum of the transactions open and closed
                net_sum = [] if transactions_under_label_main == []\
                    else sum([o['amount_dir'] for o in transactions_under_label_main ])

                log.warning (net_sum)
                log.warning (len(transactions_under_label_main))
                if len(transactions_under_label_main) >2:
                    
                    #get_closed_labels under_label_main
                    transactions_closed= ([o for o in transactions_under_label_main if 'closed' in o['label_main'] ])

                    #get_closed_labels under_label_main
                    transactions_open= ([o for o in transactions_under_label_main if 'open' in o['label_main'] ])

                    # get minimum trade seq from closed/open label main (to be paired vs open/closed label)
                    min_closed= min([o['trade_seq'] for o in transactions_closed ])
                    min_open= min([o['trade_seq'] for o in transactions_open ])
                    
                    #combining open vs closed transactions
                    transactions_under_label_main = ([o for o in transactions_under_label_main \
                        if o['trade_seq'] == min_closed or 'open' in o['label_main'] ])
                    
                    if len(transactions_open)>1:
                        transactions_under_label_main = ([o for o in transactions_under_label_main \
                        if o['trade_seq'] == min_closed or o['trade_seq'] == min_open  ])
                        
                    log.critical (f'transactions_under_label_main {transactions_under_label_main}')
                    log.critical (f'transactions_open {transactions_open}')
                    # get net sum of the transactions open and closed
                    net_sum = [] if transactions_under_label_main == [] else  sum([o['amount_dir'] for o in transactions_under_label_main ])
                    
                    # excluded trades closed labels from above trade seq
                    result_transactions_excess = ([o for o in transactions_closed if o['trade_seq'] != min_closed ])
                    transactions_excess = str_mod.parsing_sqlite_json_output([o['data'] for o in result_transactions_excess])
                    
                    for transaction in transactions_excess:
                        trade_seq = transaction['trade_seq']
                        label = transaction['label']
                        tstamp= transaction['timestamp']
                        new_label= str_mod.parsing_label(label, tstamp) ['flipping_closed']
                        transaction['label']= new_label
                        log.critical (transaction)
                        
                        where_filter = f"trade_seq"
                        await sqlite_management.deleting_row('my_trades_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            trade_seq
                                                            )
                        await sqlite_management.insert_tables('my_trades_all_json',transaction)
                        # refreshing data
                        system_tools.sleep_and_restart_program(1)
                
                #log.error (f' result {result}')
                log.error (net_sum)
                if net_sum ==0 :
                    # get trade seq
                    result = ([o['trade_seq']   for o in transactions_under_label_main ])
                    log.critical (f' result sum 0 {result}')
                    
                    for res in result:
                        #log.critical (res)
                        my_trades_open_sqlite: list = await self.querying_all('my_trades_all_json')
                        my_trades_open: list = my_trades_open_sqlite ['list_data_only']
                        result_to_dict =  ([o for o in my_trades_open if o['trade_seq'] == res])
                        #log.debug (f' result_to_dict {result_to_dict}')
                        where_filter = f"trade_seq"
                        await sqlite_management.deleting_row('my_trades_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            res
                                                            )
                        await sqlite_management.insert_tables('my_trades_closed_json',result_to_dict)
                    
                    # refreshing data
                    system_tools.sleep_and_restart_program(1)
    
    async def is_send_order_allowed(
        self,
        label,
        open_trade_strategy: list,
        open_orders: object,
        strategy_attr: list,
        min_position_size: float,
    ) -> None:
        """ 
        To open/settle transactions 
        """

        # formatting label: strategy & int. Result example: 'hedgingSpot'/'supplyDemandShort60'
        label_main = str_mod.parsing_label(label)['main']
        
        my_trades_open_sqlite_init: list = await self.querying_all('my_trades_all_json')
        my_trades_open_sqlite: list = my_trades_open_sqlite_init['all']

        # get net buy-sell position
        net_sum_current_position: list = await self.sum_my_trades_open_sqlite(my_trades_open_sqlite, label_main, 'main')
        
        try:
            label_int = str_mod.parsing_label(label)['int']
            
        except:
            label_int = None

        log.warning(f'LABEL {label} label_main {label_main} label_int {label_int}')
        open_orders_strategy = open_orders.open_orders_api_basedOn_label(label_main)

        # get net buy-sell order limit
        open_orders_strategy_limit = [
            o for o in open_orders_strategy if "limit" in o["order_type"]
        ]
        net_sum_open_orders_strategy_limit = (
            0
            if open_orders_strategy_limit == []
            else open_orders.net_sum_order_size(open_orders_strategy_limit)
        )
        len_transactions_open_orders_strategy_limit = (
            0 if open_orders_strategy_limit == [] else len(open_orders_strategy_limit)
        )

        # get net buy-sell order market
        open_orders_strategy_market = [
            o for o in open_orders_strategy if "market" in o["order_type"]
        ]
        net_sum_open_orders_strategy_market = (
            0
            if open_orders_strategy_market == []
            else open_orders.net_sum_order_size(open_orders_strategy_market)
        )
        len_transactions_open_orders_strategy_market = (
            0 if open_orders_strategy_market == [] else len(open_orders_strategy_market)
        )

        # get default side from the strategy configuration
        side_main = strategy_attr["side"]

        determine_size_and_side = open_orders.calculate_order_size_and_side_for_outstanding_transactions(
            label,
            side_main,
            net_sum_current_position,
            net_sum_open_orders_strategy_limit,
            net_sum_open_orders_strategy_market,
            min_position_size,
        )
        log.debug(f'net_sum_current_position {net_sum_current_position} \
            net_sum_open_orders_strategy_limit {net_sum_open_orders_strategy_limit} \
                net_sum_open_orders_strategy_limit {net_sum_open_orders_strategy_limit}\
                    net_sum_open_orders_strategy_market {net_sum_open_orders_strategy_market}')
        
        #log.warning(f'determine_size_and_side {determine_size_and_side}')

        determine_size_and_side["len_order_market"] = len_transactions_open_orders_strategy_limit
        
        determine_size_and_side["len_order_limit"] = len_transactions_open_orders_strategy_market
        label_open = label_numbering.labelling("open", label_main)
        determine_size_and_side["label"] = label_open

        if net_sum_current_position == 0 and label_int == None:
            
            label_int = str_mod.parsing_label(label_open)['int']

            label_closed = f"{label_main}-closed-{label_int}"

            determine_size_and_side["label_closed"] = label_closed
            
        # the strategy has outstanding position
        if net_sum_current_position != 0 and label_int != None:
            label_closed = f"{label_main}-closed-{label_int}"

            determine_size_and_side["label_closed"] = label_closed

            # the strategy has outstanding position
            if open_trade_strategy != []:

                size_as_per_label = [
                    o["amount"]
                    for o in open_trade_strategy
                    if label_int in o["label"]
                ][0]

                open_trade_hedging_price_max = max(
                    [o["price"] for o in open_trade_strategy]
                )
                open_trade_hedging_selected = [
                    o
                    for o in open_trade_strategy
                    if o["price"] == open_trade_hedging_price_max
                ]

                if (
                    label_int
                    in [o["label"] for o in open_trade_hedging_selected][0]
                ):
                    determine_size_and_side["exit_orders_limit_qty"] = size_as_per_label

                else:
                    determine_size_and_side["exit_orders_limit_qty"] = 0

        return determine_size_and_side

    async def closing_transactions(self, 
                                   label_transactions,
                                   instrument, 
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_mgt,
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions, 
                                   server_time) -> float:
        """ """
                    
        reading_from_database: dict = await self.reading_from_database()
        clean_up_closed_transactions: list = await self.clean_up_closed_transactions(my_trades_open_all)
        log.error (f'clean_up_closed_transactions {clean_up_closed_transactions}')

        my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')
        my_trades_open_all: list = my_trades_open_sqlite['all']
        #log.error (my_trades_open_all)
        
        my_trades_open: list = my_trades_open_sqlite ['list_data_only']
        
        open_orders_sqlite: list = await self.querying_all('orders_all_json')

        # open orders data
        open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']

        open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
        #log.warning (f'open_orders_from_sub_account_get {open_orders_from_sub_account_get} {len(open_orders_from_sub_account_get)} {len(open_orders_open_from_db)}')

        # Creating an instance of the open order  class
        open_order_mgt = open_orders_management.MyOrders(open_orders_open_from_db)

        # result example: 'hedgingSpot-1678610144572'/'supplyDemandShort60-1678753445244'
        for label in label_transactions:
            log.critical(f" {label}")
            grids=   grid.GridPerpetual(my_trades_open, open_orders_sqlite) 
            
            check_orders_with_the_same_labels= await grids.open_orders_as_per_main_label(label)
            log.warning(f" check_orders_with_the_same_labels {check_orders_with_the_same_labels}")
            if check_orders_with_the_same_labels ['len_result'] > 1:
                cancelled_id= [o for o in open_orders_open_from_db if o['label'] == label ]
                log.warning(f" cancelled_id {cancelled_id}")
                await self.cancel_by_order_id(cancelled_id[0])
                system_tools.sleep_and_restart_program(1)

            # result example: 'hedgingSpot'/'supplyDemandShort60'
            label_main = str_mod.parsing_label(label)['main']

            open_order_label = open_order_mgt.open_orders_api_basedOn_label(label)

            open_order_label_short = [o for o in open_order_label if o["direction"] == "sell"]
            
            open_order_label_long = [o for o in open_order_label if o["direction"] == "buy"]
            
            # get startegy details
            strategy_attr = [o for o in strategies if o["strategy"] == label_main][0]                        
            
            my_trades_open_sqlite_individual_strategy: list = await self.my_trades_open_sqlite_detailing(my_trades_open_all, label, 'individual')
            my_trades_open_sqlite_main_strategy: list = await self.my_trades_open_sqlite_detailing(my_trades_open_all, label, 'main')

            sum_my_trades_open_sqlite_all_strategy: list = await self.sum_my_trades_open_sqlite(my_trades_open_all, label)
            size_is_consistent: bool = await self.is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions)
            open_order_is_consistent: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)
            
            if size_is_consistent and open_order_is_consistent:
                
                open_trade_strategy = str_mod.parsing_sqlite_json_output([o['data'] for o in my_trades_open_sqlite_main_strategy])
                open_trade_strategy_label = str_mod.parsing_sqlite_json_output([o['data'] for o in my_trades_open_sqlite_individual_strategy])

                instrument: list= [o["instrument_name"] for o in open_trade_strategy_label][0]
                
                ticker: list =  self.reading_from_db("ticker", instrument)

                if ticker !=[]:
                        
                    # index price
                    index_price: float = ticker[0]["index_price"]

                    # get bid and ask price
                    best_bid_prc: float = ticker[0]["best_bid_price"]
                    best_ask_prc: float = ticker[0]["best_ask_price"]

                    # obtain spot equity
                    equity: float = portfolio[0]["equity"]

                    # compute notional value
                    notional: float = await self.compute_notional_value(index_price, equity)
                
                    net_sum_strategy = await self.get_net_sum_strategy_super_main(my_trades_open_sqlite, open_trade_strategy_label[0]['label'] )
                                                
                    log.error (f'sum_my_trades_open_sqlite_all_strategy {sum_my_trades_open_sqlite_all_strategy} net_sum_strategy {net_sum_strategy}')      
            
                    my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')
                            
                            
                    check_orders_with_the_same_labels= await grids.open_orders_as_per_main_label(label)
                    log.warning(f" check_orders_with_the_same_labels {check_orders_with_the_same_labels}")
                    
                    log.debug (f'open_trade_strategy_label   {open_trade_strategy_label}')
                    my_trades_closed_sqlite: list = await self.querying_all('my_trades_closed_json')
                    my_trades_closed: list = my_trades_closed_sqlite ['list_data_only']
                    my_trades_closed_trd_seq: list =  ([o['trade_seq'] for o in my_trades_closed])
                    my_trades_open_closed_label: list =  ([o['label'] for o in my_trades_open if 'closed' in o['label']])
                    is_closed = open_trade_strategy_label[0]['trade_seq'] in my_trades_closed_trd_seq
                    is_labelled = open_trade_strategy_label[0]['label'] in my_trades_open_closed_label
                    
                    if "every" in strategy_attr["strategy"]: 
            
                    # avoid reorder closed trades:
                        # restart after deleting completed trades
                        # avoid send order for trades with 0 net sum 
                                                        
                        if open_trade_strategy_label != []\
                            and net_sum_strategy != 0\
                                and is_closed == False\
                                    and is_labelled == False:                                  
                                                                            
                            params = await grids.get_params_orders_closed (open_trade_strategy_label,
                                                                        best_bid_prc,
                                                                        best_ask_prc)
                            log.debug (f'params {params}')

                            if params["order_buy"] or params["order_sell"]:                                                                                                                        
                                await self.send_limit_order(params)
                                system_tools.sleep_and_restart_program(1)
                                
                    else:
                        
                        min_position_size: float = position_sizing.pos_sizing(
                            strategy_attr["take_profit_usd"],
                            strategy_attr["entry_price"],
                            notional,
                            strategy_attr["equity_risked_pct"],
                        )

                        # determine position sizing-hedging
                        if "hedgingSpot" in strategy_attr["strategy"] :
                            min_position_size = -notional

                        exit_order_allowed = await self.is_send_order_allowed(
                            label,
                            open_trade_strategy_label,
                            open_order_mgt,
                            strategy_attr,
                            min_position_size,
                        )
                        exit_order_allowed["instrument"] = instrument

                        #log.error (f' label {label}')
                        label_id= str_mod.parsing_label(label)['int']
                        label_closed = f'''{strategy_attr["strategy"]}-closed-{label_id}'''
                        #log.error (f' label {label} label_closed {label_closed} label_closed {label_closed} min_position_size {min_position_size}')
                        
                        if exit_order_allowed["exit_orders_limit_qty"] not in NONE_DATA:

                            len_open_order_label_short = (
                                0
                                if open_order_label_short == []
                                else len(open_order_label_short)
                            )
                            len_open_order_label_long = (0 if open_order_label_long == []  
                                                         else len(open_order_label_long))

                            if "hedgingSpot" in strategy_attr["strategy"]:

                                time_threshold: float = (strategy_attr["halt_minute_before_reorder"] * ONE_MINUTE * 15)
                                
                                open_trade_strategy_max_attr = my_trades_open_mgt.my_trades_max_price_attributes_filteredBy_label(
                                    open_trade_strategy)

                                delta_time: int = server_time - open_trade_strategy_max_attr["timestamp"]
                                
                                exceed_threshold_time: int = delta_time > time_threshold
                                open_trade_strategy_max_attr_price = open_trade_strategy_max_attr["max_price"]

                                pct_prc = (open_trade_strategy_max_attr_price * strategy_attr["cut_loss_pct"])
                                
                                tp_price = open_trade_strategy_max_attr_price - pct_prc
                                
                                resupply_price = (open_trade_strategy_max_attr_price + pct_prc)
                                log.critical (f' exit_order_allowed {exit_order_allowed}')

                                # closing order
                                if (
                                    best_bid_prc < tp_price
                                    and len_open_order_label_long < 1
                                ):
                                    exit_order_allowed["entry_price"] = best_bid_prc
                                    exit_order_allowed["label"] = label_closed
                                    exit_order_allowed["side"] = exit_order_allowed[
                                        "exit_orders_limit_side"
                                    ]
                                    exit_order_allowed["size"] = exit_order_allowed[
                                        "exit_orders_limit_qty"
                                    ]
                                    exit_order_allowed["type"] = exit_order_allowed[
                                        "exit_orders_limit_type"
                                    ]
                                    await self.send_limit_order(exit_order_allowed)

                                # new order
                                if (
                                    best_ask_prc > resupply_price
                                    and exceed_threshold_time
                                    and len_open_order_label_short < 1
                                ):

                                    exit_order_allowed["entry_price"] = best_ask_prc
                                    exit_order_allowed["take_profit_usd"] = best_ask_prc
                                    exit_order_allowed["side"] = "sell"
                                    exit_order_allowed["type"] = "limit"
                                    exit_order_allowed["size"] = int(
                                        max(notional * 10 / 100, 2)
                                    )
                                    exit_order_allowed[
                                        "label"
                                    ] = label_numbering.labelling(
                                        "open", label_main
                                    )
                                    await self.send_limit_order(exit_order_allowed)
                                    system_tools.sleep_and_restart_program(1)
                            else:
                                log.warning(f"exit_order_allowed limit {exit_order_allowed}")
                                
                                strategy_label_int = str_mod.parsing_label(exit_order_allowed ['label'])['int']
                                label_closed = f"{label_main}-closed-{strategy_label_int}"
                                exit_order_allowed.update({"label": label_closed})
                                log.debug (strategy_label_int)
                                log.debug (label_closed)

                                exit_order_allowed["label"] = label_closed
                                exit_order_allowed["side"] = exit_order_allowed["exit_orders_limit_side"]

                                if exit_order_allowed["len_order_limit"] == 0:
                                    exit_order_allowed["type"] = exit_order_allowed["exit_orders_limit_type"]
                                    exit_order_allowed["take_profit_usd"] = strategy_attr["take_profit_usd"]
                                    exit_order_allowed["size"] = exit_order_allowed["exit_orders_limit_qty"]
                                    await self.send_limit_order(exit_order_allowed)

                                if exit_order_allowed["len_order_market"] == 0:
                                    exit_order_allowed["cut_loss_usd"] = strategy_attr["cut_loss_usd"]
                                    exit_order_allowed["type"] = exit_order_allowed["exit_orders_market_type"]
                                    exit_order_allowed["size"] = exit_order_allowed["exit_orders_market_qty"]
                                    await self.send_market_order(exit_order_allowed)
                                    
                                system_tools.sleep_and_restart_program(1)

                        if exit_order_allowed["exit_orders_market_qty"] != 0:
                            log.debug(f"exit_orders_market_type")
            else:
                log.critical (f' size_is_consistent {size_is_consistent}  open_order_is_consistent {open_order_is_consistent}')
                await telegram_bot_sendtext('size or open order is inconsistent', "general_error")
                await catch_error('size or open order is inconsistent', 10)
            
    async def opening_transactions(self, 
                                   instrument, 
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions, 
                                   server_time) -> None:
        """ """

        try:
            reading_from_database: dict = await self.reading_from_database()
        
            my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')
            my_trades_open_all: list = my_trades_open_sqlite['all']
            #log.error (my_trades_open_all)
            
            my_trades_open: list = my_trades_open_sqlite ['list_data_only']
            
            open_orders_sqlite: list = await self.querying_all('orders_all_json')
            open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']
            log.critical (f' open_orders_open_from_db {open_orders_open_from_db}')
            ticker =  self.reading_from_db("ticker", instrument)
            grids=  grid.GridPerpetual(my_trades_open, open_orders_sqlite) 
            
            
            open_order_mgt = open_orders_management.MyOrders(open_orders_open_from_db)
            
            open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
            #log.warning (f'open_orders_from_sub_account_get {open_orders_from_sub_account_get} {len(open_orders_from_sub_account_get)} {len(open_orders_open_from_db)}')
        
            # Creating an instance of the my-Trade class
            my_trades_open_mgt: object = myTrades_management.MyTrades(my_trades_open)
            await self.search_and_drop_orphan_closed_orders(open_order_mgt, my_trades_open_mgt)
            
            if ticker !=[]:

                # get bid and ask price
                best_bid_prc = ticker[0]["best_bid_price"]
                best_ask_prc = ticker[0]["best_ask_price"]
                
                # index price
                index_price: float = ticker[0]["index_price"]
        
                # obtain spot equity
                equity: float = portfolio[0]["equity"]
        
                # compute notional value
                notional: float = await self.compute_notional_value(index_price, equity)

                # execute each strategy
                for strategy_attr in strategies:
                    strategy_label = strategy_attr["strategy"]
                    check_orders_with_the_same_labels= await grids.open_orders_as_per_main_label(strategy_label)
                    log.warning(f" check_orders_with_the_same_labels {check_orders_with_the_same_labels}")
                    
                    if check_orders_with_the_same_labels ['len_result'] > 1:
                        log.warning( [o for o in open_orders_open_from_db if strategy_label in o['label']  ])
                        cancelled_id= [o['order_id'] for o in open_orders_open_from_db if strategy_label in o['label']] [0]
                        log.warning(f" cancelled_id {cancelled_id}")
                        await self.cancel_by_order_id(cancelled_id)
                        system_tools.sleep_and_restart_program(1)
                
                    # result example: 'hedgingSpot'
                    
                    log.critical (strategy_label)
                    time_threshold: float = (strategy_attr["halt_minute_before_reorder"] * ONE_MINUTE)
                    net_sum_strategy = await self.get_net_sum_strategy_super_main(my_trades_open_sqlite, strategy_label)
                    log.debug (f'net_sum_strategy   {net_sum_strategy}')
                    
                    sum_my_trades_open_sqlite_all_strategy: list = await self.sum_my_trades_open_sqlite(my_trades_open_all, strategy_label)
                    size_is_consistent: bool = await self.is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions)
                    open_order_is_consistent: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)
                    if open_order_is_consistent == False:
                        await self.resolving_inconsistent_open_orders(open_orders_from_sub_account_get, open_orders_open_from_db)
                    
                    if size_is_consistent and open_order_is_consistent:
                                                    
                        open_trade_strategy = [o for o in my_trades_open if strategy_label in o["label"]]  
                        
                        #log.critical(f" strategy_label  {strategy_label} open_trade_strategy  {open_trade_strategy}")    
                                                
                        if "every" in strategy_attr["strategy"]:
                            
                            params_order = await grids.get_params_orders_open (strategy_label, notional)
                            log.warning(f" params_order 1  {params_order}")
                            
                            adjusting_size_open_order = await grids.adjusting_size_open_order (params_order["side"], 
                                                                                    params_order["size"], net_sum_strategy)
                            
                            params_order["size"] = adjusting_size_open_order
                            log.critical(f" params_order adjusting_size_open_order  {params_order}")
                            
                            time_threshold: float = (strategy_attr["halt_minute_before_reorder"] * ONE_MINUTE)
                            check_cancellation = open_order_mgt.cancel_orders_based_on_time_threshold(server_time, strategy_label, ONE_MINUTE* 30)

                            if check_cancellation !=None:
                                log.critical(f" check_cancellation  {check_cancellation}")
                                log.critical(check_cancellation['open_orders_deltaTime-exceed_threshold'] \
                                    and check_cancellation['open_order_id'] !=[])
                                if check_cancellation['open_orders_deltaTime-exceed_threshold'] \
                                    and check_cancellation['open_order_id'] !=[]:
                                        await self.cancel_by_order_id(check_cancellation['open_order_id'])
                                        system_tools.sleep_and_restart_program(1)
                            
                            exceed_threshold_time_for_reorder: bool = True if open_trade_strategy ==[] else False
                            
                            if open_trade_strategy !=[]:
                                max_transaction_time = max([o['timestamp'] for o in open_trade_strategy])
                                #log.critical(f" minimum_transaction_time  {max_transaction_time}")
                                delta_time: int = server_time - max_transaction_time
                                exceed_threshold_time_for_reorder: bool = delta_time > time_threshold
                                
                            #log.critical(f" exceed_threshold_time_for_reorder  {exceed_threshold_time_for_reorder}")

                            label_open = label_numbering.labelling("open", strategy_label)
                            params_order.update({"label": label_open})
                            params_order.update({"instrument": instrument})
                            #log.critical(f" params_order A {params_order}")

                            if params_order["side"] == 'buy'\
                                and params_order["len_order_limit"] == 0\
                                    and exceed_threshold_time_for_reorder:
                                    
                                params_order["entry_price"] = best_bid_prc - .05
                                log.critical(f" params_order  {params_order}")
                                log.critical(best_bid_prc)
                                
                                await self.send_limit_order(params_order)
                                system_tools.sleep_and_restart_program(1)

                            if params_order["side"] == 'sell'\
                                and params_order["len_order_limit"] == 0 \
                                    and exceed_threshold_time_for_reorder:
                                    
                                params_order["entry_price"] = best_ask_prc +  .05
                                
                                log.critical(f" params_order  {params_order}")
                                log.critical(best_ask_prc)
                                await self.send_limit_order(params_order)
                                system_tools.sleep_and_restart_program(1)

                        else:
                                     
                            check_cancellation = open_order_mgt.cancel_orders_based_on_time_threshold(server_time, strategy_label, ONE_MINUTE* 30)

                            if check_cancellation !=None:
                                log.critical(f" check_cancellation  {check_cancellation}")
                                log.critical(check_cancellation['open_orders_deltaTime-exceed_threshold'] \
                                    and check_cancellation['open_order_id'] !=[])
                                if check_cancellation['open_orders_deltaTime-exceed_threshold'] \
                                    and check_cancellation['open_order_id'] !=[]:
                                        await self.cancel_by_order_id(check_cancellation['open_order_id'])
                                        system_tools.sleep_and_restart_program(1)
                                                           
                            # determine position sizing-hedging
                            if "hedgingSpot" in strategy_attr["strategy"]:
                                min_position_size: float = -notional

                            open_order_allowed = await self.is_send_order_allowed(
                            strategy_label,
                            open_trade_strategy,
                            open_order_mgt,
                            strategy_attr,
                            min_position_size)
                            
                            log.warning(f" open_order_allowed 1  {open_order_allowed}")
                            
                            if (
                                open_order_allowed["main_orders_qty"] != 0
                                and open_order_allowed["len_order_limit"] == 0):

                                open_order_allowed["instrument"] = instrument
                                open_order_allowed["side"] = open_order_allowed["main_orders_side"]
                                open_order_allowed["type"] = open_order_allowed["main_orders_type"]
                                
                                open_order_allowed["size"] = max(1, int(open_order_allowed["main_orders_qty"]/10))
                                                                    
                                open_order_allowed["label_numbered"] = open_order_allowed ["label"]
                                
                                open_order_allowed["entry_price"] = strategy_attr["entry_price"]
                                open_order_allowed["cut_loss_usd"] = strategy_attr["cut_loss_usd"]
                                open_order_allowed["take_profit_usd"] = strategy_attr["take_profit_usd"]
                                    
                                log.warning(f" open_order_allowed 2  {open_order_allowed}")
                                if "hedgingSpot" in strategy_attr["strategy"]:
                                    open_order_allowed["take_profit_usd"] = best_ask_prc
                                    #log.critical(f" open_order_allowed  {open_order_allowed}")
                                    await self.send_limit_order(open_order_allowed)
                                    system_tools.sleep_and_restart_program(1)
                                
                                else:
                                    open_order_allowed["label_closed_numbered"] = open_order_allowed["label_closed"]
                                    
                                    if open_order_allowed["side"] == 'buy'\
                                        and open_order_allowed["entry_price"] < best_bid_prc :
                                            
                                        open_order_allowed["entry_price"] = best_bid_prc - 1
                                        await self.send_combo_orders(open_order_allowed)

                                    if open_order_allowed["side"] == 'sell'\
                                        and best_ask_prc > open_order_allowed["entry_price"] :
                                            
                                        open_order_allowed["entry_price"] = best_ask_prc + 1
                                        await self.send_combo_orders(open_order_allowed)
                                    system_tools.sleep_and_restart_program(1)

                    else:
                        log.critical (f' size_is_consistent {size_is_consistent}  open_order_is_consistent {open_order_is_consistent}')
                        await telegram_bot_sendtext('size or open order is inconsistent', "general_error")
                        await catch_error('size or open order is inconsistent',5)
                    
        except Exception as error:
            await catch_error(error)

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

                # fetch positions for all instruments
                positions: list = reading_from_database["positions_from_sub_account"][0]
                size_from_positions: float = 0 if positions == [] else positions["size"]
                
                my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')
                my_trades_open_all: list = my_trades_open_sqlite['all']
                my_trades_open: list = my_trades_open_sqlite ['list_data_only']
                
                # obtain instruments future relevant to strategies
                instrument_transactions = [f"{self.currency.upper()}-PERPETUAL"]

                clean_up_closed_transactions: list = await self.clean_up_closed_transactions(my_trades_open_all)
                log.error (f'clean_up_closed_transactions {clean_up_closed_transactions}')
                #log.error (open_orders_open_from_db)
                #open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
                #log.warning (f'open_orders_from_sub_account_get {open_orders_from_sub_account_get} {len(open_orders_from_sub_account_get)} {len(open_orders_open_from_db)}')
                # ?################################## end of gathering basic data #####################################

                # Creating an instance of the my-Trade class
                my_trades_open_mgt: object = myTrades_management.MyTrades(my_trades_open)

                # fetch strategies attributes
                strategies = entries_exits.strategies
                
                #log.error (my_trades_open)
                #log.error ([o["label"] for o in my_trades_open])
                my_trades_open_remove_closed = [] if my_trades_open == [] \
                    else [o for o in my_trades_open if 'closed' not in o["label"]]
                strategy_labels =  [] if my_trades_open_remove_closed == [] \
                    else str_mod.remove_redundant_elements(
                    [
                        str_mod.parsing_label(o["label"])['transaction_net']
                        for o in my_trades_open_remove_closed
                    ])
                #log.error (f'strategy_labels {strategy_labels}')   
            
                # leverage_and_delta = self.compute_position_leverage_and_delta (notional, my_trades_open)
                # log.warning (leverage_and_delta)           
     
                #opening transaction
                for instrument in instrument_transactions:
                    await self.opening_transactions( 
                                   instrument, 
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions, 
                                   server_time)
                    
                # closing transactions
                if strategy_labels != []:
                    await self.closing_transactions( 
                                   strategy_labels,
                                   instrument, 
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_mgt,
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions, 
                                   server_time)
                
        except Exception as error:
            catch_error(error, 30)

async def main():
    connection_url: str = "https://test.deribit.com/api/v2/"

    currency: str = "ETH"
    sub_account = "deribit-147691"

    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]

    connection_url: str = "https://www.deribit.com/api/v2/"

    try:
        syn = ApplyHedgingSpot(
            connection_url=connection_url,
            client_id=client_id,
            client_secret=client_secret,
            currency=currency,
        )

        # get deribit server time
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

        await syn.cancel_orders_based_on_time_threshold(
            server_time, label_hedging
        )

    except Exception as error:
        catch_error(error, 30)

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(main())

    except KeyboardInterrupt:
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 30)
