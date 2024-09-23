# -*- coding: utf-8 -*-

# built ins
import asyncio
from datetime import datetime
# installed
from loguru import logger as log

# user defined formula
from utilities.system_tools import (
    raise_error_message,
    provide_path_for_file,
    reading_from_db_pickle,
    sleep_and_restart
)
from loguru import logger as log
from utilities.pickling import replace_data, read_data
from utilities.string_modification import (
    remove_redundant_elements,
    remove_dict_elements,
    extract_currency_from_text,
    parsing_label,
    my_trades_open_sqlite_detailing,
    parsing_sqlite_json_output,
)
from strategies.config_strategies import preferred_spot_currencies, paramaters_to_balancing_transactions
from db_management.sqlite_management import (
    insert_tables,
    deleting_row,
    querying_arithmetic_operator,
    executing_query_with_return,
    executing_query_based_on_currency_or_instrument_and_strategy as get_query
)

from websocket_management.cleaning_up_transactions import (
    reconciling_between_db_and_exchg_data, 
    clean_up_closed_futures_because_has_delivered,
    clean_up_closed_transactions)
from utilities.number_modification import get_closest_value

# from market_understanding import futures_analysis
from db_management import sqlite_management
from strategies import hedging_spot, market_maker as MM
from strategies.basic_strategy import (
    is_everything_consistent,
    get_strategy_config_all,
    get_transaction_side,
    check_db_consistencies,
    check_if_id_has_used_before,
    
)

from deribit_get import GetPrivateData, telegram_bot_sendtext
from configuration.config import main_dotenv

ONE_MINUTE: int = 60000
ONE_PCT: float = 1 / 100
NONE_DATA: None = [0, None, []]


def parse_dotenv(sub_account) -> dict:
    return main_dotenv(sub_account)


async def raise_error(error, idle: int = None) -> None:
    """ """
    await raise_error_message(error, idle)


async def get_private_data(currency: str = None) -> list:
    """
    Provide class object to access private get API
    """

    sub_account = "deribit-147691"
    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]
    connection_url: str = "https://www.deribit.com/api/v2/"

    return GetPrivateData(connection_url, client_id, client_secret, currency)


async def get_account_summary(currency) -> list:
    """ """

    private_data = await get_private_data(currency)

    account_summary: dict = await private_data.get_account_summary()

    return account_summary["result"]


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:

    return await telegram_bot_sendtext(bot_message, purpose)


async def get_sub_account(currency) -> list:
    """ """

    private_data = await get_private_data(currency)

    result_sub_account: dict = await private_data.get_subaccounts()

    return result_sub_account["result"]

        
async def get_transaction_log(currency: str, start_timestamp: int, count: int= 1000) -> list:
    """ """

    private_data = await get_private_data(currency)

    result_transaction_log: dict = await private_data.get_transaction_log(start_timestamp, count)

    result_transaction_log_to_result = result_transaction_log["result"]

    result_transaction_log_to_result_logs = [] if result_transaction_log_to_result  == []\
        else result_transaction_log_to_result["logs"]

    return result_transaction_log_to_result_logs


        
async def resupply_transaction_log(currency: str) -> list:
    """ """

    log.warning(f"resupply {currency.upper()} TRANSACTION LOG db-START")
    
    currencies = preferred_spot_currencies()
        
    table= "transaction_log_json"
    
    where_filter= "timestamp"
    
    first_tick_query= querying_arithmetic_operator(where_filter, "MAX", table)
    
    first_tick_query_result = await executing_query_with_return(first_tick_query)
    
    first_tick_fr_sqlite= first_tick_query_result [0]["MAX (timestamp)"] 
                    
    balancing_params=paramaters_to_balancing_transactions()

    max_closed_transactions_downloaded_from_sqlite=balancing_params["max_closed_transactions_downloaded_from_sqlite"]   
    
    for currency in currencies:   
        
        transaction_log= await get_transaction_log (currency, 
                                                    first_tick_fr_sqlite-1, 
                                                    max_closed_transactions_downloaded_from_sqlite)
                
        for transaction in transaction_log:
            
            modified_dict= remove_dict_elements(transaction,"info")
                        
            timestamp_log= modified_dict ["timestamp"]
            
            type_log= modified_dict ["type"]
                        
            if timestamp_log > first_tick_fr_sqlite:

                custom_label= f"custom-{type_log.title()}-{timestamp_log}"
                
                if "trade" in type_log:
                
                    tran_id_log= modified_dict ["trade_id"]

                    instrument_name_log= modified_dict ["instrument_name"]
                    
                    column_list: str="label", "trade_id"
                    
                    from_sqlite_open= await get_query ("my_trades_all_json", 
                                                       instrument_name_log, 
                                                       "all", 
                                                       "all", 
                                                       column_list)                                       

                    from_sqlite_closed = await get_query("my_trades_closed_json", 
                                                         instrument_name_log, 
                                                         "all", 
                                                         "all", 
                                                         column_list,
                                                         max_closed_transactions_downloaded_from_sqlite, 
                                                         "id")   
                    
                    combined= from_sqlite_open + from_sqlite_closed
                    
                    label_log= [o["label"] for o in combined if tran_id_log in o["trade_id"]]
                                                            
                    if label_log !=[]:
                        modified_dict.update({"label": label_log[0]})
                    
                    else:
                        modified_dict.update({"label": custom_label})
                
                else:
                    modified_dict.update({"label": custom_label})
                
                #log.debug (f"transaction_log_json {modified_dict}")
                await insert_tables("transaction_log_json", modified_dict)

    log.warning(f"resupply {currency.upper()} TRANSACTION LOG db-DONE")
        
    
def compute_notional_value(index_price: float, equity: float) -> float:
    """ """
    return index_price * equity


def reading_from_db(end_point, instrument: str = None, status: str = None) -> float:
    """ """
    return reading_from_db_pickle(end_point, instrument, status)


async def send_limit_order(params) -> None:
    """ """
    private_data = await get_private_data()

    #await private_data.get_cancel_order_all()
    await private_data.send_limit_order(params)


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

        everything_consistent = is_everything_consistent(params)

        if  everything_consistent:
            await inserting_additional_params(params)
            await send_limit_order(params)
            #await asyncio.sleep(10)


async def get_my_trades_from_exchange(count: int, currency) -> list:
    """ """
    private_data = await get_private_data(currency)
    trades: list = await private_data.get_user_trades_by_currency(count)

    return [] if trades == [] else trades["result"]["trades"]


async def cancel_by_order_id(open_order_id) -> None:
    private_data = await get_private_data()

    result = await private_data.get_cancel_order_byOrderId(open_order_id)
    
    try:
        if (result["error"]["message"])=="not_open_order":
            
            where_filter = f"order_id"
            
            await sqlite_management.deleting_row(
                                "orders_all_json",
                                "databases/trading.sqlite3",
                                where_filter,
                                "=",
                                open_order_id,
                            )
            
    except:

        log.critical(f"CANCEL_by_order_id {result} {open_order_id}")

        return result


async def cancel_the_cancellables(filter: str = None) -> None:

    params: list = get_strategy_config_all()
    cancellable_strategies: dict = [
        o["strategy"] for o in params if o["cancellable"] == True
    ]
    
    log.error (f"cancellable_strategies {cancellable_strategies}  filter {filter}")
    currencies: list = preferred_spot_currencies()
    
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

                            await sqlite_management.deleting_row(
                                "orders_all_json",
                                "databases/trading.sqlite3",
                                where_filter,
                                "=",
                                order_id,
                            )


async def if_cancel_is_true(order) -> None:
    """ """
    # log.debug (order)
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
                    await procedures_for_unlabelled_orders(order, instrument_name)

    else:
        if open_orders_from_sub_accounts !=[]:
            for order in open_orders_from_sub_accounts:
                await insert_tables("orders_all_json", order)

def reading_from_pkl_data(end_point, currency, status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, currency, status)
    data = read_data(path)

    return data
    
async def check_db_consistencies_and_clean_up_imbalances(currency: str, sub_accounts: list =[]) -> None:
    
    if sub_accounts== [] or sub_accounts is None:
        sub_accounts = reading_from_pkl_data("sub_accounts",currency)

    sub_accounts=sub_accounts[0]

    positions= sub_accounts["positions"]

    active_instruments_from_positions = [o["instrument_name"] for o in positions]
                    
    column_list_order: str="order_id", "label"
    
    column_list_trade: str= "instrument_name","label", "amount", "price","has_closed_label", "timestamp"

    my_trades_currency: list= await get_query("my_trades_all_json", currency, "all", "all", column_list_trade)

    all_outstanding_instruments = [o["instrument_name"] for o in my_trades_currency]
                      
    open_orders_from_sub_accounts= sub_accounts["open_orders"]
    
    positions_from_sub_accounts= sub_accounts["positions"]
    
    
    for instrument_name in all_outstanding_instruments:
        log.warning (f"instrument_name {instrument_name}")      
        log.warning (f"instrument_name {instrument_name in active_instruments_from_positions}")      
        
        my_trades_instrument: list= await get_query("my_trades_all_json", instrument_name, "all", "all", column_list_trade)
        
        currency=extract_currency_from_text(instrument_name)
            
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
            await cancel_the_cancellables()
                                                        
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
                    #log.critical (f"transaction_log_from_sqlite_open {transaction_log_from_sqlite_open}")
                    delivered_transaction= [o for o in transaction_log_from_sqlite_open if "delivery" in o["type"] ]
                    delivery_timestamp= [o["timestamp"] for o in delivered_transaction ]
                    delivery_timestamp= [] if delivery_timestamp==[] else max(delivery_timestamp)
                    
                    #log.warning (f"delivery_timestamp {delivery_timestamp} last_time_stamp_sqlite {last_time_stamp_sqlite} last_time_stamp_sqlite < delivery_timestamp {last_time_stamp_sqlite < delivery_timestamp}")
                    
                    if delivery_timestamp !=[] and last_time_stamp_sqlite < delivery_timestamp:
                            
                            transactions_from_other_side= [ o for o in my_trades_currency if instrument_name not in o["instrument_name"]]
                            for transaction in transactions_from_other_side:
                                log.error (f"transactions_from_other_side {transaction}")
                            
                            await clean_up_closed_futures_because_has_delivered(instrument_name, delivered_transaction)
                        
            
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
    log.info(f"resupply {currency.upper()} sub account db-START")
    sub_accounts = await get_sub_account(currency)

    my_path_sub_account = provide_path_for_file("sub_accounts", currency)
    replace_data(my_path_sub_account, sub_accounts)
    
async def inserting_additional_params(params: dict) -> None:
    """ """

    if "open" in params["label"]:
        await sqlite_management.insert_tables("supporting_items_json", params)


def get_last_price(my_trades_open_strategy: list) -> float:
    """ """
    my_trades_open_strategy_buy = [
        o for o in my_trades_open_strategy if o["amount"] > 0
    ]
    my_trades_open_strategy_sell = [
        o for o in my_trades_open_strategy if o["amount"] < 0
    ]
    buy_traded_price = [o["price"] for o in my_trades_open_strategy_buy]
    sell_traded_price = [o["price"] for o in my_trades_open_strategy_sell]

    return {
        "min_buy_traded_price": 0 if buy_traded_price == [] else min(buy_traded_price),
        "max_sell_traded_price": (
            0 if sell_traded_price == [] else max(sell_traded_price)
        ),
    }


def delta_price_pct(last_traded_price: float, market_price: float) -> bool:
    """ """
    delta_price = abs(abs(last_traded_price) - market_price)
    return (
        0
        if (last_traded_price == [] or last_traded_price == 0)
        else delta_price / last_traded_price
    )
async def procedures_for_unlabelled_orders(order, instrument_name):
    """_summary_
    """
    from transaction_management.deribit.open_orders_management import manage_orders

    side= get_transaction_side(order)
    order.update({"everything_is_consistent": True})
    order.update({"order_allowed": True})
    order.update({"entry_price": order["price"]})
    order.update({"size": order["amount"]})
    order.update({"type": "limit"})
    order.update({"side": side})
    side_label= "Short" if side== "sell" else "Long"
    last_update=order["creation_timestamp"]
    label_open: str = (f"custom{side_label.title()}-open-{last_update}")
    order.update({"label": label_open})
    log.info (f"order {order}")
    
    label_has_exist_before= await check_if_id_has_used_before (instrument_name,"label",label_open, 100)
    
    order_id= order["order_id"]
    await cancel_by_order_id (order_id)
    
    if not label_has_exist_before:
        await if_order_is_true(order, instrument_name)
        await manage_orders (order)       
    await sleep_and_restart()

def delta_price_constraint(
    threshold: float,
    last_price_all: dict,
    market_price: float,
    net_sum_strategy: int,
    side: str,
) -> bool:
    """ """
    is_reorder_ok = False
    last_traded_price = None

    if side == "buy":
        last_traded_price = last_price_all["min_buy_traded_price"]
        delta_price_exceed_threhold = (
            delta_price_pct(last_traded_price, market_price) > threshold
            and market_price < last_traded_price
        )
        is_reorder_ok = delta_price_exceed_threhold or net_sum_strategy <= 0

    if side == "sell":
        last_traded_price = last_price_all["max_sell_traded_price"]
        delta_price_exceed_threhold = (
            delta_price_pct(last_traded_price, market_price) > threshold
            and market_price > last_traded_price
        )
        is_reorder_ok = delta_price_exceed_threhold or net_sum_strategy >= 0

    return True if last_traded_price == 0 else is_reorder_ok


def get_label_transaction_main(label_transaction_net: list) -> list:
    """ """

    return remove_redundant_elements(
        [(parsing_label(o))["main"] for o in label_transaction_net]
    )


def get_trades_within_respective_strategy(my_trades_open: list, label: str) -> list:
    """ """

    return [o for o in my_trades_open if parsing_label(o["label"])["main"] == label]


def get_min_max_price_from_transaction_in_strategy(
    get_prices_in_label_transaction_main: list,
) -> list:
    """ """
    return dict(
        max_price=(
            0
            if get_prices_in_label_transaction_main == []
            else max(get_prices_in_label_transaction_main)
        ),
        min_price=(
            0
            if get_prices_in_label_transaction_main == []
            else min(get_prices_in_label_transaction_main)
        ),
    )

async def closing_transactions(
    label_transaction_net,
    strategies,
    my_trades_open_sqlite,
    my_trades_open,
    market_condition,
) -> float:
    """ """

    log.critical(f"CLOSING TRANSACTIONS-START")

    my_trades_open_all: list = my_trades_open_sqlite["all"]

    my_trades_open: list = my_trades_open_sqlite["list_data_only"]
    # log.error(f"my_trades_open {my_trades_open}")
    # log.error(f"transactions_all_summarized {transactions_all_summarized}")

    label_transaction_main = get_label_transaction_main(label_transaction_net)

    # log.error(f"label_transaction_main {label_transaction_main}")

    for label in label_transaction_main:
        log.debug(f"label {label}")
        
        if label != None:

            my_trades_open_strategy = get_trades_within_respective_strategy(
                my_trades_open, label
            )

            get_prices_in_label_transaction_main = [
                o["price"] for o in my_trades_open_strategy
            ]
            max_price = get_min_max_price_from_transaction_in_strategy(
                get_prices_in_label_transaction_main
            )["max_price"]

            min_price = get_min_max_price_from_transaction_in_strategy(
                get_prices_in_label_transaction_main
            )["min_price"]

            if "Short" in label or "hedging" in label:
                transaction = [
                    o for o in my_trades_open_strategy if o["price"] == max_price
                ]
            if "Long" in label:
                transaction = [
                    o for o in my_trades_open_strategy if o["price"] == min_price
                ]

            if "futureSpread" not in label:
                    
                label = [parsing_label(o["label"])["transaction_net"] for o in transaction][0]

                # result example: 'hedgingSpot'/'supplyDemandShort60'
                label_main = parsing_label(label)["main"]

                # get startegy details
                strategy_attr = [o for o in strategies if o["strategy"] == label_main][0]

                my_trades_open_sqlite_transaction_net_strategy: list = (
                    my_trades_open_sqlite_detailing(
                        my_trades_open_all, label, "transaction_net"
                    )
                )

                open_trade_strategy_label = parsing_sqlite_json_output(
                    [o["data"] for o in my_trades_open_sqlite_transaction_net_strategy]
                )

                instrument: list = [o["instrument_name"] for o in open_trade_strategy_label][0]

                ticker: list = reading_from_db("ticker", instrument)

                if ticker != []:

                    # get instrument_attributes
                    # instrument_attributes_all: list = reading_from_db("instruments", currency)[
                    #    0
                    # ]["result"]
                    # instrument_attributes: list = [
                    ##    o
                    #    for o in instrument_attributes_all
                    #    if o["instrument_name"] == instrument
                    # ]
                    # tick_size: float = instrument_attributes[0]["tick_size"]
                    # taker_commission: float = instrument_attributes[0]["taker_commission"]
                    # min_trade_amount: float = instrument_attributes[0]["min_trade_amount"]
                    # contract_size: float = instrument_attributes[0]["contract_size"]

                    index_price: float = ticker[0]["index_price"]

                    # get bid and ask price
                    best_bid_prc: float = ticker[0]["best_bid_price"]
                    best_ask_prc: float = ticker[0]["best_ask_price"]

                    if False and "hedgingSpot" in strategy_attr["strategy"]:

                        closest_price = get_closest_value(
                            get_prices_in_label_transaction_main, best_bid_prc
                        )

                        if "hedging" in label:
                            nearest_transaction_to_index = [
                                o
                                for o in my_trades_open_strategy
                                if o["price"] == closest_price
                            ]

                        log.debug(
                            f" {label_main} closest_price {closest_price} best_bid_prc {best_bid_prc} pct diff {abs(closest_price-best_bid_prc)/closest_price}"
                        )

                        hedging = hedging_spot.HedgingSpot(label_main)

                        send_closing_order: dict = await hedging.is_send_exit_order_allowed(
                            market_condition,
                            index_price,
                            best_ask_prc,
                            best_bid_prc,
                            nearest_transaction_to_index,
                        )

                        await if_order_is_true(send_closing_order, instrument)

                    if "marketMaker" in strategy_attr["strategy"] and False:

                        market_maker = MM.MarketMaker(label_main)

                        send_closing_order: dict = (
                            await market_maker.is_send_exit_order_allowed(
                                market_condition,
                                best_ask_prc,
                                best_bid_prc,
                                open_trade_strategy_label,
                            )
                        )
                        log.critical(f" send_closing_order {send_closing_order}")
                        # await if_order_is_true(send_closing_order, instrument)

    log.critical(f"CLOSING TRANSACTIONS-DONE")
