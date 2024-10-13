# -*- coding: utf-8 -*-

# built ins
import asyncio
from datetime import datetime
import os
import tomli

# installed
from loguru import logger as log

# user defined formula

from configuration.config import main_dotenv
from db_management.sqlite_management import (
    insert_tables,
    deleting_row,
    querying_arithmetic_operator,
    executing_query_with_return,
    executing_query_based_on_currency_or_instrument_and_strategy as get_query)
from strategies.config_strategies import paramaters_to_balancing_transactions
from strategies.basic_strategy import (
    is_label_and_side_consistent,
    check_db_consistencies,
    get_basic_closing_paramaters,
    are_size_and_order_appropriate)
from transaction_management.deribit.transaction_log import (saving_transaction_log,)
from transaction_management.deribit.orders_management import (
    saving_traded_orders,)
from transaction_management.deribit.api_requests import (
    get_currencies,
    get_instruments,
    get_tickers,
    SendApiRequest)
from utilities.system_tools import (
    catch_error_message,
    raise_error_message,
    provide_path_for_file,
    reading_from_db_pickle,
    sleep_and_restart)
from utilities.pickling import replace_data, read_data
from utilities.string_modification import (
    remove_double_brackets_in_list,
    remove_redundant_elements,
    extract_currency_from_text,
    parsing_label,)
from websocket_management.cleaning_up_transactions import (
    reconciling_between_db_and_exchg_data, 
    clean_up_closed_transactions)


def deribit_url_main() -> str:
    return "https://www.deribit.com/api/v2/"


def parse_dotenv(sub_account) -> dict:
    return main_dotenv(sub_account)

async def raise_error(error, idle: int = None) -> None:
    """ """
    await raise_error_message(error, idle)


def get_config(file_name: str) -> list:
    """ """
    config_path = provide_path_for_file (file_name)
    
    try:
        if os.path.exists(config_path):
            with open(config_path, "rb") as handle:
                read= tomli.load(handle)
                return read
    except:
        return []


async def get_private_data(currency: str = None) -> list:
    """
    Provide class object to access private get API
    """

    sub_account = "deribit-147691"
    return SendApiRequest (sub_account, currency)
    #return api_request

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:

    return await telegram_bot_sendtext(bot_message, purpose)
        
async def get_transaction_log(currency: str, start_timestamp: int, count: int= 1000) -> list:
    """ """

    private_data = await get_private_data(currency)

    result_transaction_log: dict = await private_data.get_transaction_log(start_timestamp, count)
    
    result_transaction_log_to_result = result_transaction_log["result"]
    
    #log.info (f"result_transaction_log_to_result {result_transaction_log_to_result}")

    return [] if result_transaction_log_to_result  == []\
        else result_transaction_log_to_result["logs"]
    
def compute_notional_value(index_price: float, 
                           equity: float) -> float:
    """ """
    return index_price * equity


def reading_from_db(end_point, 
                    instrument: str = None, 
                    status: str = None) -> float:
    """ """
    return reading_from_db_pickle(end_point, instrument, status)


async def send_limit_order(params) -> None:
    """ """
    private_data = await get_private_data()

    send_limit_result = await private_data.send_limit_order(params)
    
    return send_limit_result


async def if_order_is_true(order, instrument: str = None) -> None:
    """ """
    # log.debug (order)
    if order["order_allowed"]:

        # get parameter orders
        try:
            params = order["order_parameters"]
        except:
            params = order

        if instrument != None:
            # update param orders with instrument
            params.update({"instrument": instrument})

        label_and_side_consistent = is_label_and_side_consistent(params)

        if  label_and_side_consistent:
            await inserting_additional_params(params)
            send_limit_result = await send_limit_order(params)
            return send_limit_result
            #await asyncio.sleep(10)
        else:
            
            return []
            #await asyncio.sleep(10)


async def get_my_trades_from_exchange(count: int, currency) -> list:
    """ """
    private_data = await get_private_data(currency)
    trades: list = await private_data.get_user_trades_by_currency(count)

    return [] if trades == [] else trades["result"]["trades"]


async def cancel_all () -> None:
    private_data = await get_private_data()

    await private_data.get_cancel_order_all()
    

async def cancel_by_order_id(open_order_id) -> None:
    private_data = await get_private_data()

    result = await private_data.get_cancel_order_byOrderId(open_order_id)
    
    try:
        if (result["error"]["message"])=="not_open_order":
            
            where_filter = f"order_id"
            
            await deleting_row(
                                "orders_all_json",
                                "databases/trading.sqlite3",
                                where_filter,
                                "=",
                                open_order_id,
                            )
            
    except:

        log.critical(f"CANCEL_by_order_id {result} {open_order_id}")

        return result


async def cancel_the_cancellables(cancellable_strategies, filter: str = None) -> None:

    file_toml = "config_strategies.toml"
        
    config_app = get_config(file_toml)

    tradable_config_app = config_app["tradable"]
    
    currencies= [o["spot"] for o in tradable_config_app] [0]
    
    where_filter = f"order_id"
    
    column_list= "label", where_filter
    
    for currency in currencies:
        open_orders_sqlite: list=  await get_query("orders_all_json", 
                                                    currency.upper(), 
                                                    "all",
                                                    "all",
                                                    column_list)

        if open_orders_sqlite != []:

            for strategy in cancellable_strategies:
                
                open_orders_cancellables = [
                    o for o in open_orders_sqlite if strategy in o["label"]
                ]


                if open_orders_cancellables != []:

                    if filter != None and open_orders_cancellables != []:

                        open_orders_cancellables = [
                            o for o in open_orders_cancellables if filter in o["label"]
                        ]

                if open_orders_cancellables != []:

                    open_orders_cancellables_id = [
                        o["order_id"] for o in open_orders_cancellables
                    ]

                    if open_orders_cancellables_id != []:

                        for order_id in open_orders_cancellables_id:

                            await cancel_by_order_id(order_id)

                            log.critical(f" cancel_the_cancellable {order_id}")                           

                            await deleting_row(
                                "orders_all_json",
                                "databases/trading.sqlite3",
                                where_filter,
                                "=",
                                order_id,
                            )


async def if_cancel_is_true(order) -> None:
    """ """
    #log.warning (order)
    if order["cancel_allowed"]:

        # get parameter orders
        await cancel_by_order_id(order["cancel_id"])

async def updated_open_orders_database(open_orders_from_sub_accounts, from_sqlite_open) -> None:
    
    log.error (f"open_orders_from_sub_accounts {open_orders_from_sub_accounts}")

    open_orders_from_sub_accounts_order_id= [o["order_id"] for o in open_orders_from_sub_accounts]
    log.warning (f"open_orders_from_sub_accounts_order_id {open_orders_from_sub_accounts_order_id}")
        
    order_id_from_current_db= [o["order_id"] for o in from_sqlite_open]
    log.error (f"order_id_from_current_db {order_id_from_current_db}")
    
    if order_id_from_current_db !=[]:
        
        if open_orders_from_sub_accounts==[]:
            for order in order_id_from_current_db:
                await deleting_row(
            "orders_all_json",
            "databases/trading.sqlite3",
            "order_id",
            "=",
            order,
        )
                
        else:
            
            for order_id in order_id_from_current_db:
                
                if order_id not in open_orders_from_sub_accounts_order_id:
                    log.critical (f"open_orders_from_sub_accounts_order_id {open_orders_from_sub_accounts_order_id}")
                    await deleting_row(
            "orders_all_json",
            "databases/trading.sqlite3",
            "order_id",
            "=",
            order_id,
        )

            for order in open_orders_from_sub_accounts:
                
                label=order["label"]
                instrument_name=order["instrument_name"]
                    
                if order["order_id"] not in order_id_from_current_db:
                    await insert_tables("orders_all_json", order)

                if label=="":
                    await labelling_the_unlabelled_and_resend_it(order, instrument_name)

    else:
        if open_orders_from_sub_accounts !=[]:
            for order in open_orders_from_sub_accounts:
                await insert_tables("orders_all_json", order)

def reading_from_pkl_data(end_point, currency, status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, currency, status)
    data = read_data(path)

    return data


def get_instruments_kind(currency: str, settlement_periods, kind: str= "all") -> list:
    """_summary_

    Args:
        currency (str): _description_
        kind (str): "future_combo",  "future"
        Instance:  [
                    {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1,'counter_currency': 'USD', 
                    'settlement_period': 'month', 'settlement_currency': 'ETH', 'creation_timestamp': 1719564006000, 
                    'instrument_id': 342036, 'base_currency': 'ETH', 'tick_size': 0.05, 'contract_size': 1, 'is_active': True, 
                    'expiration_timestamp': 1725004800000, 'instrument_type': 'reversed', 'taker_commission': 0.0, 
                    'maker_commission': 0.0, 'instrument_name': 'ETH-FS-27SEP24_30AUG24', 'kind': 'future_combo', 
                    'rfq': False, 'price_index': 'eth_usd'}, ]
     Returns:
        list: _description_
        
        
    """ 
    
    my_path_instruments = provide_path_for_file(
        "instruments", currency
    )

    instruments_raw = read_data(my_path_instruments)
    instruments = instruments_raw[0]["result"]
    non_spot_instruments=  [
        o for o in instruments if o["kind"] != "spot"]
    instruments_kind= non_spot_instruments if kind =="all" else  [
        o for o in instruments if o["kind"] == kind]
    
    return  [o for o in instruments_kind if o["settlement_period"] in settlement_periods]


async def get_futures_for_active_currencies (active_currencies,
                                             settlement_periods) -> list:
    """_summary_

    Returns:
        list: _description_
    """
    
    instruments_holder_place= []
    for currency in active_currencies:

        future_instruments= get_instruments_kind (currency,
                                                  settlement_periods,
                                                  "future" )

        future_combo_instruments= get_instruments_kind (currency,
                                                  settlement_periods,
                                                  "future_combo" )
        
        active_combo_perp = [o for o in future_combo_instruments if "_PERP" in o["instrument_name"]]
        
        combined_instruments = future_instruments + active_combo_perp
        instruments_holder_place.append(combined_instruments)    
    
    #removing inner list 
    # typical result: [['BTC-30AUG24', 'BTC-6SEP24', 'BTC-27SEP24', 'BTC-27DEC24', 
    # 'BTC-28MAR25', 'BTC-27JUN25', 'BTC-PERPETUAL'], ['ETH-30AUG24', 'ETH-6SEP24', 
    # 'ETH-27SEP24', 'ETH-27DEC24', 'ETH-28MAR25', 'ETH-27JUN25', 'ETH-PERPETUAL']]
    
    instruments_holder_plc= []
    for instr in instruments_holder_place:
        instruments_holder_plc.append(instr)

    return remove_double_brackets_in_list(instruments_holder_plc)
    
    
async def get_futures_instruments (active_currencies, 
                                   settlement_periods) -> list:
    
    active_futures=  await get_futures_for_active_currencies(active_currencies,
                                                             settlement_periods)
    
    active_combo = [o for o in active_futures if "future_combo" in o["kind"]]
          
    min_expiration_timestamp = min([o["expiration_timestamp"] for o in active_futures]) 
    
    return dict(instruments_name = [o["instrument_name"] for o in (active_futures)],
                min_expiration_timestamp = min_expiration_timestamp,
                active_futures = [o for o in active_futures if "future" in o["kind"]],
                active_combo_perp =  active_combo,
                instruments_name_with_min_expiration_timestamp = [o["instrument_name"] for o in active_futures \
                    if o["expiration_timestamp"] == min_expiration_timestamp][0]
                )
    
def currency_inline_with_database_address (currency: str, database_address: str) -> bool:
    return currency.lower()  in str(database_address)


async def get_and_save_currencies()->None:
    
    try:

        get_currencies_all = await get_currencies()
        
        currencies = [o["currency"] for o in get_currencies_all["result"]]
        
        for currency in currencies:

            instruments = await get_instruments(currency)

            my_path_instruments = provide_path_for_file("instruments", currency)

            replace_data(my_path_instruments, instruments)

        my_path_cur = provide_path_for_file("currencies")

        replace_data(my_path_cur, currencies)
        # catch_error('update currencies and instruments')

    except Exception as error:
        
        await cancel_all ()
        
        catch_error_message(
        error, 10, "app"
        )

async def synchronising_my_trade_db_vs_exchange (currency: str,
                                                order_db_table: str, 
                                                trade_db_table: str, 
                                                archive_db_table: str,
                                                transaction_log_trading) -> None:
    """
    """
    log.warning("Synchronising my_trade_db vs exchange")
        
    column_list= "instrument_name", "position", "timestamp"
    
    from_transaction_log = await get_query (transaction_log_trading, 
                                                currency, 
                                                "all", 
                                                "all", 
                                                column_list)                                       

    instruments = remove_redundant_elements([o["instrument_name"] for o in from_transaction_log])
    
    #log.error (f"from_transaction_log {from_transaction_log}")
    
    for instrument_name in instruments:
        
        last_time_stamp_log = max([o["timestamp"] for o in from_transaction_log if o["instrument_name"] == instrument_name])
        current_position_log = [o["position"] for o in from_transaction_log if o["timestamp"] == last_time_stamp_log][0]
        
        column_list= "instrument_name",  "timestamp", "amount"
       
        from_sqlite_open= await get_query (trade_db_table, 
                                            instrument_name, 
                                            "all", 
                                            "all", 
                                            column_list)                                       
                
        current_instrument_trading_position =  0 if from_sqlite_open == [] else sum([o["amount"] for o in from_sqlite_open  ])
        
        log.error (f"{instrument_name} current_instrument_trading_position {current_instrument_trading_position} current_position_log {current_position_log}")
        
        #if current_instrument_trading_position != current_position_log:
        
async def update_trades_from_exchange (currency: str,
                                    archive_db_table,
                                    order_table,
                                    qty_trades: int =  100) -> None:
    """
    """
    log.warning ("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")     
    trades_from_exchange = await get_my_trades_from_exchange (qty_trades, currency)
    log.warning ("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")     
    
    if trades_from_exchange:
        log.warning ("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")     
        
        trades_from_exchange_without_futures_combo = [ o for o in trades_from_exchange if f"{currency}-FS" not in o["instrument_name"]]
        log.warning ("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")     

        if trades_from_exchange_without_futures_combo:
            
            for trade in trades_from_exchange_without_futures_combo:
                log.info ("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")     
                await saving_traded_orders (trade, 
                                            archive_db_table,
                                            order_table)

    
async def on_restart(currencies_default: str,
                     order_table: str) -> None:
    """
    """

    log.warning("Cancelling all orders")
    await cancel_all()
    
    # refresh databases
    await get_and_save_currencies()                
    log.warning("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    
    for currency in currencies_default:
        
        archive_db_table= f"my_trades_all_{currency.lower()}_json"
        
        transaction_log_trading= f"transaction_log_{currency.lower()}_json"
        
        await resupply_transaction_log(currency, 
                                       transaction_log_trading,
                                       archive_db_table)
        
        #await update_trades_from_exchange (currency,
        #                                   archive_db_table,
        #                                   order_table,
        #                                   100)
        #await check_db_consistencies_and_clean_up_imbalances(currency)                           

    log.warning("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    
async def check_db_consistencies_and_clean_up_imbalances(currency: str, cancellable_strategies, sub_accounts: list =[]) -> None:
    
    if sub_accounts== [] or sub_accounts is None:
        sub_accounts = reading_from_pkl_data("sub_accounts",currency)

    sub_accounts=sub_accounts[0]

    positions= sub_accounts["positions"]

    active_instruments_from_positions = [o["instrument_name"] for o in positions]
                    
    column_list_order: str="order_id", "label","amount"
    
    column_list_trade: str= column_list_order, "instrument_name","price", "timestamp","trade_id","side"

    my_trades_currency: list= await get_query("my_trades_all_json", currency, "all", "all", column_list_trade)

    all_outstanding_instruments = remove_redundant_elements([o["instrument_name"] for o in my_trades_currency])
                      
    open_orders_from_sub_accounts= sub_accounts["open_orders"]
    
    positions_from_sub_accounts= sub_accounts["positions"]
    
    for instrument_name in all_outstanding_instruments:
        log.warning (f"instrument_name {instrument_name} {instrument_name in active_instruments_from_positions}")      
        
        my_trades_instrument: list= [o for o in my_trades_currency if instrument_name in o["instrument_name"]]
        
        currency: str = extract_currency_from_text(instrument_name)
            
        order_from_sqlite_open= await get_query("orders_all_json", 
                                                    currency, 
                                                    "all", 
                                                    "all", 
                                                    column_list_order)        
                         
        db_consistencies= check_db_consistencies (instrument_name, 
                                                  my_trades_instrument, 
                                                  positions_from_sub_accounts,
                                                  order_from_sqlite_open,
                                                  open_orders_from_sub_accounts)

        log.debug (f"db_consistencies {db_consistencies}")
        order_is_consistent= db_consistencies["order_is_consistent"]
        
        size_is_consistent= db_consistencies["trade_size_is_consistent"]
            
        if not db_consistencies["no_non_label_from_from_sqlite_open"]:
            await updated_open_orders_database(open_orders_from_sub_accounts,order_from_sqlite_open)
            
        if not order_is_consistent:
            log.critical (f"BALANCING-ORDERS-START")
            #await resupply_sub_accountdb(currency)
            await updated_open_orders_database(open_orders_from_sub_accounts,order_from_sqlite_open)
            log.critical (f"BALANCING-ORDERS-DONE")
            await cancel_the_cancellables(cancellable_strategies)
                                                        
        if not size_is_consistent:
            log.critical (f"BALANCING TRADE-START")
            
            await cancel_the_cancellables("open")
                
            if "PERPETUAL" not in instrument_name:
                time_stamp= [o["timestamp"] for o in my_trades_instrument]
                
                if time_stamp !=[]:
                    
                    last_time_stamp_sqlite= max(time_stamp)
                    
                    transaction_log_from_sqlite_open= await get_query("transaction_log_json", 
                                                    instrument_name, 
                                                    "all", 
                                                    "all", 
                                                    "standard")
                    log.critical (f"transaction_log_from_sqlite_open {transaction_log_from_sqlite_open}")
                    delivered_transaction= [o for o in transaction_log_from_sqlite_open if "delivery" in o["type"] ]
                    delivery_timestamp= [o["timestamp"] for o in delivered_transaction ]
                    delivery_timestamp= [] if delivery_timestamp==[] else max(delivery_timestamp)
                    
                    #log.warning (f"delivery_timestamp {delivery_timestamp} last_time_stamp_sqlite {last_time_stamp_sqlite} last_time_stamp_sqlite < delivery_timestamp {last_time_stamp_sqlite < delivery_timestamp}")
                    
                    if delivery_timestamp !=[] and last_time_stamp_sqlite < delivery_timestamp:
                            
                        transactions_from_other_side= [ o for o in my_trades_currency \
                            if instrument_name not in o["instrument_name"]]
                                                
                        column_data: str="trade_id","timestamp","amount","price","label","amount","order_id"
                        
                        my_trades_instrument_data: list= await get_query("my_trades_all_json", instrument_name, "all", "all", column_data)
                            
                        for transaction in my_trades_instrument_data:
                            
                            label_int= parsing_label(transaction["label"])["int"]
                            #log.error (f"label_int {label_int}")
                            
                            transactions_from_other_side= [ o for o in my_trades_currency \
                            if instrument_name not in o["instrument_name"] and label_int in o["label"] ]
                            
                            orders_from_other_side= [ o["amount"] for o in order_from_sqlite_open \
                            if instrument_name not in o["instrument_name"] and label_int in o["label"] ]
                            
                            orders_from_other_side= 0 if orders_from_other_side == [] else sum(orders_from_other_side)
                            
                            sum_transactions_from_other_side= sum([o["amount"] for o in transactions_from_other_side])
                            
                            for transaction in transactions_from_other_side:
                                
                                log.debug (f"transaction {transaction}")                
                                
                                basic_closing_paramaters= get_basic_closing_paramaters (transaction)  
                                basic_closing_paramaters.update({"instrument":transaction["instrument_name"]})
                                tickers= await get_tickers (basic_closing_paramaters["instrument"])
                                
                                if basic_closing_paramaters["side"]=="sell":
                                    entry_price=tickers["best_ask_price"]

                                if basic_closing_paramaters["side"]=="buy":
                                    entry_price=tickers["best_bid_price"]
                                    
                                basic_closing_paramaters.update({"entry_price":entry_price})
                                basic_closing_paramaters.update({"size":abs(basic_closing_paramaters["size"])})
                                
                                log.error (f"basic_closing_paramaters {basic_closing_paramaters}")
                                log.error (f"sum_transactions_from_other_side {sum_transactions_from_other_side}")
                                log.error (f"orders_from_other_side {orders_from_other_side}")
                                log.error (basic_closing_paramaters["size"])
                                size_and_order_appropriate = are_size_and_order_appropriate("reduce_position",
                                                                                            sum_transactions_from_other_side,
                                                                                            orders_from_other_side,
                                                                                            basic_closing_paramaters["size"])
                                
                                
                                log.error (f"size_and_order_appropriate {size_and_order_appropriate}")
                                if False and  size_and_order_appropriate:
                                    await send_limit_order(basic_closing_paramaters)  
                                
                            #log.error (f"my_trades_instrument_data {transaction}")
                        
                            
                            #await clean_up_closed_futures_because_has_delivered(instrument_name, transaction, delivered_transaction)
                        
            
            balancing_params=paramaters_to_balancing_transactions()
            
            max_transactions_downloaded_from_exchange=balancing_params["max_transactions_downloaded_from_exchange"]
            
            trades_from_exchange = await get_my_trades_from_exchange(max_transactions_downloaded_from_exchange, currency)
            
            #log.debug (f"trades_from_exchange {trades_from_exchange}")
            
            trades_from_exchange_without_futures_combo= [ o for o in trades_from_exchange if f"{currency}-FS" not in o["instrument_name"]]
            
            #if "ETH" in instrument_name:
            #    log.debug (f"trades_from_exchange_without_futures_combo {trades_from_exchange_without_futures_combo}")
            
            await reconciling_between_db_and_exchg_data(instrument_name,
                                                        trades_from_exchange_without_futures_combo,
                                                        positions_from_sub_accounts,
                                                        order_from_sqlite_open,
                                                        open_orders_from_sub_accounts)
            
            log.warning (f"CLEAN UP CLOSED TRANSACTIONS-START")
            await clean_up_closed_transactions(instrument_name)
            log.critical (f"BALANCING-DONE")



async def resupply_sub_accountdb(currency) -> None:

    # resupply sub account db
    #log.info(f"resupply {currency.upper()} sub account db-START")
    private_data = await get_private_data (currency)
    sub_accounts = await private_data.get_subaccounts()
    log.info(f"sub_accounts {sub_accounts}")

    my_path_sub_account = provide_path_for_file("sub_accounts", currency)
    replace_data(my_path_sub_account, sub_accounts)
 
        
async def comparing_last_trade_id_in_transaction_log_vs_my_trades_all(trade_db_table: str,
                                                                      transaction_log_trading: str,) -> bool:
    """
    
    """
    
    where_filter= "timestamp"
    
    last_tick_from_transaction_log_query= querying_arithmetic_operator(where_filter, "MAX", transaction_log_trading)
    last_tick_from_my_trades_query= querying_arithmetic_operator(where_filter, "MAX", trade_db_table)
    
    last_tick_from_transaction_log_result = await executing_query_with_return(last_tick_from_transaction_log_query)
    last_tick_from_my_trades_query_result = await executing_query_with_return(last_tick_from_my_trades_query)

    last_tick_from_transaction_log = last_tick_from_transaction_log_result [0]["MAX (timestamp)"] 
    last_tick_from_my_trades = last_tick_from_my_trades_query_result [0]["MAX (timestamp)"] 

    return {
        "last_tick_is_eqv": last_tick_from_transaction_log == last_tick_from_my_trades,
        "last_tick_from_transaction_log": last_tick_from_transaction_log,
        "last_tick_from_my_trades": last_tick_from_my_trades,
    }


        
def first_tick_fr_sqlite_if_database_still_empty (max_closed_transactions_downloaded_from_sqlite: int) -> int:
    """
    
    """
    
    from configuration.label_numbering import get_now_unix_time
    
    server_time = get_now_unix_time()  
    
    some_day_ago = 3600000 * max_closed_transactions_downloaded_from_sqlite
    
    delta_some_day_ago = server_time - some_day_ago
    
    return delta_some_day_ago
                                                    
                      
async def resupply_transaction_log(currency: str,
                                   transaction_log_trading,
                                   archive_db_table: str) -> list:
    """ """

    #log.warning(f"resupply {currency.upper()} TRANSACTION LOG db-START")
                
    where_filter= "timestamp"
    
    first_tick_query= querying_arithmetic_operator(where_filter, "MAX", transaction_log_trading)
    
    first_tick_query_result = await executing_query_with_return(first_tick_query)
        
    balancing_params=paramaters_to_balancing_transactions()

    max_closed_transactions_downloaded_from_sqlite=balancing_params["max_closed_transactions_downloaded_from_sqlite"]   
    
    first_tick_fr_sqlite= first_tick_query_result [0]["MAX (timestamp)"] 
    #log.warning(f"first_tick_fr_sqlite {first_tick_fr_sqlite} {not first_tick_fr_sqlite}")
    
    if not first_tick_fr_sqlite:
                
        first_tick_fr_sqlite = first_tick_fr_sqlite_if_database_still_empty (max_closed_transactions_downloaded_from_sqlite)
    
    #log.debug(f"first_tick_fr_sqlite {first_tick_fr_sqlite}")
    
    transaction_log= await get_transaction_log (currency, 
                                                first_tick_fr_sqlite-1, 
                                                max_closed_transactions_downloaded_from_sqlite)
    #log.warning(f"transaction_log {transaction_log}")
            
    await saving_transaction_log (transaction_log_trading,
                                  archive_db_table,
                                  transaction_log, 
                                  first_tick_fr_sqlite, 
                                  )

    #log.warning(f"resupply {currency.upper()} TRANSACTION LOG db-DONE")
        
   
async def inserting_additional_params(params: dict) -> None:
    """ """

    if "open" in params["label"]:
        await insert_tables("supporting_items_json", params)


def delta_price_pct(last_traded_price: float, market_price: float) -> bool:
    """ """
    delta_price = abs(abs(last_traded_price) - market_price)
    return (
        0
        if (last_traded_price == [] or last_traded_price == 0)
        else delta_price / last_traded_price
    )
async def labelling_the_unlabelled_and_resend_it(order, instrument_name):
    """_summary_
    """
    from transaction_management.deribit.orders_management import labelling_unlabelled_transaction
    
    labelling_order= labelling_unlabelled_transaction (order)
    labelled_order= labelling_order["order"]
    
    order_id= order["order_id"]

    await cancel_by_order_id (order_id)
    
    await if_order_is_true(labelled_order, instrument_name)

    
async def distribute_ticker_result_as_per_data_type(my_path_ticker, data_orders, instrument
) -> None:
    """ """

    try:
        # ticker: list = pickling.read_data(my_path_ticker)

        if data_orders["type"] == "snapshot":
            replace_data(my_path_ticker, data_orders)

            # ticker_fr_snapshot: list = pickling.read_data(my_path_ticker)

        else:
            ticker_change: list = read_data(my_path_ticker)
            if ticker_change != []:
                # log.debug (ticker_change)

                for item in data_orders:
                    ticker_change[0][item] = data_orders[item]
                    replace_data(my_path_ticker, ticker_change)

    except Exception as error:
        await raise_error_message(
            error,
            "WebSocket connection - failed to distribute_incremental_ticker_result_as_per_data_type",
        )

