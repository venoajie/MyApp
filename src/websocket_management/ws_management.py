# -*- coding: utf-8 -*-

# built ins
import asyncio
import functools

# installed
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools, string_modification as str_mod
from market_understanding import futures_analysis
from db_management import sqlite_management
from strategies import entries_exits, basic_strategy
from websocket_management.entries_and_exit_management import (
    opening_transactions,
    closing_transactions,
    reading_from_pkl_database,
    count_and_delete_ohlc_rows,
    current_server_time,
    clean_up_closed_transactions,
    get_account_balances_and_transactions_from_exchanges,
)


#  parameterless decorator
def  async_lru_cache_decorator(async_function):
     @functools.lru_cache
     def  cached_async_function(*args, **kwargs):
         coroutine = async_function(*args,  **kwargs)
         return  asyncio.ensure_future(coroutine)
     return cached_async_function

#  decorator with options
def  async_lru_cache(*lru_cache_args,  **lru_cache_kwargs):
    def  async_lru_cache_decorator(async_function):
        @functools.lru_cache(*lru_cache_args,  **lru_cache_kwargs)
        def  cached_async_function(*args, **kwargs):
            coroutine =  async_function(*args, **kwargs)
            return  asyncio.ensure_future(coroutine)
        return cached_async_function
    return  async_lru_cache_decorator

async def raise_error(error, idle: int = None) -> None:
    """ """
    await system_tools.raise_error_message(error, idle)


async def update_portfolio(data_orders, currency) -> None:

    my_path_portfolio = system_tools.provide_path_for_file("portfolio", currency)
    pickling.replace_data(my_path_portfolio, data_orders)


async def resupply_sub_accountdb(currency) -> None:

    # resupply sub account db
    log.info(f"resupply sub account db-START")
    account_balances_and_transactions_from_exchanges = await get_account_balances_and_transactions_from_exchanges(
        currency
    )
    sub_accounts = account_balances_and_transactions_from_exchanges["sub_account"]

    my_path_sub_account = system_tools.provide_path_for_file("sub_accounts", currency)
    pickling.replace_data(my_path_sub_account, sub_accounts)
    log.info(f"{sub_accounts}")
    log.info(f"resupply sub account db-DONE")


async def update_user_changes(data_orders, currency) -> None:

    from transaction_management.deribit import myTrades_management

    positions = data_orders["positions"]
    trades = data_orders["trades"]
    orders = data_orders["orders"]

    my_trades_open_sqlite: dict = await sqlite_management.querying_table(
        "my_trades_all_json"
    )
    my_trades_open_all: list = my_trades_open_sqlite["all"]
    if trades:
        for trade in trades:

            log.info(f"trade {trade}")
            my_trades = myTrades_management.MyTrades(trade)

            await sqlite_management.insert_tables("my_trades_all_json", trade)
            my_trades.distribute_trade_transactions(currency)

        clean_up_transactions: list = await clean_up_closed_transactions(
            my_trades_open_all
        )
        log.error(f"clean_up_closed_transactions {clean_up_transactions}")

    if orders:
        # my_orders = open_orders_management.MyOrders(orders)
        log.debug(f"my_orders {orders}")

        for order in orders:

            #! ##############################################################################

            open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
                "orders_all_json"
            )
            len_open_orders_sqlite_list_data = len([o for o in open_orders_sqlite])
            log.warning(
                f" order sqlite BEFORE {len_open_orders_sqlite_list_data} {open_orders_sqlite}"
            )

            #! ##############################################################################

            log.warning(f"order {order}")
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

                #! EXAMPLES of order id state
                # untriggered: insert
                # {'web': False, 'triggered': False, 'trigger_price': 1874.0, 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'take_limit', 'order_state': 'untriggered', 'order_id': 'ETH-TPTB-5703081', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768062826, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768062826, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}

                # triggered: cancel untrigger, insert trigger
                # {'web': False, 'triggered': True, 'trigger_price': 1874.0, 'trigger_order_id': 'ETH-TPTB-5703081', 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'stop_order_id': 'ETH-TPTB-5703081', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'take_limit', 'order_state': 'triggered', 'order_id': 'ETH-TPTB-5703081', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768062826, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768062826, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}], 'instrument_name': 'ETH-PERPETUAL'}

                # open: cancel trigger insert open
                # {'web': False, 'triggered': True, 'trigger_price': 1874.0, 'trigger_order_id': 'ETH-TPTB-5703081', 'trigger_offset': None, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1874.0, 'stop_order_id': 'ETH-TPTB-5703081', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1860.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-32754477205', 'mmp': False, 'max_show': 1.0, 'last_update_timestamp': 1680768064536, 'label': 'test-123', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1680768064536, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 1.0}], 'instrument_name': 'ETH-PERPETUAL'}

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

        #! ###########################################################

        clean_up_transactions: list = await clean_up_closed_transactions(
            my_trades_open_all
        )
        log.error(f"clean_up_closed_transactions {clean_up_transactions}")

    if positions:
        # log.error (f'positions {positions}')

        my_path_position = system_tools.provide_path_for_file("positions", currency)
        pickling.replace_data(my_path_position, positions)


async def ws_manager_exchange(message_channel, data_orders, currency) -> None:

    if message_channel == f"user.portfolio.{currency.lower()}":

        await update_portfolio(data_orders, currency)

        await resupply_sub_accountdb(currency)

    if message_channel == f"user.changes.any.{currency.upper()}.raw":

        await update_user_changes(data_orders, currency)

        await resupply_sub_accountdb(currency)


@async_lru_cache(ttl=100)
async def market_condition(threshold,limit, ratio) -> None:
    await basic_strategy.get_market_condition(
        threshold, limit, ratio
    )


async def ws_manager_market(
    message_channel, data_orders, instruments_kind, currency, private_data
) -> None:

    DATABASE: str = "databases/trading.sqlite3"
    TABLE_OHLC1: str = "ohlc1_eth_perp_json"
    TABLE_OHLC30: str = "ohlc30_eth_perp_json"
    TABLE_OHLC60: str = "ohlc60_eth_perp_json"
    TABLE_OHLC1D: str = "ohlc1D_eth_perp_json"
    WHERE_FILTER_TICK: str = "tick"

    last_tick_query_ohlc1: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC1
    )

    last_tick_query_ohlc30: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC30
    )
    last_tick_query_ohlc60: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC60
    )

    last_tick_query_ohlc1D: str = sqlite_management.querying_arithmetic_operator(
        "tick", "MAX", TABLE_OHLC1D
    )

    last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(last_tick_query_ohlc1)

    # gathering basic data
    reading_from_database: dict = await reading_from_pkl_database(currency)

    # get portfolio data
    portfolio: list = reading_from_database["portfolio"]

    # fetch strategies attributes
    strategies = entries_exits.strategies

    limit = 100
    ratio = 0.9
    threshold = 0.01 / 100

    market_condition = await basic_strategy.get_market_condition(
        threshold, limit, ratio
    )
    
    market_condition_lru= market_condition(threshold, limit, ratio)
    log.error(f"market_condition {market_condition} {market_condition_lru}")

    if "chart.trades.ETH-PERPETUAL." in message_channel:

        last_tick_fr_data_orders: int = data_orders["tick"]

        if (
            TABLE_OHLC30 != None
            or TABLE_OHLC1 != None
            or TABLE_OHLC60 != None
            or TABLE_OHLC1 != None
        ):

            if message_channel == "chart.trades.ETH-PERPETUAL.1":
                log.error(message_channel)

                # refilling current ohlc table with updated data
                if last_tick1_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.replace_row(
                        data_orders,
                        "data",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

                # new tick ohlc
                else:
                    # prepare query
                    open_interest_last_value_query = sqlite_management.querying_last_open_interest(
                        last_tick1_fr_sqlite, TABLE_OHLC1
                    )

                    # get current oi
                    open_interest_last_value = await last_open_interest_fr_sqlite(
                        open_interest_last_value_query
                    )

                    # insert new ohlc data
                    await sqlite_management.insert_tables(TABLE_OHLC1, data_orders)

                    # update last tick
                    last_tick1_fr_sqlite = await last_tick_fr_sqlite(
                        last_tick_query_ohlc1
                    )

                    # insert open interest in previous tick to the new tick
                    await sqlite_management.replace_row(
                        open_interest_last_value,
                        "open_interest",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

                # capping sqlite rows
                await count_and_delete_ohlc_rows()

                # to avoid error if index price/portfolio = []/None
                if portfolio:

                    # fetch positions for all instruments
                    positions_all: list = reading_from_database[
                        "positions_from_sub_account"
                    ]
                    size_from_positions: float = 0 if positions_all == [] else sum(
                        [o["size"] for o in positions_all]
                    )

                    my_trades_open_sqlite: dict = await sqlite_management.querying_table(
                        "my_trades_all_json"
                    )
                    my_trades_open: list = my_trades_open_sqlite["list_data_only"]

                    instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
                    server_time = await current_server_time()

                    for instrument in instrument_transactions:
                        await opening_transactions(
                            instrument,
                            portfolio,
                            strategies,
                            my_trades_open_sqlite,
                            size_from_positions,
                            server_time,
                            market_condition,
                        )

            if message_channel == "chart.trades.ETH-PERPETUAL.30":

                last_tick30_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc30
                )

                if last_tick30_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC30,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick30_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC30, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC30, data_orders)

            if message_channel == "chart.trades.ETH-PERPETUAL.60":

                last_tick60_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc60
                )

                if last_tick60_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC60,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick60_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC60, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC60, data_orders)

            if message_channel == "chart.trades.ETH-PERPETUAL.1D":

                last_tick1D_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc1D
                )

                if last_tick1D_fr_sqlite == last_tick_fr_data_orders:

                    await sqlite_management.deleting_row(
                        TABLE_OHLC1D,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick1D_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(TABLE_OHLC1D, data_orders)

                else:
                    await sqlite_management.insert_tables(TABLE_OHLC1D, data_orders)

    instrument_ticker = (message_channel)[19:]
    if message_channel == f"incremental_ticker.{instrument_ticker}":
        # log.warning (message_channel)
        my_path_futures_analysis = system_tools.provide_path_for_file(
            "futures_analysis", currency
        )

        my_path_ticker = system_tools.provide_path_for_file("ticker", instrument_ticker)

        try:

            if "PERPETUAL" in data_orders["instrument_name"]:
                # log.info(data_orders)

                if "open_interest" in data_orders:

                    open_interest = data_orders["open_interest"]

                    await sqlite_management.replace_row(
                        open_interest,
                        "open_interest",
                        TABLE_OHLC1,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "is",
                        last_tick1_fr_sqlite,
                    )

            await distribute_ticker_result_as_per_data_type(
                my_path_ticker, data_orders, instrument_ticker
            )

            symbol_index: str = f"{currency}_usd"
            my_path_index: str = system_tools.provide_path_for_file(
                "index", symbol_index
            )
            index_price: list = pickling.read_data(my_path_index)
            ticker_instrument: list = pickling.read_data(my_path_ticker)
            if ticker_instrument != []:
                # log.error(ticker_instrument)
                instrument_name = ticker_instrument[0]["instrument_name"]
                instrument: list = [
                    o
                    for o in instruments_kind
                    if o["instrument_name"] == instrument_name
                ][0]

                # combine analysis of each instrument futures result
                tickers = futures_analysis.combining_individual_futures_analysis(
                    index_price[0]["price"], instrument, ticker_instrument[0],
                )
                ticker_all: list = pickling.read_data(my_path_futures_analysis)

                if ticker_all == None:
                    pickling.replace_data(my_path_futures_analysis, ticker_all)
                else:
                    ticker_all: list = [
                        o
                        for o in ticker_all
                        if o["instrument_name"] != instrument_ticker
                    ]

                    #! double file operation. could be further improved
                    pickling.replace_data(my_path_futures_analysis, ticker_all)

                    pickling.append_and_replace_items_based_on_qty(
                        my_path_futures_analysis, tickers, 100
                    )

                if portfolio:

                    # fetch positions for all instruments
                    positions_all: list = reading_from_database[
                        "positions_from_sub_account"
                    ]
                    size_from_positions: float = 0 if positions_all == [] else sum(
                        [o["size"] for o in positions_all]
                    )

                    my_trades_open_sqlite: dict = await sqlite_management.querying_table(
                        "my_trades_all_json"
                    )
                    my_trades_open: list = my_trades_open_sqlite["list_data_only"]

                    # clean up transactions all
                    my_trades_open = [o for o in my_trades_open if "label" in o]

                    my_trades_open_remove_closed_labels = (
                        []
                        if my_trades_open == []
                        else [o for o in my_trades_open if "closed" not in o["label"]]
                    )
                    label_transaction_net = (
                        []
                        if my_trades_open_remove_closed_labels == []
                        else str_mod.remove_redundant_elements(
                            [
                                str_mod.parsing_label(o["label"])["transaction_net"]
                                for o in my_trades_open_remove_closed_labels
                            ]
                        )
                    )

                    await closing_transactions(
                        label_transaction_net,
                        portfolio,
                        strategies,
                        my_trades_open_sqlite,
                        my_trades_open,
                        size_from_positions,
                        market_condition,
                        currency,
                    )

        except Exception as error:
            log.error(error)
            await system_tools.raise_error_message(
                "WebSocket management - failed to process data"
            )


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
