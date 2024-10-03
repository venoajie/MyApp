#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# built ins
from datetime import datetime, timedelta
import aioschedule as schedule
import asyncio
import json

# installed
import websockets
import orjson
from loguru import logger as log

# user defined formula
from configuration import id_numbering, config
from configuration.label_numbering import get_now_unix_time
from db_management.sqlite_management import (
    querying_table,
    executing_query_with_return,
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    querying_arithmetic_operator,
    insert_tables)
from deribit_get import (
    telegram_bot_sendtext,
    get_currencies,
    get_instruments)
from strategies.basic_strategy import (
    check_if_id_has_used_before,
    is_label_and_side_consistent,)
from strategies.hedging_spot import HedgingSpot  
from strategies.futures_spread import delete_respective_closed_futures_from_trade_db, FutureSpreads
from transaction_management.deribit.orders_management import (
    labelling_unlabelled_transaction,
    OrderManagement,)
from utilities.number_modification import get_closest_value
from utilities.pickling import (
    replace_data,
    read_data,)
from utilities.system_tools import (
    provide_path_for_file,
    raise_error_message,
    catch_error_message,
    sleep_and_restart,)
from utilities.string_modification import (
    remove_double_brackets_in_list,
    remove_redundant_elements,
    extract_currency_from_text,)
from websocket_management.ws_management import (
    cancel_the_cancellables,    
    compute_notional_value, 
    cancel_by_order_id,
    get_config,
    get_my_trades_from_exchange,
    if_cancel_is_true,
    if_order_is_true,
    resupply_sub_accountdb,
    resupply_transaction_log,
    check_db_consistencies_and_clean_up_imbalances,)
from websocket_management.allocating_ohlc import (
    ohlc_result_per_time_frame,
    inserting_open_interest,)
from websocket_management.cleaning_up_transactions import (
    clean_up_closed_transactions,
    remove_duplicated_elements,
    )

def deribit_url_main() -> str:
    return "https://www.deribit.com/api/v2/"

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)

def reading_from_pkl_data(end_point, currency, status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, currency, status)

    data = read_data(path)

    return data


async def update_db_pkl(path, data_orders, currency) -> None:

    my_path_portfolio = provide_path_for_file(path, currency)
    
    if currency_inline_with_database_address(currency,my_path_portfolio):
        replace_data(my_path_portfolio, data_orders)
        
async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:

    return await telegram_bot_sendtext(bot_message, purpose)

def get_settlement_period (strategy_atributes) -> list:
    
    return (remove_redundant_elements(remove_double_brackets_in_list([o["settlement_period"]for o in strategy_atributes])))


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
    
    connection_url: str = deribit_url_main()

    try:

        get_currencies_all = await get_currencies(connection_url)
        
        currencies = [o["currency"] for o in get_currencies_all["result"]]
        
        for currency in currencies:

            instruments = await get_instruments(connection_url, currency)

            my_path_instruments = provide_path_for_file("instruments", currency)

            replace_data(my_path_instruments, instruments)

        my_path_cur = provide_path_for_file("currencies")

        replace_data(my_path_cur, currencies)
        # catch_error('update currencies and instruments')

    except Exception as error:
        catch_error_message(
        error, 10, "app"
        )
        
async def update_user_changes(data_orders, 
                              currency, 
                              order_db_table,
                              trade_db_table, 
                              archive_db_table,
                              cancellable_strategies) -> None:
    
    log.warning (f"update_user_changes-START")

    positions = data_orders["positions"]
    trades = data_orders["trades"]
    orders = data_orders["orders"]
    
    instrument_name = data_orders["instrument_name"]

    log.info (f"{instrument_name} {data_orders}")
        
    if orders:
        
        order_management= OrderManagement(order_db_table, 
                                          trade_db_table, 
                                          archive_db_table)
        
        if trades:
            await order_management.saving_traded_orders (trades)
            
        else:
            for order in orders:
                
                label= order["label"]
                
                order_id= order["order_id"]

                order_state= order["order_state"]
                
                label_and_side_consistent= is_label_and_side_consistent(order)
                
                log.critical (f' ORDERS label_and_side_consistent {label_and_side_consistent} everything_NOT_consistent {not label_and_side_consistent}')
                
                if label_and_side_consistent and label:
                    
                    await order_management.saving_orders (order_db_table,
                                                          order,
                                                          order_state)
                    
                # check if transaction has label. Provide one if not any
                if  not label_and_side_consistent:
                
                    await insert_tables(order_db_table, order)

                    await cancel_by_order_id (order_id)                    
                
                    await telegram_bot_sendtext('size or open order is inconsistent', "general_error")

                if not label:
                    
                    new_order = labelling_unlabelled_transaction(label)
                
                    label_has_exist_before= await check_if_id_has_used_before (instrument_name,
                                                                               "order_id",
                                                                               order_id,)
                    await insert_tables(order_db_table, order)
                    
                    await cancel_by_order_id (order_id)
                    
                    if not label_has_exist_before:
                        await if_order_is_true(new_order, instrument_name)
                    
    #log.debug (f"positions {positions}")
    await update_db_pkl("positions", data_orders, currency)
        
    await remove_duplicated_elements()
    log.info(f"update_user_changes-END")



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

    instruments = [o["instrument_name"] for o in from_transaction_log]
    
    log.error (f"from_transaction_log {from_transaction_log}")
    
    for instrument_name in instruments:
        
        last_time_stamp_log = max([o["timestamp"] for o in from_transaction_log if o["instrument_name"] == instrument_name])
        current_position_log = [o["position"] for o in from_transaction_log if o["timestamp"] == last_time_stamp_log][0]
        
        from_sqlite_open= await get_query (trade_db_table, 
                                            instrument_name, 
                                            "all", 
                                            "all", 
                                            column_list)                                       
                
        current_instrument_trading_position =  0 if from_sqlite_open == [] else sum([o["amount"] for o in from_sqlite_open  ])
        
        log.error (f"current_instrument_trading_position {current_instrument_trading_position} current_position_log {current_position_log}")
        
        if current_instrument_trading_position != current_position_log:
            
            trades_from_exchange = await get_my_trades_from_exchange (100, currency)
            
            if trades_from_exchange:
                
                trades_from_exchange_without_futures_combo = [ o for o in trades_from_exchange if f"{currency}-FS" not in o["instrument_name"]]

                if trades_from_exchange_without_futures_combo:
                    
                        order_management= OrderManagement(order_db_table, 
                                                    trade_db_table, 
                                                    archive_db_table)
                        
                        selected_trades_from_exchange = [o for o in trades_from_exchange_without_futures_combo
                                                        if o["timestamp"] >= last_time_stamp_log]
                        
                        await order_management.saving_traded_orders (selected_trades_from_exchange)
        
    
async def on_restart(currencies_default: str,
                     cancellable_strategies: list,
                     order_db_table: str, 
                     trade_db_table: str,) -> None:
    """
    """

    log.warning("Cancelling selected orders")
    await cancel_the_cancellables(cancellable_strategies)
    
    # refresh databases
    await get_and_save_currencies()                
    
    for currency in currencies_default:
        
        archive_db_table= f"my_trades_all_{currency.lower()}_json"
        
        transaction_log_trading= f"transaction_log_{currency.lower()}_json"
        
        await resupply_transaction_log(currency, 
                                       transaction_log_trading,
                                       archive_db_table)
        
        await resupply_sub_accountdb(currency)
        
        await synchronising_my_trade_db_vs_exchange (currency,
                                                    order_db_table, 
                                                    trade_db_table,
                                                    archive_db_table,
                                                    transaction_log_trading)
        #await check_db_consistencies_and_clean_up_imbalances(currency)                           

class StreamAccountData:

    """

    +----------------------------------------------------------------------------------------------+
    +----------------------------------------------------------------------------------------------+

    """

    def __init__(self, client_id: str, client_secret: str, live=True) -> None:
        # Async Event Loop
        self.loop = asyncio.get_event_loop()

        if not live:
            self.ws_connection_url: str = "wss://test.deribit.com/ws/api/v2"
        elif live:
            self.ws_connection_url: str = "wss://www.deribit.com/ws/api/v2"
        else:
            raise Exception("live must be a bool, True=real, False=paper")

        # Instance Variables
        self.connection_url: str = (
            deribit_url_main()
            if "test" not in self.ws_connection_url
            else "https://test.deribit.com/api/v2/"
        )
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.websocket_client: websockets.WebSocketClientProtocol = None
        self.refresh_token: str = None
        self.refresh_token_expiry_time: int = None
    
        # Start Primary Coroutine
        self.loop.run_until_complete(self.ws_manager())

    async def ws_manager(self) -> None:
        
        async with websockets.connect(
            self.ws_connection_url,
            ping_interval=None,
            compression=None,
            close_timeout=60,
        ) as self.websocket_client:
              
            file_toml = "config_strategies.toml"
                
            config_app = get_config(file_toml)

            tradable_config_app = config_app["tradable"]
            
            currencies= [o["spot"] for o in tradable_config_app] [0]
            
            strategy_atributes = config_app["strategies"]
                                    
            active_strategies =   [o["strategy_label"] for o in strategy_atributes if o["is_active"]==True]
            
            cancellable_strategies =   [o["strategy_label"] for o in strategy_atributes if o["cancellable"]==True]
            
            trade_db_table= "my_trades_all_json"
            
            order_db_table= "orders_all_json"                
             
            # Establish restart procedure
            await on_restart(currencies,
                             cancellable_strategies,
                             order_db_table, 
                             trade_db_table,)
                            
            while True:
                
                # Authenticate WebSocket Connection
                await self.ws_auth()
                # Establish Heartbeat
                await self.establish_heartbeat()

                # Start Authentication Refresh Task
                self.loop.create_task(self.ws_refresh_auth())
                
                settlement_periods= get_settlement_period (strategy_atributes)
                                
                futures_instruments=await get_futures_instruments(currencies,
                                                                  settlement_periods)  
                
                active_futures = futures_instruments["active_futures"]   

                active_combo_perp = futures_instruments["active_combo_perp"]  

                instruments_name = futures_instruments["instruments_name"]   
                
                min_expiration_timestamp = futures_instruments["min_expiration_timestamp"]    
                
                resolution = 1                
                                            
                for instrument in instruments_name:
                    
                    await clean_up_closed_transactions (instrument, trade_db_table)

                    currency = extract_currency_from_text(instrument).upper()   
                                    
                    self.loop.create_task(
                        self.ws_operation(
                            operation="subscribe",
                            ws_channel=f"incremental_ticker.{instrument}",))
                                               
                    if "PERPETUAL" in instrument:
                        

                        self.loop.create_task(
                            self.ws_operation(
                                operation="subscribe",
                                ws_channel=f"chart.trades.{instrument}.1",
                            )
                        )
                        
                self.loop.create_task(
                    self.ws_operation(
                        operation="subscribe", ws_channel=f"user.portfolio.{currency}"
                    )
                )

                self.loop.create_task(
                    self.ws_operation(
                        operation="subscribe",
                        ws_channel=f"user.changes.any.{currency.upper()}.raw",
                    )
                )                        
                
                while self.websocket_client.open:
                    # Receive WebSocket messages
                    message: bytes = await self.websocket_client.recv()
                    message: dict = orjson.loads(message)
                    message_channel: str = None
                    
                    if "id" in list(message):
                        log.warning (message)
                        if message["id"] == 9929:
                            
                            if self.refresh_token is None:

                                log.info ("Successfully authenticated WebSocket Connection")

                            else:
                                log.info ("Successfully refreshed the authentication of the WebSocket Connection")

                            self.refresh_token = message["result"]["refresh_token"]

                            # Refresh Authentication well before the required datetime
                            if message["testnet"]:
                                expires_in: int = 300
                            else:
                                expires_in: int = message["result"]["expires_in"] - 240

                            self.refresh_token_expiry_time = datetime.utcnow() + timedelta(
                                seconds=expires_in
                            )

                        elif message["id"] == 8212:
                            # Avoid logging Heartbeat messages
                            continue

                    elif "method" in list(message):

                        # Respond to Heartbeat Message
                        if message["method"] == "heartbeat":
                            await self.heartbeat_response()

                    if "params" in list(message):
                        if message["method"] != "heartbeat":
                            message_channel = message["params"]["channel"]
                            
                            log.info (message_channel)

                            data_orders: list = message["params"]["data"]       
                            
                            currency: str = extract_currency_from_text(message_channel)
                            
                            currency_lower=currency
                            
                            currency_upper=currency.upper()
                            
                            archive_db_table= f"my_trades_all_{currency_lower}_json"
                            
                            transaction_log_trading= f"transaction_log_{currency_lower}_json"

                            if message_channel == f"user.portfolio.{currency.lower()}":
                                # also always performed at restart                                
                                await update_db_pkl("portfolio", data_orders, currency)
                                
                                await resupply_sub_accountdb(currency)    

                            if (message_channel== f"user.changes.any.{currency.upper()}.raw"):
                                log.debug (f"changes {data_orders}")
                                
                                await update_user_changes(data_orders, 
                                                          currency, 
                                                          order_db_table,
                                                          trade_db_table, 
                                                          archive_db_table,
                                                          cancellable_strategies)
                                
                                await resupply_transaction_log(currency, 
                                                               transaction_log_trading,
                                                               archive_db_table)
                                
                                await resupply_sub_accountdb(currency)
                                
                                await synchronising_my_trade_db_vs_exchange (currency,
                                                                             order_db_table, 
                                                                             trade_db_table,
                                                                             archive_db_table,
                                                                             transaction_log_trading)
                                #await check_db_consistencies_and_clean_up_imbalances(currency,
                                #                                                     cancellable_strategies)                           
                            
                            
                            TABLE_OHLC1: str = f"ohlc{resolution}_{currency_lower}_perp_json"
                            WHERE_FILTER_TICK: str = "tick"
                            DATABASE: str = "databases/trading.sqlite3"
                            
                            if "chart.trades" in message_channel:
                                instrument_ticker = ((message_channel)[13:]).partition('.')[0] 
                                                                
                                await ohlc_result_per_time_frame(instrument_ticker,
                                                                 resolution,
                                                                data_orders,
                                                                TABLE_OHLC1,
                                                                WHERE_FILTER_TICK,
                                                                )
                                
                            instrument_ticker = (message_channel)[19:]                  
                            
                            if (
                                message_channel
                                == f"incremental_ticker.{instrument_ticker}"):
                                
                                my_path_ticker = provide_path_for_file(
                                    "ticker", instrument_ticker)
                                
                                await self.distribute_ticker_result_as_per_data_type(
                                    my_path_ticker, data_orders, instrument_ticker)
                                            
                                try:
                                    
                                    if "PERPETUAL" in data_orders["instrument_name"]:
                                        
                                        if "open_interest" in data_orders:
                                            await inserting_open_interest(currency, 
                                                                          WHERE_FILTER_TICK, 
                                                                          TABLE_OHLC1, 
                                                                          data_orders)

                                        #! is_transactionlog_vs_sub_accounts_ok
                                        #is_transactionlog_vs_my_trd_curr_ok
                                        #is_transactionlog_vs_my_trd_all_ok
                                        #is_my_orders_all_vs_sub_accounts_ok
                                        
                                            
                                        try:                                          
                                                                                        
                                            #log.critical (f" OPENING HEDGING-START-{instrument_ticker.upper()}")
                                                                                      
                                            TA_result_data_all = await querying_table("market_analytics_json")

                                            TA_result_data_only=  TA_result_data_all["list_data_only"]
                                            
                                            TA_result_data = [o for o in TA_result_data_only if currency_upper in o["instrument"]]                                                                                                    
                                            
                                            ticker= reading_from_pkl_data("ticker",instrument_ticker)
                                            
                                            try:
                                                ticker= ticker[0]
                                            except:
                                                ticker= []
                                                                                            
                                            if ticker !=[]:
                                                        
                                                try:
                                                    index_price= data_orders["index_price"]
                                                    
                                                except:
                                                    
                                                    index_price= ticker["index_price"]
                                                    
                                                    if index_price==[]:
                                                        index_price = ticker ["estimated_delivery_price"]
                                                    
                                                # get portfolio data  
                                                portfolio= reading_from_pkl_data("portfolio",currency)
                                                
                                                column_list: str= "instrument_name","label", "amount", "price","side"
                                    
                                                my_trades_currency: list= await get_query(trade_db_table, 
                                                                                            currency, 
                                                                                            "all", 
                                                                                            "all", 
                                                                                            column_list)
                                                
                                                my_trades_instrument: list= [o for o in my_trades_currency if instrument_ticker in o["instrument_name"]]
                                                # obtain spot equity
                                                equity: float = portfolio[0]["equity"]                                       
                                                                                    
                                                if ticker !=[] and index_price is not None and equity >0:
                                                
                                                    tick_TA=  max([o["tick"] for o in TA_result_data])
                                                    
                                                    server_time = get_now_unix_time()  
                                                    
                                                    log.debug (f"server_time {server_time}")
                                                    
                                                    delta_time = server_time-tick_TA
                                                    
                                                    delta_time_seconds = delta_time/1000                                                
                                                    
                                                    delta_time_expiration = min_expiration_timestamp - server_time  
                                                                                                        
                                                    if delta_time_seconds < 120:#ensure freshness of ta
                                                        
                                                        notional: float = compute_notional_value(index_price, equity)
                                                            
                                                        best_ask_prc: float = ticker["best_ask_price"] 
                                                        
                                                        column_trade= "trade_id","label"
                                                        
                                                        column_order= "instrument_name","label","order_id","amount"
                                                        
                                                        currency = extract_currency_from_text (instrument_ticker)
                                                        
                                                        data_from_db_trade_open = await get_query(archive_db_table, 
                                                                                                instrument_ticker, 
                                                                                                "all", 
                                                                                                "all", 
                                                                                                column_trade)     
                                                        
                                                        data_from_db_order_open_currency = await get_query(order_db_table, 
                                                                                                currency, 
                                                                                                "all", 
                                                                                                "all", 
                                                                                                column_order)    
                                                         
                                                        data_from_db_order_open = [o for o in data_from_db_order_open_currency \
                                                            if instrument_ticker in o["instrument_name"]]
                                                        
                                                        combined_result = data_from_db_trade_open + data_from_db_order_open
                                                       
                                                        for strategy in active_strategies:
                                                        
                                                            my_trades_strategy_open = [o for o in my_trades_instrument if "open" in (o["label"])\
                                                                and strategy in (o["label"]) ]

                                                            strategy_params= [o for o in strategy_atributes if o["strategy_label"] == strategy]                                                                
        
                                                            if "hedgingSpot" in strategy:
                                                                
                                                                log.debug (f"strategy {strategy}-START")
                                                                
                                                                hedging = HedgingSpot(strategy,
                                                                                      strategy_params)
                                                                
                                                                send_order: dict = (
                                                                await hedging.is_send_and_cancel_open_order_allowed(
                                                                    currency,
                                                                    instrument_ticker,
                                                                    active_futures,
                                                                    combined_result,
                                                                    notional,
                                                                    index_price,
                                                                    best_ask_prc,
                                                                    server_time,
                                                                    TA_result_data))
                                                                
                                                                if send_order["order_allowed"]:
                                                                    await if_order_is_true(send_order, instrument_ticker)
                                                                    await if_cancel_is_true(send_order)

                                                                if my_trades_strategy_open !=[]:
                                                                                                                                               
                                                                    best_bid_prc: float = ticker["best_bid_price"]
                                                                    
                                                                    get_prices_in_label_transaction_main = [o["price"] for o in my_trades_strategy_open]

                                                                    closest_price = get_closest_value(get_prices_in_label_transaction_main, best_bid_prc)

                                                                    nearest_transaction_to_index = [o for o in my_trades_strategy_open if o["price"] == closest_price]
                                                                    #log.debug (f"nearest_transaction_to_index {nearest_transaction_to_index}")
                                                                    
                                                                    send_closing_order: dict = await hedging.is_send_exit_order_allowed(
                                                                        TA_result_data,
                                                                        index_price,
                                                                        best_bid_prc,
                                                                        nearest_transaction_to_index,
                                                                        server_time,
                                                                    )
                                                                    #log.error (f"send_closing_order {send_closing_order}")
                                                                    await if_order_is_true(send_closing_order, instrument_ticker)
                                                                    await if_cancel_is_true(send_closing_order)

                                                                log.debug (f"strategy {strategy}-DONE")

                                                    # check for delivered instrument

                                                            if "futureSpread" in strategy:
                                                                log.error (f"strategy {strategy} {currency}-START")
                                                                
                                                                #for combo in active_combo_perp:
                                                                    #instrumen_ticker = combo["instrument_name"]
                                                                    #order_book_request = requests.get(order_book_end_point(instrumen_ticker,20)).json()["result"]
                                                                    #log.info (f"order_book_request {order_book_request}")
                                                                    #result = [o for o in transform_nested_dict_to_list(order_book_request) ]

                                                                    #log.info (f"instrumen_id {instrumen_ticker}")
                                                                    #log.info (f"result {result}")

                                                                db_order_open_strategy = [o for o in data_from_db_order_open_currency \
                                                                    if strategy in o["label"]]
                                                                
                                                                db_trade_open_strategy = [o for o in my_trades_currency \
                                                                    if strategy in o["label"]]
                                                                
                                                                amount_order_strategy = 0 if db_order_open_strategy == [] \
                                                                    else sum([o["amount"] for o in db_order_open_strategy])
                                                        
                                                                amount_trade_strategy = 0 if db_trade_open_strategy == [] \
                                                                    else sum([o["amount"] for o in db_trade_open_strategy])
                                                        
                                                                
                                                                net_positions = amount_order_strategy + amount_trade_strategy
                                                                #log.error (f"net_positions {net_positions}  amount_strategy {amount_order_strategy} amount_trade_strategy {amount_trade_strategy}")
                                                                future_spreads = FutureSpreads(strategy,
                                                                                            strategy_params)

                                                                log.error (f"strategy {strategy}-DONE")

                                                    if delta_time_expiration < 0:
                                                        
                                                        instruments_name_with_min_expiration_timestamp = futures_instruments [
                                                            "instruments_name_with_min_expiration_timestamp"]     
                                                        
                                                        # check any oustanding instrument that has deliverd
                                                        
                                                        for currency in currencies:
                                                            
                                                            delivered_transactions = [o for o in my_trades_currency \
                                                                if instruments_name_with_min_expiration_timestamp in o["instrument_name"]]
                                                            
                                                            if delivered_transactions:
                                                                
                                                                for transaction in delivered_transactions:
                                                                    delete_respective_closed_futures_from_trade_db (transaction, trade_db_table)

                                                        
                                                        # updating instrument
                                                        await sleep_and_restart ()
                                
                                            
                                        except ValueError:
                                            import traceback
                                            traceback.format_exc()
                                            log.info(f" error {error}")
                                            #continue
                                                                
                                except Exception as error:
                                    log.error(error)
                                    await raise_error_message(
                                        "WebSocket connection - failed to process data"
                                    )

                                    #continue
                                    
                else:
                
                    log.info("WebSocket connection has broken.")
                    await raise_error_message(
                        "error-WebSocket connection EXCHANGE has broken",
                        0.1,
                        "WebSocket connection EXCHANGE has broken",
                    )
        
                    #! Establish restart procedure
                
    async def distribute_ticker_result_as_per_data_type(
        self, my_path_ticker, data_orders, instrument
    ) -> None:
        """ """

        try:
                        
            if data_orders["type"] == "snapshot":
                replace_data(my_path_ticker, data_orders)

            else:
                ticker_change: list = read_data(my_path_ticker)
                if ticker_change != []:
                    
                    for item in data_orders:
                        ticker_change[0][item] = data_orders[item]
                        replace_data(my_path_ticker, ticker_change)

        except Exception as error:
            await raise_error_message(
                error,
                "WebSocket connection - failed to distribute_incremental_ticker_result_as_per_data_type",
            )
            
    async def establish_heartbeat(self) -> None:
        """
        Requests DBT's `public/set_heartbeat` to
        establish a heartbeat connection.
        """
        msg: dict = {
            "jsonrpc": "2.0",
            "id": 9098,
            "method": "public/set_heartbeat",
            "params": {"interval": 10},
        }

        try:
            await self.websocket_client.send(json.dumps(msg))
        except Exception as error:
            log.warning(error)

    async def heartbeat_response(self) -> None:
        """
        Sends the required WebSocket response to
        the Deribit API Heartbeat message.
        """
        msg: dict = {
            "jsonrpc": "2.0",
            "id": 8212,
            "method": "public/test",
            "params": {},
        }

        try:
            await self.websocket_client.send(json.dumps(msg))

        except Exception as error:
            log.warning(error)

    async def ws_auth(self) -> None:
        """
        Requests DBT's `public/auth` to
        authenticate the WebSocket Connection.
        """
        msg: dict = {
            "jsonrpc": "2.0",
            "id": 9929,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        }
        
        await self.websocket_client.send(json.dumps(msg))

    async def ws_refresh_auth(self) -> None:
        """
        Requests DBT's `public/auth` to refresh
        the WebSocket Connection's authentication.
        """
        while True:
            if self.refresh_token_expiry_time is not None:
                if datetime.utcnow() > self.refresh_token_expiry_time:
                    msg: dict = {
                        "jsonrpc": "2.0",
                        "id": 9929,
                        "method": "public/auth",
                        "params": {
                            "grant_type": "refresh_token",
                            "refresh_token": self.refresh_token,
                        },
                    }

                    await self.websocket_client.send(json.dumps(msg))

            await asyncio.sleep(150)

    async def ws_operation(
        self, operation: str, ws_channel: str, id: int = 100
    ) -> None:
        """
        Requests `public/subscribe` or `public/unsubscribe`
        to DBT's API for the specific WebSocket Channel.
        """
        await asyncio.sleep(5)
        
        id = id_numbering.id(operation, ws_channel)

        msg: dict = {
            "jsonrpc": "2.0",
            "method": f"private/{operation}",
            "id": id,
            "params": {"channels": [ws_channel]},
        }

        await self.websocket_client.send(json.dumps(msg))


def main():
    """
    https://stackoverflow.com/questions/70880668/is-it-possible-to-iterate-a-list-calling-async-function
    https://stackoverflow.com/questions/56161595/how-to-use-async-for-in-python
    """
    # https://www.codementor.io/@jflevesque/python-asynchronous-programming-with-asyncio-library-eq93hghoc
    sub_account = "deribit-147691"
    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]   

    try:

        StreamAccountData(client_id=client_id, client_secret=client_secret)

    except Exception as error:
        catch_error_message(
            error, 1, "app"
        )
        
if __name__ == "__main__":
    try:
        
        main()
        
        while True:
            loop.run_until_complete(schedule.run_pending())

    except (KeyboardInterrupt, SystemExit):

        asyncio.get_event_loop().run_until_complete(main().stop_ws())
        
    except Exception as error:
                
        catch_error_message(
        error, 10, "app"
        )
