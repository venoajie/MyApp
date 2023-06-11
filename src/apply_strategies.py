#!/usr/bin/python3

# built ins
import asyncio
#from time import sleep
#import orjson

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
import deribit_get
from transaction_management.deribit import open_orders_management, myTrades_management
from utilities import (
    pickling, 
    system_tools, 
    string_modification as str_mod
    )
from risk_management import  position_sizing
from configuration import config
from strategies import (
    entries_exits, 
    grid_perpetual as grid, 
    hedging_spot, 
    market_maker as MM
    )
from db_management import sqlite_management
# from market_understanding import futures_analysis

ONE_MINUTE: int = 60000
ONE_PCT: float = 1/100
NONE_DATA: None = [0, None, []]

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

async def raise_error(error, idle: int = None) -> None:
    """ """
    await system_tools.raise_error_message(error, idle)

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

    async def get_account_balances_and_transactions_from_exchanges(self) -> list:
        """ """

        try:
            private_data = await self.get_private_data()
            result_sub_account: dict = await private_data.get_subaccounts()
            result_open_orders: dict = await private_data.get_open_orders_byCurrency()
            result_account_summary: dict =  await private_data.get_account_summary()
            result_get_positions: dict =  await private_data.get_positions()

        except Exception as error:
            await raise_error(error)
            
        return dict(
            sub_account= result_sub_account["result"],
            open_orders= result_open_orders["result"],
            account_summary= result_account_summary["result"],
            get_positions= result_get_positions["result"],
            open_orders_instance= open_orders_management.MyOrders(result_open_orders["result"]))
        
    async def get_account_summary(self) -> list:
        """ """

        private_data = await self.get_private_data()

        account_summary: dict = await private_data.get_account_summary()

        return account_summary["result"]

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
        result = await sqlite_management.querying_table (table,  database) 
        
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

    async def get_net_sum_strategy_main(self, my_trades_open_sqlite: list, 
                           label: str) -> float:
        """ """
        return  0 if my_trades_open_sqlite==[] \
                else sum([o['amount_dir'] for o in my_trades_open_sqlite['all'] \
                    if  str_mod.parsing_label(o['label_main'])['main'] == str_mod.parsing_label(label)['main']])

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
        return system_tools.reading_from_db_pickle (end_point, instrument, status)

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
        #log.critical(f' SUB ACCOUNT {sub_account}')
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
        log.info (f'CANCEL_by_order_id {result}')
        
        reading_from_database: dict = await self.reading_from_database()
        open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
        open_orders_sqlite: list = await self.querying_all('orders_all_json')
        open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']
        
        await self.resolving_inconsistent_open_orders(open_orders_from_sub_account_get, open_orders_open_from_db)
        
        return result

    async def current_server_time(self) -> float:
        """ """
        current_time = await deribit_get.get_server_time(self.connection_url)
        return current_time["result"]


    async def transform_wrong_closed_trading_to_open (self, wrong_transaction) -> float:
        """ """
        
        open_label= f'''{str_mod.parsing_label({wrong_transaction})}['main']-open-{str_mod.parsing_label({wrong_transaction})}['int']'''
        
        return open_label

    async def if_order_is_true(self, order, instrument: str = None) -> None:
        """ """
        #log.debug (order)
        if order['order_allowed']:
            
            # get parameter orders
            params= order['order_parameters']
            
            if instrument != None:
                # update param orders with instrument
                params.update({"instrument": instrument})
                
            await self.send_limit_order(params)

    async def if_cancel_is_true(self, order) -> None:
        """ """
        log.debug (order)
        if order['cancel_allowed']:
            
            # get parameter orders
            await self.cancel_by_order_id(order['cancel_id'])
            
    async def is_size_consistent(self, sum_my_trades_open_sqlite_all_strategy, size_from_positions) -> bool:
        """ """

        log.warning (f' size_from_sqlite {sum_my_trades_open_sqlite_all_strategy} size_from_positions {size_from_positions}')

        return sum_my_trades_open_sqlite_all_strategy == size_from_positions

    async def is_open_orders_consistent(self, open_orders_from_sub_account_get, open_orders_open_from_db) -> bool:
        """ """

        len_open_orders_from_sub_account_get = len(open_orders_from_sub_account_get)
        
        len_open_orders_open_from_db = len(open_orders_open_from_db)
        sub_acc= await self.get_account_balances_and_transactions_from_exchanges()
        sub_acc_orders= sub_acc['open_orders']
        log.warning (f' len_open_orders_from_sub_account_get {len_open_orders_from_sub_account_get} len_open_orders_open_from_db {len_open_orders_open_from_db}')
        log.error (f' sub_acc {sub_acc_orders}')
        return len_open_orders_from_sub_account_get == len_open_orders_open_from_db
        
    async def resolving_inconsistent_open_orders(self, open_orders_from_sub_account_get, open_orders_open_from_db) -> None:
        """ """

        if open_orders_open_from_db == []:
            for order in open_orders_from_sub_account_get:
                await sqlite_management.insert_tables('orders_all_json',order)  
    
        else:
            if open_orders_open_from_db != []:
                for order in open_orders_open_from_db:
                    #log.error (order)
                    where_filter = f"order_id"
                    order_id = order['order_id']
                    await sqlite_management.deleting_row('orders_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            order_id)
                    
            for order in open_orders_from_sub_account_get:
                await sqlite_management.insert_tables('orders_all_json',order)    

    async def send_market_order(self, params) -> None:
        """ """

        private_data = await self.get_private_data()
        await private_data.send_market_order(params)

    async def send_limit_order(self, params) -> None:
        """ """       
        
        reading_from_database: dict = await self.reading_from_database()
        open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
        open_orders_sqlite: list = await self.querying_all('orders_all_json')
        open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']
        
        #size_is_consistent: bool = await self.is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions)
        #open_order_is_consistent: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)
        
        #if open_order_is_consistent == False:
        #    await self.resolving_inconsistent_open_orders(open_orders_from_sub_account_get, open_orders_open_from_db)
        #    await system_tools.sleep_and_restart (5)
        
        private_data = await self.get_private_data()
        await private_data.send_limit_order(params)
        
        reading_from_database: dict = await self.reading_from_database()
        open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
        open_orders_sqlite: list = await self.querying_all('orders_all_json')
        open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']
        await self.resolving_inconsistent_open_orders(open_orders_from_sub_account_get, open_orders_open_from_db)

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
                        
        if transactions_all !=[]:
            trades_with_closed_labels = [o for o in transactions_all if 'closed' in o['label_main'] ]
            
            for transaction in trades_with_closed_labels:      
                
                # get label net
                label_net = str_mod.remove_redundant_elements(
                        [str_mod.parsing_label(o["label_main"])['transaction_net']
                            for o in [transaction]])[0]
                
                # get transactions net
                transactions_under_label_main = 0 \
                    if transaction== [] \
                        else ([o for o in transactions_all \
                            if str_mod.parsing_label(o['label_main'])['transaction_net'] == label_net])
                
                #log.info(f'label_net {label_net}')
                #log.info(transactions_under_label_main)
                # get net sum of the transactions open and closed
                net_sum = [] if transactions_under_label_main == []\
                    else sum([o['amount_dir'] for o in transactions_under_label_main ])

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
                    
                    # get net sum of the transactions open and closed
                    net_sum = [] if transactions_under_label_main == [] else  sum([o['amount_dir'] for o in transactions_under_label_main ])
                    #log.critical(transactions_under_label_main)
                    
                    # excluded trades closed labels from above trade seq
                    result_transactions_excess = ([o for o in transactions_closed if o['trade_seq'] != min_closed ])
                    transactions_excess = str_mod.parsing_sqlite_json_output([o['data'] for o in result_transactions_excess])
                    
                    for transaction in transactions_excess:
                        trade_seq = transaction['trade_seq']
                        label = transaction['label']
                        tstamp= transaction['timestamp']
                        new_label= str_mod.parsing_label(label, tstamp) ['flipping_closed']
                        transaction['label']= new_label
                        
                        where_filter = f"trade_seq"
                        await sqlite_management.deleting_row('my_trades_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            trade_seq
                                                            )
                        await sqlite_management.insert_tables('my_trades_all_json',transaction)
                        
                        # refreshing data
                        await system_tools.sleep_and_restart(1)
                
                if net_sum ==0 :
                    
                    # get trade seq
                    result = ([o['trade_seq']   for o in transactions_under_label_main ])
                    #log.info(f' result {result}')
                    
                    for res in result:

                        my_trades_open_sqlite: list = await self.querying_all('my_trades_all_json')
                        my_trades_open: list = my_trades_open_sqlite ['list_data_only']
                        #log.info(f' res {res} ')
                        #log.warning(([o['trade_seq']  for o in my_trades_open ]))
                        #log.critical(([o for o in my_trades_open if o['trade_seq'] == res]))
                        result_to_dict =  ([o for o in my_trades_open if o['trade_seq'] == res])[0]

                        where_filter = f"trade_seq"
                        await sqlite_management.deleting_row('my_trades_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            res
                                                            )
                        await sqlite_management.insert_tables('my_trades_closed_json',result_to_dict)
                
                if net_sum !=0 :
                    
                    # get trade seq
                    result = ([o['trade_seq']   for o in transactions_under_label_main ])
                    
                    for res in result:

                        my_trades_open_sqlite: list = await self.querying_all('my_trades_all_json')
                        my_trades_open: list = my_trades_open_sqlite ['list_data_only']
                        result_to_dict =  ([o for o in my_trades_open if o['trade_seq'] == res])[0]
                        result_to_dict['label'] =  str_mod.parsing_label(result_to_dict['label'])['closed_to_open']

                        where_filter = f"trade_seq"
                        await sqlite_management.deleting_row('my_trades_all_json', 
                                                            "databases/trading.sqlite3",
                                                            where_filter,
                                                            "=",
                                                            res
                                                            )
                        await sqlite_management.insert_tables('my_trades_all_json',result_to_dict)
                    
                    # refreshing data
                    await system_tools.sleep_and_restart(1)
    
    async def closing_transactions(self, 
                                   label_transaction_net,
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions,
                                   ) -> float:
        """ """
                    
        log.critical (f'CLOSING TRANSACTIONS')
        reading_from_database: dict = await self.reading_from_database()
        clean_up_closed_transactions: list = await self.clean_up_closed_transactions(my_trades_open_all)

        my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')

        my_trades_open_all: list = my_trades_open_sqlite['all']
        
        my_trades_open: list = my_trades_open_sqlite ['list_data_only']
        
        open_orders_sqlite: list = await self.querying_all('orders_all_json')

        # open orders data
        open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']

        open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]

        # Creating an instance of the open order  class
        open_order_mgt = open_orders_management.MyOrders(open_orders_open_from_db)        
        log.error (f'clean_up_closed_transactions {clean_up_closed_transactions}')

        label_transaction_main = str_mod.remove_redundant_elements ([(str_mod.parsing_label(o))['main'] for o in label_transaction_net])
        log.warning (f'label_transaction_main {label_transaction_main}')

        for label in label_transaction_main:
            log.debug (f'label {label}')

            my_trades_open_strategy =  [o for o in my_trades_open if str_mod.parsing_label(o["label"])['main']  == label]
            #log.debug (my_trades_open_strategy)
            get_prices_in_label_transaction_main =  [o['price'] for o in my_trades_open_strategy]
            max_price =  0 if get_prices_in_label_transaction_main == [] else max(get_prices_in_label_transaction_main)
            min_price =  0 if get_prices_in_label_transaction_main == [] else min(get_prices_in_label_transaction_main)

            if 'Short' in label or 'hedging' in label:
                transaction =  [o for o in my_trades_open_strategy if o["price"] == max_price]
            if 'Long' in label:
                transaction =  [o for o in my_trades_open_strategy if o["price"] == min_price]
                        
            label = [
                        str_mod.parsing_label(o["label"])['transaction_net']
                        for o in transaction
                    ][0]

            log.critical(f" {label} max_price {max_price} min_price {min_price} pct diff {abs(min_price-max_price)/min_price}")

            grids=   grid.GridPerpetual(my_trades_open, open_orders_sqlite) 
            
            check_orders_with_the_same_labels= await grids.open_orders_as_per_main_label(label)
            
            if check_orders_with_the_same_labels ['len_result'] > 1:
                log.critical(f" check_orders_with_the_same_labels {check_orders_with_the_same_labels}")
                cancelled_id= [o for o in open_orders_open_from_db if o['label'] == label ]
                log.warning(f" cancelled_id {cancelled_id}")

                for id in cancelled_id:
                    log.warning(f" id {id}")
                    await self.cancel_by_order_id(id)

            # result example: 'hedgingSpot'/'supplyDemandShort60'
            label_main = str_mod.parsing_label(label)['main']
            log.warning(f" label {label} label_main {label_main}")

            open_order_label = open_order_mgt.open_orders_api_basedOn_label(label)

            open_order_label_short = [o for o in open_order_label if o["direction"] == "sell"]
            
            open_order_label_long = [o for o in open_order_label if o["direction"] == "buy"]
            
            # get startegy details
            strategy_attr = [o for o in strategies if o["strategy"] == label_main][0]                        
            
            my_trades_open_sqlite_individual_strategy: list = await self.my_trades_open_sqlite_detailing(my_trades_open_all, label, 'individual')
            my_trades_open_sqlite_main_strategy: list = await self.my_trades_open_sqlite_detailing(my_trades_open_all, label, 'main')

            sum_my_trades_open_sqlite_all_strategy: list = await self.sum_my_trades_open_sqlite(my_trades_open_all, label)
            size_is_consistent: bool = await self.is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions)
            #: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)
            
            if size_is_consistent:# and open_order_is_consistent:
                
                open_trade_strategy = str_mod.parsing_sqlite_json_output([o['data'] for o in my_trades_open_sqlite_main_strategy])
                open_trade_strategy_label = str_mod.parsing_sqlite_json_output([o['data'] for o in my_trades_open_sqlite_individual_strategy])

                instrument: list= [o["instrument_name"] for o in open_trade_strategy_label][0]
                
                ticker: list =  self.reading_from_db("ticker", instrument)

                if ticker !=[]:
                        
                    # index price
                    index_price: float = ticker[0]["index_price"]
                    
                    # get instrument_attributes
                    instrument_attributes_all: list =  self.reading_from_db("instruments", self.currency)[0]['result']
                    instrument_attributes: list =  [o for o in instrument_attributes_all if o['instrument_name'] == instrument ]
                    tick_size: float = instrument_attributes[0]["tick_size"]
                    taker_commission: float = instrument_attributes[0]["taker_commission"]
                    min_trade_amount: float = instrument_attributes[0]["min_trade_amount"]
                    contract_size: float = instrument_attributes[0]["contract_size"]
                    log.error (f'tick_size A {tick_size} taker_commission {taker_commission} min_trade_amount {min_trade_amount} contract_size {contract_size}')

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
                    #log.warning(f" check_orders_with_the_same_labels {check_orders_with_the_same_labels}")
                    
                    log.debug (f'open_trade_strategy_label   {open_trade_strategy_label}')
                    
                    len_open_order_label_long = (0 if open_order_label_long == []  
                                                    else len(open_order_label_long))
                                          
                    if "hedgingSpot" in strategy_attr["strategy"] :
                        
                        # closing order
                        closed_order= hedging_spot.is_send_exit_order_allowed (notional,
                                                                                best_bid_prc,
                                                                                size_from_positions, 
                                                                                len_open_order_label_long,
                                                                                open_trade_strategy_label,
                                                                                strategy_attr
                                                                                )                        
                        await self.if_order_is_true(closed_order)
                
                    if "marketMaker" in strategy_attr["strategy"]:
                        
                        market_maker= MM.MarketMaker(label)
                        
                        send_order: dict = await market_maker.is_send_exit_order_allowed (best_ask_prc,
                                                                                          best_bid_prc,
                                                                                          open_trade_strategy_label
                                                                                          )    
                        log.critical (f' send_order {send_order}')   
                        await self.if_order_is_true(send_order, instrument)   
                        
            else:
                log.critical (f' size_is_consistent {size_is_consistent} ')
                #await telegram_bot_sendtext('size or open order is inconsistent', "general_error")
                await system_tools.sleep_and_restart (5)
            
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
            log.critical (f'OPENING TRANSACTIONS')
            reading_from_database: dict = await self.reading_from_database()
        
            my_trades_open_sqlite: dict = await self.querying_all('my_trades_all_json')
            my_trades_open_all: list = my_trades_open_sqlite['all']
            #log.error (my_trades_open_all)
            
            my_trades_open: list = my_trades_open_sqlite ['list_data_only']
            
            open_orders_sqlite: list = await self.querying_all('orders_all_json')
            open_orders_open_from_db: list= open_orders_sqlite ['list_data_only']
            
            ticker: list =  self.reading_from_db("ticker", instrument)
            grids=  grid.GridPerpetual(my_trades_open, open_orders_sqlite) 
            
            open_order_mgt = open_orders_management.MyOrders(open_orders_open_from_db)
            
            open_orders_from_sub_account_get = reading_from_database["open_orders_from_sub_account"]
        
            if ticker !=[]:

                # get bid and ask price
                best_bid_prc: float = ticker[0]["best_bid_price"]
                best_ask_prc: float = ticker[0]["best_ask_price"]
                
                # index price
                index_price: float = ticker[0]["index_price"]
        
                # obtain spot equity
                equity: float = portfolio[0]["equity"]
        
                # compute notional value
                notional: float = await self.compute_notional_value(index_price, equity)             

                # execute each strategy
                for strategy_attr in strategies:
                    strategy_label = strategy_attr["strategy"] 
                    
                    log.critical (f' {strategy_label}')
                    
                    check_orders_with_the_same_labels= await grids.open_orders_as_per_main_label(strategy_label)
                    
                    if check_orders_with_the_same_labels ['len_result'] > 1:
                        
                        cancelled_id= [o['order_id'] for o in open_orders_open_from_db if strategy_label in o['label']]
                        for id in cancelled_id:
                            await self.cancel_by_order_id(id)
                    
                    net_sum_strategy = await self.get_net_sum_strategy_super_main(my_trades_open_sqlite, strategy_label)
                    net_sum_strategy_main = await self.get_net_sum_strategy_main(my_trades_open_sqlite, strategy_label)
                    log.debug (f'net_sum_strategy   {net_sum_strategy} net_sum_strategy_main   {net_sum_strategy_main}')
                    
                    sum_my_trades_open_sqlite_all_strategy: list = await self.sum_my_trades_open_sqlite(my_trades_open_all, strategy_label)
                    size_is_consistent: bool = await self.is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions)
                    #open_order_is_consistent: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)
                    
                    #if open_order_is_consistent == False:
                    #    await self.resolving_inconsistent_open_orders(open_orders_from_sub_account_get, open_orders_open_from_db)
                    
                    if size_is_consistent:# and open_order_is_consistent:                                                    
                                                                                        
                        if "hedgingSpot" in strategy_attr["strategy"]:

                            current_outstanding_order_len= (check_orders_with_the_same_labels) ['len_result']
                            
                            #basic hedging                                
                            send_order: dict = hedging_spot.is_send_open_order_allowed (notional,
                                                                                    best_ask_prc,
                                                                                    net_sum_strategy_main, 
                                                                                    current_outstanding_order_len,
                                                                                    strategy_attr
                                                                                    )                            
                            await self.if_order_is_true(send_order, instrument)
                            
                        if "marketMaker" in strategy_attr["strategy"]:
                            
                            market_maker= MM.MarketMaker(strategy_label)
                            
                            send_order: dict = await market_maker.is_send_and_cancel_open_order_allowed (notional,
                                                                                                         best_ask_prc,
                                                                                                         best_bid_prc,
                                                                                                         server_time
                                                                                                         )    
                            #log.critical (f' send_order {send_order}')   
                            await self.if_order_is_true(send_order, instrument)   
                            await self.if_cancel_is_true(send_order)   
                                        
                    else:
                        log.critical (f' size_is_consistent {size_is_consistent} ')
                        #await telegram_bot_sendtext('size or open order is inconsistent', "general_error")
                        await system_tools.sleep_and_restart (5)

                    #placed at the end of opening code to ensure db consistency
                    check_cancellation = open_order_mgt.cancel_orders_based_on_time_threshold(server_time, strategy_label, ONE_MINUTE* 30)

                    if check_cancellation !=None:
                        if check_cancellation['open_orders_deltaTime-exceed_threshold'] \
                            and check_cancellation['open_order_id'] !=[]:
                                await self.cancel_by_order_id(check_cancellation['open_order_id'])
                                                
        except Exception as error:
            await raise_error(error)

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

                # ?################################## end of gathering basic data #####################################

                # Creating an instance of the my-Trade class
                my_trades_open_mgt: object = myTrades_management.MyTrades(my_trades_open)

                # fetch strategies attributes
                strategies = entries_exits.strategies
    
                
                #log.error (my_trades_open)
                #log.error ([o["label"] for o in my_trades_open])
                my_trades_open_remove_closed_labels = [] if my_trades_open == [] \
                    else [o for o in my_trades_open if 'closed' not in o["label"]]
                                        
                #log.debug (my_trades_open_remove_closed_labels)
                
                label_transaction_net =  [] if my_trades_open_remove_closed_labels == [] \
                    else str_mod.remove_redundant_elements(
                    [
                        str_mod.parsing_label(o["label"])['transaction_net']
                        for o in my_trades_open_remove_closed_labels
                    ]
                    )
            
                #log.error (label_transaction_net)
                # leverage_and_delta = self.compute_position_leverage_and_delta (notional, my_trades_open)
                # log.warning (leverage_and_delta)           
     
                # closing transactions
                if label_transaction_net != []:
                    await self.closing_transactions( 
                                   label_transaction_net,
                                   portfolio, 
                                   strategies, 
                                   my_trades_open_sqlite, 
                                   my_trades_open_all, 
                                   my_trades_open,
                                   size_from_positions
                                   )
                    
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
                    
                
                clean_up_closed_transactions: list = await self.clean_up_closed_transactions(my_trades_open_all)
                log.error (f'clean_up_closed_transactions 2 {clean_up_closed_transactions}')
                
        except Exception as error:
            await raise_error(error, 30)

async def count_and_delete_ohlc_rows(rows_threshold: int = 100000):
    
    tables= ['ohlc1_eth_perp_json', 'ohlc30_eth_perp_json']                   
    database: str = "databases/trading.sqlite3"
    
    for table in tables:

        count_rows_query=  sqlite_management.querying_arithmetic_operator('tick', 'COUNT', table)
        rows= await sqlite_management.executing_query_with_return(count_rows_query)
        rows= rows[0]['COUNT (tick)']

        if rows >rows_threshold:

            where_filter = f"tick"
            first_tick_query= sqlite_management.querying_arithmetic_operator ('tick', 'MIN', table)
            first_tick_fr_sqlite= await sqlite_management.executing_query_with_return(first_tick_query)
            first_tick= first_tick_fr_sqlite[0]['MIN (tick)']

            await sqlite_management.deleting_row(table, 
                                                database,
                                                where_filter,
                                                "=",
                                                first_tick
                                                )

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
        
        # resupply sub account db
        account_balances_and_transactions_from_exchanges= await syn.get_account_balances_and_transactions_from_exchanges()
        sub_accounts = account_balances_and_transactions_from_exchanges ['sub_account']

        my_path_sub_account = system_tools.provide_path_for_file(
            "sub_accounts", currency
        )
        pickling.replace_data(my_path_sub_account, sub_accounts)
        
        # get deribit server time
        server_time = await syn.current_server_time()

        #log.error (f'sub_accounts {sub_accounts}')
        await syn.running_strategy(server_time)

        # capping sqlite rows
        await count_and_delete_ohlc_rows()
        
    except Exception as error:
        await raise_error(error, 30)

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(main())

    except KeyboardInterrupt:
        system_tools.catch_error_message (KeyboardInterrupt)

    except Exception as error:
        system_tools.catch_error_message (error, 30)
