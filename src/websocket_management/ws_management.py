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
from strategies import basic_strategy, hedging_spot, market_maker as MM
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
            error,
            "Capture market data - failed to fetch last open_interest",
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
            error,
            "Capture market data - failed to fetch last_tick_fr_sqlite",
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


def reading_from_db(end_point, instrument: str = None, status: str = None) -> float:
    """ """
    return system_tools.reading_from_db_pickle(end_point, instrument, status)


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

        is_app_running = system_tools.is_current_file_running("app")
        everything_consistent = basic_strategy.is_everything_consistent(params)

        if is_app_running and everything_consistent:
            await inserting_additional_params(params)
            await send_limit_order(params)
            await asyncio.sleep(10)

async def get_my_trades_from_exchange(count: int, currency) -> list:
    """
    """
    private_data = await get_private_data(currency)
    trades: list = await private_data.get_user_trades_by_currency(count)

    return [] if trades == [] else trades["result"]["trades"]


async def cancel_by_order_id(open_order_id) -> None:
    private_data = await get_private_data()

    result = await private_data.get_cancel_order_byOrderId(open_order_id)
    log.info(f"CANCEL_by_order_id {result}")

    return result


async def cancel_the_cancellables() -> None:
    from strategies import basic_strategy

    params: list = basic_strategy.get_strategy_config_all()
    cancellable_strategies: dict = [
        o["strategy"] for o in params if o["cancellable"] == True
    ]

    open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
        "orders_all_json"
    )
    # log.critical(f" open_orders_sqlite {open_orders_sqlite}")
    # log.critical(f" cancellable_strategies {cancellable_strategies}")
    for strategy in cancellable_strategies:
        open_orders_cancellables_id = [
            o["order_id"] for o in open_orders_sqlite if strategy in o["label"]
        ]
        # log.critical(f" open_orders_cancellables_id {strategy} {open_orders_cancellables_id}")

        if open_orders_cancellables_id != []:
            for open_order_id in open_orders_cancellables_id:

                await cancel_by_order_id(open_order_id)

                log.critical(f" deleting {open_order_id}")
                where_filter = f"order_id"
                await sqlite_management.deleting_row(
                    "orders_all_json",
                    "databases/trading.sqlite3",
                    where_filter,
                    "=",
                    open_order_id,
                )


async def if_cancel_is_true(order) -> None:
    """ """
    # log.debug (order)
    if order["cancel_allowed"]:

        # get parameter orders
        await cancel_by_order_id(order["cancel_id"])


async def resupply_sub_accountdb(currency) -> None:

    # resupply sub account db
    log.info(f"resupply sub account db-START")
    sub_accounts = await get_sub_account(currency)

    my_path_sub_account = system_tools.provide_path_for_file("sub_accounts", currency)
    pickling.replace_data(my_path_sub_account, sub_accounts)
    log.info(f"{sub_accounts}")
    log.info(f"resupply sub account db-DONE")


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

    log.info(
        f"buy_traded_price   {buy_traded_price} sell_traded_price   {sell_traded_price}"
    )
    log.debug([o["amount"] for o in my_trades_open_strategy_buy])

    log.error([o["amount"] for o in my_trades_open_strategy_sell])

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

    log.debug(
        f"constraint   {is_reorder_ok} last_traded_price   {last_traded_price}  market_price   {market_price} side   {side}"
    )
    return True if last_traded_price == 0 else is_reorder_ok


async def opening_transactions(
    instrument,
    portfolio,
    strategies,
    my_trades_open_sqlite,
    size_from_positions,
    server_time,
    market_condition,
    take_profit_pct_daily,
) -> None:
    """ """

    log.warning(f"OPENING TRANSACTIONS-START")

    try:
        my_trades_open_all: list = my_trades_open_sqlite["all"]

        transactions_all_summarized: list = await basic_strategy.querying_label_and_size("my_trades_all_json")
        
        log.error (my_trades_open_sqlite)
        log.warning (my_trades_open_all)
        log.info (transactions_all_summarized)

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

                THRESHOLD_BEFORE_REORDER = ONE_PCT / 2

                my_trades_open = [
                    o for o in transactions_all_summarized if "open" in (o["label"])
                ]

                my_trades_open_strategy = [
                    o for o in my_trades_open if strategy_label in (o["label"])
                ]

                last_price_all = get_last_price(my_trades_open_strategy)

                log.debug(f"last_price   {last_price_all}")

                if "hedgingSpot" in strategy_attr["strategy"]:

                    THRESHOLD_TIME_TO_CANCEL = 3

                    hedging = hedging_spot.HedgingSpot(strategy_label)

                    send_order: dict = (
                        await hedging.is_send_and_cancel_open_order_allowed(
                            notional,
                            best_ask_prc,
                            server_time,
                            market_condition,
                            THRESHOLD_TIME_TO_CANCEL,
                        )
                    )

                    await if_order_is_true(send_order, instrument)
                    await if_cancel_is_true(send_order)

                if "marketMaker" in strategy_attr["strategy"]:

                    market_maker = MM.MarketMaker(strategy_label)

                    send_order: dict = (
                        await market_maker.is_send_and_cancel_open_order_allowed(
                            size_from_positions,
                            notional,
                            best_ask_prc,
                            best_bid_prc,
                            server_time,
                            market_condition,
                            take_profit_pct_daily,
                        )
                    )

                    constraint = (
                        False
                        if send_order["order_allowed"] == False
                        else delta_price_constraint(
                            THRESHOLD_BEFORE_REORDER,
                            last_price_all,
                            index_price,
                            net_sum_strategy,
                            send_order["order_parameters"]["side"],
                        )
                    )

                    if constraint:

                        await if_order_is_true(send_order, instrument)
                        await if_cancel_is_true(send_order)
                        log.info(send_order)

    except Exception as error:
        await raise_error(error)

    log.warning(f"OPENING TRANSACTIONS-DONE")

def get_label_transaction_main(label_transaction_net: list) -> list:
    """ """
    
    return str_mod.remove_redundant_elements(
        [(str_mod.parsing_label(o))["main"] for o in label_transaction_net]
    )

def get_trades_within_respective_strategy(my_trades_open: list, label: str) -> list:
    """ """
    
    return [
            o
            for o in my_trades_open
            if str_mod.parsing_label(o["label"])["main"] == label
        ]

def get_min_max_price_from_transaction_in_strategy(get_prices_in_label_transaction_main: list) -> list:
    """ """
    return dict(
            max_price=(0 if get_prices_in_label_transaction_main == []
            else max(get_prices_in_label_transaction_main)
            ),
            min_price=(0 if get_prices_in_label_transaction_main == []
            else min(get_prices_in_label_transaction_main))
            )

async def closing_transactions(
    label_transaction_net,
    portfolio,
    strategies,
    my_trades_open_sqlite,
    my_trades_open,
    market_condition,
    currency,
) -> float:
    """ """

    log.critical(f"CLOSING TRANSACTIONS-START")

    my_trades_open_all: list = my_trades_open_sqlite["all"]

    my_trades_open: list = my_trades_open_sqlite["list_data_only"]
    transactions_all_summarized: list = await basic_strategy.querying_label_and_size("my_trades_all_json")
    #log.error(f"my_trades_open {my_trades_open}")
    #log.error(f"transactions_all_summarized {transactions_all_summarized}")

    label_transaction_main = get_label_transaction_main(label_transaction_net)

    log.error(f"label_transaction_main {label_transaction_main}")

    for label in label_transaction_main:
        log.debug(f"label {label}")

        my_trades_open_strategy = get_trades_within_respective_strategy(my_trades_open,label)

        get_prices_in_label_transaction_main = [
            o["price"] for o in my_trades_open_strategy
        ]
        max_price = get_min_max_price_from_transaction_in_strategy(
            get_prices_in_label_transaction_main)["max_price"]
        
        min_price = get_min_max_price_from_transaction_in_strategy(
            get_prices_in_label_transaction_main)["min_price"]

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

        my_trades_open_sqlite_transaction_net_strategy: list = (
            str_mod.my_trades_open_sqlite_detailing(
                my_trades_open_all, label, "transaction_net"
            )
        )

        sum_my_trades_open_sqlite_all_strategy: list = (
            str_mod.sum_my_trades_open_sqlite(my_trades_open_all, label)
        )

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

                send_closing_order: dict = (
                    await market_maker.is_send_exit_order_allowed(
                        market_condition,
                        best_ask_prc,
                        best_bid_prc,
                        open_trade_strategy_label,
                    )
                )
                log.critical(f" send_closing_order {send_closing_order}")
                await if_order_is_true(send_closing_order, instrument)

    log.critical(f"CLOSING TRANSACTIONS-DONE")

