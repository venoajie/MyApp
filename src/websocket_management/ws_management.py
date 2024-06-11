# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from loguru import logger as log

# user defined formula
from utilities import (
    pickling,
    system_tools,
    string_modification as str_mod,
    number_modification as num_mod,
)
from market_understanding import futures_analysis
from db_management import sqlite_management
from strategies import basic_strategy,hedging_spot, market_maker as MM
import deribit_get
from configuration import config

ONE_MINUTE: int = 60000
ONE_PCT: float = 1 / 100
NONE_DATA: None = [0, None, []]


def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


async def raise_error(error, idle: int = None) -> None:
    """ """
    await system_tools.raise_error_message(error, idle)


async def get_private_data(currency: str = None) -> list:
    """
    Provide class object to access private get API
    """

    sub_account = "deribit-147691"
    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]
    connection_url: str = "https://www.deribit.com/api/v2/"

    return deribit_get.GetPrivateData(
        connection_url, client_id, client_secret, currency
    )


async def get_account_summary() -> list:
    """ """

    private_data = await get_private_data()

    account_summary: dict = await private_data.get_account_summary()

    return account_summary["result"]


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

async def get_sub_account(currency) -> list:
    """ """

    private_data = await get_private_data(currency)

    result_sub_account: dict = await private_data.get_subaccounts()

    return result_sub_account["result"]


async def last_open_interest_fr_sqlite(last_tick_query_ohlc1) -> float:
    """ """
    try:
        last_open_interest = await sqlite_management.executing_query_with_return(
            last_tick_query_ohlc1
        )

    except Exception as error:
        await system_tools.raise_error_message(
            error, "Capture market data - failed to fetch last open_interest",
        )
    return last_open_interest[0]["open_interest"]


async def last_tick_fr_sqlite(last_tick_query_ohlc1) -> int:
    """ """
    try:
        last_tick1_fr_sqlite = await sqlite_management.executing_query_with_return(
            last_tick_query_ohlc1
        )

    except Exception as error:
        await system_tools.raise_error_message(
            error, "Capture market data - failed to fetch last_tick_fr_sqlite",
        )
    return last_tick1_fr_sqlite[0]["MAX (tick)"]


async def distribute_ticker_result_as_per_data_type(
    my_path_ticker, data_orders, instrument
) -> None:
    """ """

    try:
        # ticker: list = pickling.read_data(my_path_ticker)

        if data_orders["type"] == "snapshot":
            pickling.replace_data(my_path_ticker, data_orders)

            # ticker_fr_snapshot: list = pickling.read_data(my_path_ticker)

        else:
            ticker_change: list = pickling.read_data(my_path_ticker)
            if ticker_change != []:
                # log.debug (ticker_change)

                for item in data_orders:
                    ticker_change[0][item] = data_orders[item]
                    pickling.replace_data(my_path_ticker, ticker_change)

    except Exception as error:
        await system_tools.raise_error_message(
            error,
            "WebSocket management - failed to distribute_incremental_ticker_result_as_per_data_type",
        )


async def reading_from_pkl_database(currency) -> float:
    """ """

    path_sub_accounts: str = system_tools.provide_path_for_file(
        "sub_accounts", currency
    )

    path_portfolio: str = system_tools.provide_path_for_file("portfolio", currency)
    path_positions: str = system_tools.provide_path_for_file("positions", currency)
    positions = pickling.read_data(path_positions)
    sub_account = pickling.read_data(path_sub_accounts)
    positions_from_sub_account = sub_account[0]["positions"]
    open_orders_from_sub_account = sub_account[0]["open_orders"]
    portfolio = pickling.read_data(path_portfolio)

    # at start, usually position == None
    if positions in NONE_DATA:
        positions = positions_from_sub_account  # await self.get_positions ()
        pickling.replace_data(path_positions, positions)

    # log.debug (my_trades_open)
    if portfolio in NONE_DATA:
        portfolio = await get_account_summary()
        pickling.replace_data(path_portfolio, portfolio)
        portfolio = pickling.read_data(path_portfolio)

    return {
        "positions": positions,
        "positions_from_sub_account": positions_from_sub_account,
        "open_orders_from_sub_account": open_orders_from_sub_account,
        "portfolio": portfolio,
    }


def compute_notional_value(index_price: float, equity: float) -> float:
    """ """
    return index_price * equity


async def is_size_consistent(
    sum_my_trades_open_sqlite_all_strategy, size_from_positions
) -> bool:
    """ """

    log.warning(
        f" size_from_sqlite {sum_my_trades_open_sqlite_all_strategy} size_from_positions {size_from_positions}"
    )

    return sum_my_trades_open_sqlite_all_strategy == size_from_positions


def reading_from_db(end_point, instrument: str = None, status: str = None) -> float:
    """ """
    return system_tools.reading_from_db_pickle(end_point, instrument, status)

async def manage_params (params: dict) -> None:

    log.debug(f"additional_params {params}")
    
    if "open" in params:
        await sqlite_management.insert_tables("supporting_items_json", params)


async def send_limit_order(params) -> None:
    """ """
    private_data = await get_private_data()
    
    await private_data.get_cancel_order_all()
    await private_data.send_limit_order(params)


async def if_order_is_true(order, instrument: str = None) -> None:
    """ """
    # log.debug (order)
    if order["order_allowed"]:

        # get parameter orders
        params = order["order_parameters"]

        if instrument != None:
            # update param orders with instrument
            params.update({"instrument": instrument})

        is_app_running=system_tools.is_current_file_running("app")
        everything_consistent= basic_strategy.is_everything_consistent(params)
        
        await manage_params(params)
        
        if is_app_running and everything_consistent:
            await send_limit_order(params)
            await asyncio.sleep(10)

async def cancel_by_order_id(open_order_id) -> None:
    private_data = await get_private_data()

    result = await private_data.get_cancel_order_byOrderId(open_order_id)
    log.info(f"CANCEL_by_order_id {result}")

    return result


async def if_cancel_is_true(order) -> None:
    """ """
    # log.debug (order)
    if order["cancel_allowed"]:

        # get parameter orders
        await cancel_by_order_id(order["cancel_id"])

async def update_portfolio(data_orders, currency) -> None:

    my_path_portfolio = system_tools.provide_path_for_file("portfolio", currency)
    pickling.replace_data(my_path_portfolio, data_orders)

async def resupply_sub_accountdb(currency) -> None:

    # resupply sub account db
    log.info(f"resupply sub account db-START")
    sub_accounts = await get_sub_account(currency)

    my_path_sub_account = system_tools.provide_path_for_file("sub_accounts", currency)
    pickling.replace_data(my_path_sub_account, sub_accounts)
    log.info(f"{sub_accounts}")
    log.info(f"resupply sub account db-DONE")

async def manage_positions (positions: dict, currency: str) -> None:

    my_path_position = system_tools.provide_path_for_file("positions", currency)
    pickling.replace_data(my_path_position, positions)

async def manage_trades (trades: dict) -> None:

    for trade in trades:
        log.info(f"trade {trade}")
        label=trade["label"]

        log.info(f"label {label}")
        additional_params = sqlite_management.querying_additional_params()
        log.info(f"get_additional_params {additional_params}")
        params=await sqlite_management.executing_query_with_return(additional_params)["data"]
        log.info(f"params {params}")
        additional_params_label = [
                o for o in params if label in o
            ]
        log.info(f"additional_params_label {additional_params_label}")
        trade.update({"take_profit": additional_params["take_profit"]})
        log.info(f"trade {trade}")

        await sqlite_management.insert_tables("my_trades_all_json", trade)

async def manage_orders (orders: dict) -> None:

    for order in orders:

        #! ##############################################################################

        open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
            "orders_all_json"
        )
        len_open_orders_sqlite_list_data = len([o for o in open_orders_sqlite])
        #log.warning(
        #    f" order sqlite BEFORE {len_open_orders_sqlite_list_data} {open_orders_sqlite}"
        #)

        #! ##############################################################################

        #log.warning(f"order {order}")
        # log.error ("trade_seq" not in order)
        # log.error ("trade_seq" in order)

        if "trade_seq" not in order:
            # get the order state
            order_state = order["order_state"]

        if "trade_seq" in order:

            # get the order state
            order_state = order["state"]

        log.error(f"ORDER STATE {order_state}")

        if (
            order_state == "cancelled"
            or order_state == "filled"
            or order_state == "triggered"
        ):

            order_id = (
                order["order_id"]
                if order_state != "triggered"
                else ["stop_order_id'"]
            )

            # open_orders_sqlite =  await syn.querying_all('orders_all_json')
            open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
                "orders_all_json"
            )
            # open_orders_sqlite_list_data =  open_orders_sqlite['list_data_only']

            is_order_id_in_active_orders = [
                o for o in open_orders_sqlite if o["order_id"] == order_id
            ]

            where_filter = f"order_id"
            if is_order_id_in_active_orders == []:
                order_id = order["label"]
                where_filter = f"label_main"

            log.critical(f" deleting {order_id}")
            await sqlite_management.deleting_row(
                "orders_all_json",
                "databases/trading.sqlite3",
                where_filter,
                "=",
                order_id,
            )

        if (
            order_state == "open"
            or order_state == "untriggered"
            or order_state == "triggered"
        ):

            await sqlite_management.insert_tables("orders_all_json", order)

        #! ###########################################################
        open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
            "orders_all_json"
        )
        len_open_orders_sqlite_list_data = len([o for o in open_orders_sqlite])
        log.critical(
            f" order sqlite AFTER {len_open_orders_sqlite_list_data} {open_orders_sqlite}"
        )
        
        everything_consistent= basic_strategy.is_everything_consistent(order)
        log.critical (f' ORDERS everything_consistent {everything_consistent} everything_NOT_consistent {not everything_consistent}')
        
        if  not everything_consistent:
            await cancel_by_order_id(order["cancel_id"])
            await telegram_bot_sendtext('size or open order is inconsistent', "general_error")

    #! ###########################################################

async def update_user_changes(data_orders, my_trades_open_sqlite, currency) -> None:

    from websocket_management.cleaning_up_transactions import (
            clean_up_closed_transactions,
        )
    
    log.info(f"update_user_changes-START")
    #log.info (data_orders)

    positions = data_orders["positions"]
    trades = data_orders["trades"]
    orders = data_orders["orders"]
    my_trades_open_all: list = my_trades_open_sqlite["all"]
    
    if trades:
        await manage_trades (trades)
        await clean_up_closed_transactions(my_trades_open_all)
        
    if orders:
        #log.warning(f"my_orders {data_orders}")
        #log.debug(f"my_orders {orders}")

        await manage_orders (orders)
        await clean_up_closed_transactions(my_trades_open_all)

    if positions:
        await manage_positions (positions, currency)
    
    log.info(f"update_user_changes-END")

def get_last_price(my_trades_open_strategy: list) -> float:
    """
    """
    my_trades_open_strategy_buy= [o for o in my_trades_open_strategy if o["amount_dir"] > 0] 
    my_trades_open_strategy_sell= [o for o in my_trades_open_strategy if o["amount_dir"] < 0] 
    buy_traded_price= [o["price"] for o in my_trades_open_strategy_buy] 
    sell_traded_price= [o["price"] for o in my_trades_open_strategy_sell] 

    log.info (
                    f"buy_traded_price   {buy_traded_price} sell_traded_price   {sell_traded_price}"
                )
    log.debug ([o["amount_dir"] for o in my_trades_open_strategy_buy] )

    log.error ([o["amount_dir"] for o in my_trades_open_strategy_sell] )
    
    return  {
            "min_buy_traded_price": 0 if buy_traded_price ==[] else min(buy_traded_price),
            "max_sell_traded_price": 0 if sell_traded_price ==[] else max(sell_traded_price)
        }

def delta_price_pct(last_traded_price: float, market_price: float) -> bool:
    """
    """
    delta_price= abs(abs(last_traded_price)-market_price)
    return 0 if  (last_traded_price == [] or last_traded_price == 0) \
        else delta_price/last_traded_price

def delta_price_constraint(threshold: float, last_price_all: dict, market_price: float, net_sum_strategy: int, side: str) -> bool:
    """
    """
    is_reorder_ok= False
    last_traded_price=None

    if side=="buy":
        last_traded_price= last_price_all["min_buy_traded_price"]
        delta_price_exceed_threhold= delta_price_pct(last_traded_price,market_price) > threshold \
            and market_price < last_traded_price
        is_reorder_ok=  delta_price_exceed_threhold or net_sum_strategy <= 0

    if side=="sell":
        last_traded_price= last_price_all["max_sell_traded_price"]
        delta_price_exceed_threhold= delta_price_pct(last_traded_price,market_price) > threshold \
            and market_price > last_traded_price
        is_reorder_ok= delta_price_exceed_threhold or net_sum_strategy >= 0

    log.debug(
                    f"constraint   {is_reorder_ok} last_traded_price   {last_traded_price}  market_price   {market_price} side   {side}" 
                )       
    return True if last_traded_price==0 else is_reorder_ok

async def opening_transactions(
    instrument,
    portfolio,
    strategies,
    my_trades_open_sqlite,
    size_from_positions,
    server_time,
    market_condition,
    take_profit_pct_daily
) -> None:
    """ """

    log.warning(f"OPENING TRANSACTIONS-START")

    try:
        my_trades_open_all: list = my_trades_open_sqlite["all"]
        # log.error (my_trades_open_all)

        ticker: list = reading_from_db("ticker", instrument)

        if ticker != []:

            # get bid and ask price
            best_bid_prc: float = ticker[0]["best_bid_price"]
            best_ask_prc: float = ticker[0]["best_ask_price"]

            # index price
            index_price: float = ticker[0]["index_price"]

            # obtain spot equity
            equity: float = portfolio[0]["equity"]

            # compute notional value
            notional: float = compute_notional_value(index_price, equity)

            # execute each strategy
            for strategy_attr in strategies:
                strategy_label = strategy_attr["strategy"]

                log.critical(f" {strategy_label}")

                net_sum_strategy = str_mod.get_net_sum_strategy_super_main(
                    my_trades_open_sqlite, strategy_label
                )
                net_sum_strategy_main = str_mod.get_net_sum_strategy_main(
                    my_trades_open_sqlite, strategy_label
                )
                log.debug(
                    f"net_sum_strategy   {net_sum_strategy} net_sum_strategy_main   {net_sum_strategy_main}"
                )

                sum_my_trades_open_sqlite_all_strategy: list = str_mod.sum_my_trades_open_sqlite(
                    my_trades_open_all, strategy_label
                )
                size_is_consistent: bool = await is_size_consistent(
                    sum_my_trades_open_sqlite_all_strategy, size_from_positions
                )

                if size_is_consistent:  # and open_order_is_consistent:
   
                    THRESHOLD_BEFORE_REORDER = ONE_PCT/2
                    
                    my_trades_open = [o for o in my_trades_open_all if "open" in (o["label_main"])]

                    my_trades_open_strategy = [
                o
                for o in my_trades_open
                if strategy_label in (o["label_main"])
            ]
   
                    last_price_all= get_last_price(my_trades_open_strategy)
                 
                    log.debug(
                    f"last_price   {last_price_all}"
                )

                    if "hedgingSpot" in strategy_attr["strategy"]:

                        THRESHOLD_TIME_TO_CANCEL = 3

                        hedging = hedging_spot.HedgingSpot(strategy_label)

                        send_order: dict = await hedging.is_send_and_cancel_open_order_allowed(
                            notional,
                            best_ask_prc,
                            server_time,
                            market_condition,
                            THRESHOLD_TIME_TO_CANCEL,
                        )

                        await if_order_is_true(send_order, instrument)
                        await if_cancel_is_true(send_order)

                    if  "marketMaker" in strategy_attr["strategy"]:

                        market_maker = MM.MarketMaker(strategy_label)
                        

                        send_order: dict = await market_maker.is_send_and_cancel_open_order_allowed(
                            size_from_positions, notional, best_ask_prc, best_bid_prc, server_time, market_condition,take_profit_pct_daily
                        )
                                            
                        constraint= False if send_order["order_allowed"]==False\
                            else delta_price_constraint(THRESHOLD_BEFORE_REORDER, last_price_all, index_price, net_sum_strategy, send_order["order_parameters"]["side"])
            
                        if constraint:
                            
                            await if_order_is_true(send_order, instrument)
                            await if_cancel_is_true(send_order)
                            log.info(send_order)

                else:
                    log.critical(f" size_is_consistent {size_is_consistent} ")
                    # await telegram_bot_sendtext('size or open order is inconsistent', "general_error")

    except Exception as error:
        await raise_error(error)

    log.warning(f"OPENING TRANSACTIONS-DONE")


async def closing_transactions(
    label_transaction_net,
    portfolio,
    strategies,
    my_trades_open_sqlite,
    my_trades_open,
    size_from_positions,
    market_condition,
    currency,
) -> float:
    """ """

    log.critical(f"CLOSING TRANSACTIONS-START")

    my_trades_open_sqlite: dict = await sqlite_management.querying_table(
        "my_trades_all_json"
    )
    my_trades_open_all: list = my_trades_open_sqlite["all"]

    my_trades_open: list = my_trades_open_sqlite["list_data_only"]

    label_transaction_main = str_mod.remove_redundant_elements(
        [(str_mod.parsing_label(o))["main"] for o in label_transaction_net]
    )

    for label in label_transaction_main:
        log.debug(f"label {label}")

        my_trades_open_strategy = [
            o
            for o in my_trades_open
            if str_mod.parsing_label(o["label"])["main"] == label
        ]

        get_prices_in_label_transaction_main = [
            o["price"] for o in my_trades_open_strategy
        ]
        max_price = (
            0
            if get_prices_in_label_transaction_main == []
            else max(get_prices_in_label_transaction_main)
        )
        min_price = (
            0
            if get_prices_in_label_transaction_main == []
            else min(get_prices_in_label_transaction_main)
        )

        if "Short" in label or "hedging" in label:
            transaction = [
                o for o in my_trades_open_strategy if o["price"] == max_price
            ]
        if "Long" in label:
            transaction = [
                o for o in my_trades_open_strategy if o["price"] == min_price
            ]

        label = [
            str_mod.parsing_label(o["label"])["transaction_net"] for o in transaction
        ][0]

        # result example: 'hedgingSpot'/'supplyDemandShort60'
        label_main = str_mod.parsing_label(label)["main"]

        # get startegy details
        strategy_attr = [o for o in strategies if o["strategy"] == label_main][0]

        my_trades_open_sqlite_transaction_net_strategy: list = str_mod.my_trades_open_sqlite_detailing(
            my_trades_open_all, label, "transaction_net"
        )

        sum_my_trades_open_sqlite_all_strategy: list = str_mod.sum_my_trades_open_sqlite(
            my_trades_open_all, label
        )
        size_is_consistent: bool = await is_size_consistent(
            sum_my_trades_open_sqlite_all_strategy, size_from_positions
        )
        #: bool = await self.is_open_orders_consistent(open_orders_from_sub_account_get, open_orders_open_from_db)

        if size_is_consistent:  # and open_order_is_consistent:

            open_trade_strategy_label = str_mod.parsing_sqlite_json_output(
                [o["data"] for o in my_trades_open_sqlite_transaction_net_strategy]
            )

            instrument: list = [
                o["instrument_name"] for o in open_trade_strategy_label
            ][0]

            ticker: list = reading_from_db("ticker", instrument)

            if ticker != []:

                # index price
                index_price: float = ticker[0]["index_price"]

                # get instrument_attributes
                instrument_attributes_all: list = reading_from_db(
                    "instruments", currency
                )[0]["result"]
                instrument_attributes: list = [
                    o
                    for o in instrument_attributes_all
                    if o["instrument_name"] == instrument
                ]
                tick_size: float = instrument_attributes[0]["tick_size"]
                taker_commission: float = instrument_attributes[0]["taker_commission"]
                min_trade_amount: float = instrument_attributes[0]["min_trade_amount"]
                contract_size: float = instrument_attributes[0]["contract_size"]
                # log.error (f'tick_size A {tick_size} taker_commission {taker_commission} min_trade_amount {min_trade_amount} contract_size {contract_size}')

                # get bid and ask price
                best_bid_prc: float = ticker[0]["best_bid_price"]
                best_ask_prc: float = ticker[0]["best_ask_price"]

                # obtain spot equity
                equity: float = portfolio[0]["equity"]

                # compute notional value
                notional: float = compute_notional_value(index_price, equity)

                net_sum_strategy = str_mod.get_net_sum_strategy_super_main(
                    my_trades_open_sqlite, open_trade_strategy_label[0]["label"]
                )

                log.error(
                    f"sum_my_trades_open_sqlite_all_strategy {sum_my_trades_open_sqlite_all_strategy} net_sum_strategy {net_sum_strategy} "
                )

                if "hedgingSpot" in strategy_attr["strategy"]:

                    closest_price = num_mod.get_closest_value(
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
                        best_ask_prc,
                        best_bid_prc,
                        nearest_transaction_to_index,
                    )

                    await if_order_is_true(send_closing_order, instrument)

                if "marketMaker" in strategy_attr["strategy"]:

                    market_maker = MM.MarketMaker(label_main)

                    send_closing_order: dict = await market_maker.is_send_exit_order_allowed(
                        market_condition,best_ask_prc, best_bid_prc, open_trade_strategy_label
                    )
                    log.critical(f" send_closing_order {send_closing_order}")
                    await if_order_is_true(send_closing_order, instrument)

        else:
            log.critical(f" size_is_consistent {size_is_consistent} ")

    log.critical(f"CLOSING TRANSACTIONS-DONE")


async def current_server_time() -> float:
    """ """
    current_time = await deribit_get.get_server_time()
    return current_time["result"]
