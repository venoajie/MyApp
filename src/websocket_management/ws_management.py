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
    current_server_time,
    get_account_balances_and_transactions_from_exchanges,
)
from websocket_management.cleaning_up_transactions import (
    count_and_delete_ohlc_rows,
    clean_up_closed_transactions,
)

#  parameterless decorator
def async_lru_cache_decorator(async_function):
    # https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live
    # https://www.anycodings.com/questions/how-to-cache-asyncio-coroutines
    @functools.lru_cache
    def cached_async_function(ttl_hash=None, *args, **kwargs):
        coroutine = async_function(*args, **kwargs)
        return asyncio.ensure_future(coroutine)

    return cached_async_function


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    import time

    return round(time.time() / seconds)


#  decorator with options
def async_lru_cache(*lru_cache_args, **lru_cache_kwargs):
    def async_lru_cache_decorator(async_function):
        @functools.lru_cache(*lru_cache_args, **lru_cache_kwargs)
        def cached_async_function(*args, **kwargs):
            coroutine = async_function(*args, **kwargs)
            return asyncio.ensure_future(coroutine)

        return cached_async_function

    return async_lru_cache_decorator


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


@async_lru_cache(maxsize=128)
async def market_condition_cache(
    threshold, limit, ratio, ttl_hash=get_ttl_hash()
) -> None:
    market = await basic_strategy.get_market_condition(threshold, limit, ratio)
    return market



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
