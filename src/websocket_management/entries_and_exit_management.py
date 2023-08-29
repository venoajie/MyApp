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
from strategies import hedging_spot, market_maker as MM
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


async def send_limit_order(params) -> None:
    """ """
    private_data = await get_private_data()
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


async def opening_transactions(
    instrument,
    portfolio,
    strategies,
    my_trades_open_sqlite,
    size_from_positions,
    server_time,
    market_condition,
) -> None:
    """ """

    log.warning(f"OPENING TRANSACTIONS-START")

    try:

        my_trades_open_sqlite: dict = await sqlite_management.querying_table(
            "my_trades_all_json"
        )
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

                    if "marketMaker" in strategy_attr["strategy"]:

                        market_maker = MM.MarketMaker(strategy_label)

                        send_order: dict = await market_maker.is_send_and_cancel_open_order_allowed(
                            notional, best_ask_prc, best_bid_prc, server_time
                        )

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

                    log.critical(
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
                        best_ask_prc, best_bid_prc, open_trade_strategy_label
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
