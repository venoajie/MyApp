# -*- coding: utf-8 -*-

# built ins
import asyncio
import json

# installed
from loguru import logger as log

# user defined formula
from utilities import pickling, system_tools, string_modification as str_mod
from market_understanding import futures_analysis
from db_management import sqlite_management
from strategies import entries_exits, hedging_spot, basic_strategy, market_maker as MM
import deribit_get
from configuration import  config

ONE_MINUTE: int = 60000
ONE_PCT: float = 1 / 100
NONE_DATA: None = [0, None, []]

def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)

sub_account = "deribit-147691"
client_id: str = parse_dotenv(sub_account)["client_id"]
client_secret: str = parse_dotenv(sub_account)["client_secret"]
connection_url: str="https://www.deribit.com/api/v2/"

async def raise_error(error, idle: int = None) -> None:
    """ """
    await system_tools.raise_error_message(error, idle)
    
async def get_private_data(connection_url, client_id, client_secret, currency) -> list:
    """
    Provide class object to access private get API
    """
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

    path_portfolio: str = system_tools.provide_path_for_file(
        "portfolio", currency
    )
    path_positions: str = system_tools.provide_path_for_file(
        "positions", currency
    )
    positions = pickling.read_data(path_positions)
    sub_account = pickling.read_data(path_sub_accounts)
    # log.critical(f' SUB ACCOUNT {sub_account}')
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

async def is_size_consistent(sum_my_trades_open_sqlite_all_strategy, size_from_positions
) -> bool:
    """ """

    log.warning(
        f" size_from_sqlite {sum_my_trades_open_sqlite_all_strategy} size_from_positions {size_from_positions}"
    )

    return sum_my_trades_open_sqlite_all_strategy == size_from_positions


def reading_from_db(end_point, instrument: str = None, status: str = None
) -> float:
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
    my_trades_open_all,
    size_from_positions,
    server_time,
    market_condition,
) -> None:
    """ """

    try:
        log.critical(f"OPENING TRANSACTIONS")

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

                        THRESHOLD_TIME_TO_CANCEL = 30

                        hedging = hedging_spot.HedgingSpot(strategy_label)

                        send_order: dict = await hedging.is_send_and_cancel_open_order_allowed(
                            notional,
                            best_ask_prc,
                            server_time,
                            market_condition,
                            THRESHOLD_TIME_TO_CANCEL,
                        )

                        # await self.if_order_is_true(send_order, instrument)
                        # await self.if_cancel_is_true(send_order)

                    if "marketMaker" in strategy_attr["strategy"]:

                        market_maker = MM.MarketMaker(strategy_label)

                        send_order: dict = await market_maker.is_send_and_cancel_open_order_allowed(
                            notional, best_ask_prc, best_bid_prc, server_time
                        )

                        await if_order_is_true(send_order, instrument)
                        await if_cancel_is_true(send_order)

                else:
                    log.critical(f" size_is_consistent {size_is_consistent} ")
                    # await telegram_bot_sendtext('size or open order is inconsistent', "general_error")
                    await system_tools.sleep_and_restart(5)

    except Exception as error:
        await raise_error(error)
    
async def current_server_time() -> float:
    """ """
    current_time = await deribit_get.get_server_time()
    return current_time["result"]
    
    
async def get_account_balances_and_transactions_from_exchanges(currency) -> list:
    """ """

    try:
        private_data = await get_private_data(connection_url, client_id, client_secret, currency)
        result_sub_account: dict = await private_data.get_subaccounts()
        result_open_orders: dict = await private_data.get_open_orders_byCurrency()
        result_account_summary: dict = await private_data.get_account_summary()
        result_get_positions: dict = await private_data.get_positions()

    except Exception as error:
        await raise_error(error)

    return dict(
        sub_account=result_sub_account["result"],
        open_orders=result_open_orders["result"],
        account_summary=result_account_summary["result"],
        get_positions=result_get_positions["result"]
    )
async def ws_manager_exchange(message_channel, data_orders, currency) -> None:
    
    from transaction_management.deribit import myTrades_management

        
    if message_channel == f"user.portfolio.{currency.lower()}":
        my_path_portfolio = system_tools.provide_path_for_file(
            "portfolio", currency
        )
        pickling.replace_data(my_path_portfolio, data_orders)

    if (
        message_channel
        == f"user.changes.any.{currency.upper()}.raw"
    ):
        # log.info(data_orders)
        positions = data_orders["positions"]
        trades = data_orders["trades"]
        orders = data_orders["orders"]
        # private_data = await self.get_private_data(currency)
        # result_open_orders: dict =  await private_data.get_open_orders_byCurrency()
        # log.error (result_open_orders)
        #! ###########################################################

        # open_trades_sqlite = await sqlite_management.executing_label_and_size_query ('my_trades_all_json')
        # len_open_trades_sqlite = len([o  for o in open_trades_sqlite])
        # log.debug (f' trade sqlite BEFORE {len_open_trades_sqlite}')
        #! ###########################################################

        if trades:
            for trade in trades:

                log.info(f"trade {trade}")
                my_trades = myTrades_management.MyTrades(trade)

                await sqlite_management.insert_tables(
                    "my_trades_all_json", trade
                )
                my_trades.distribute_trade_transactions(currency)

                # my_trades_path_all = system_tools.provide_path_for_file(
                # "my_trades", currency, "all"
            # )
            #    self. appending_data (trade, my_trades_path_all)

        if orders:
            # my_orders = open_orders_management.MyOrders(orders)
            log.debug(f"my_orders {orders}")

            for order in orders:

                #! ##############################################################################

                open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
                    "orders_all_json"
                )
                len_open_orders_sqlite_list_data = len(
                    [o for o in open_orders_sqlite]
                )
                log.warning(
                    f" order sqlite BEFORE {len_open_orders_sqlite_list_data} {open_orders_sqlite}"
                )

                sub_acc = (
                    await syn.get_account_balances_and_transactions_from_exchanges()
                )
                sub_acc_orders = sub_acc["open_orders"]
                log.error(
                    f" sub_acc BEFORE {len(sub_acc_orders)} {sub_acc_orders} "
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
                        o
                        for o in open_orders_sqlite
                        if o["order_id"] == order_id
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

                    await sqlite_management.insert_tables(
                        "orders_all_json", order
                    )

                    # orders_path_all = system_tools.provide_path_for_file(
                    # orders", currency, "all")

                    # self. appending_data (order, orders_path_all)

                    # my_orders.distribute_order_transactions(currency)

                #! ###########################################################
                open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
                    "orders_all_json"
                )
                len_open_orders_sqlite_list_data = len(
                    [o for o in open_orders_sqlite]
                )
                log.critical(
                    f" order sqlite AFTER {len_open_orders_sqlite_list_data} {open_orders_sqlite}"
                )

                sub_acc = (
                    await syn.get_account_balances_and_transactions_from_exchanges()
                )
                sub_acc_orders = sub_acc["open_orders"]
                log.error(
                    f" sub_acc AFTER {len(sub_acc_orders)} {sub_acc_orders} "
                )

        # open_trades_sqlite = await sqlite_management.executing_label_and_size_query ('my_trades_all_json')
        # len_open_trades_sqlite = len([o  for o in open_trades_sqlite])
        # log.debug (f' trade sqlite AFTER {len_open_trades_sqlite} ')
        #! ###########################################################

        if positions:
            # log.error (f'positions {positions}')

            my_path_position = system_tools.provide_path_for_file(
                "positions", currency
            )
            pickling.replace_data(my_path_position, positions)

async def ws_manager_market(message_channel, data_orders, instruments_kind, currency, private_data) -> None:

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

    last_tick1_fr_sqlite: int = await last_tick_fr_sqlite(
        last_tick_query_ohlc1
    )

    if "chart.trades.ETH-PERPETUAL." in message_channel:

        last_tick_fr_data_orders: int = data_orders["tick"]

        if (
            TABLE_OHLC30 != None
            or TABLE_OHLC1 != None
            or TABLE_OHLC60 != None
            or TABLE_OHLC1 != None
        ):

            if (
                message_channel
                == "chart.trades.ETH-PERPETUAL.1"
            ):
                log.error (message_channel)

                # refilling current ohlc table with updated data
                if (
                    last_tick1_fr_sqlite
                    == last_tick_fr_data_orders
                ):

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
                    await sqlite_management.insert_tables(
                        TABLE_OHLC1, data_orders
                    )

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
                
            if (
                message_channel
                == "chart.trades.ETH-PERPETUAL.30"
            ):

                last_tick30_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc30
                )

                if (
                    last_tick30_fr_sqlite
                    == last_tick_fr_data_orders
                ):

                    await sqlite_management.deleting_row(
                        TABLE_OHLC30,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick30_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(
                        TABLE_OHLC30, data_orders
                    )

                else:
                    await sqlite_management.insert_tables(
                        TABLE_OHLC30, data_orders
                    )

            if (
                message_channel
                == "chart.trades.ETH-PERPETUAL.60"
            ):

                last_tick60_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc60
                )

                if (
                    last_tick60_fr_sqlite
                    == last_tick_fr_data_orders
                ):

                    await sqlite_management.deleting_row(
                        TABLE_OHLC60,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick60_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(
                        TABLE_OHLC60, data_orders
                    )

                else:
                    await sqlite_management.insert_tables(
                        TABLE_OHLC60, data_orders
                    )

            if (
                message_channel
                == "chart.trades.ETH-PERPETUAL.1D"
            ):

                last_tick1D_fr_sqlite = await last_tick_fr_sqlite(
                    last_tick_query_ohlc1D
                )

                if (
                    last_tick1D_fr_sqlite
                    == last_tick_fr_data_orders
                ):

                    await sqlite_management.deleting_row(
                        TABLE_OHLC1D,
                        DATABASE,
                        WHERE_FILTER_TICK,
                        "=",
                        last_tick1D_fr_sqlite,
                    )

                    await sqlite_management.insert_tables(
                        TABLE_OHLC1D, data_orders
                    )

                else:
                    await sqlite_management.insert_tables(
                        TABLE_OHLC1D, data_orders
                    )


        # gathering basic data
        reading_from_database: dict = await reading_from_pkl_database(currency)

        # get portfolio data
        portfolio: list = reading_from_database["portfolio"]

        # fetch strategies attributes
        strategies = entries_exits.strategies

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
            my_trades_open_all: list = await sqlite_management.executing_label_and_size_query(
                "my_trades_all_json"
            )
            instrument_transactions = [f"{currency.upper()}-PERPETUAL"]
            server_time= current_server_time()

            limit = 100
            ratio = 0.9
            threshold = 0.01 / 100

            sub_acc = (
                await get_account_balances_and_transactions_from_exchanges(currency)
            )

            market_condition = await basic_strategy.get_market_condition(
                threshold, limit, ratio
            )
            log.error(f"market_condition {market_condition}")

            for instrument in instrument_transactions:
                await opening_transactions(
            instrument,
            portfolio,
            strategies,
            my_trades_open_sqlite,
            my_trades_open_all,
            size_from_positions,
            server_time,
            market_condition,
        )    


    instrument_ticker = (message_channel)[19:]
    if (
        message_channel
        == f"incremental_ticker.{instrument_ticker}"
    ):
        #log.warning (message_channel)
        my_path_futures_analysis = system_tools.provide_path_for_file(
            "futures_analysis", currency
        )

        my_path_ticker = system_tools.provide_path_for_file(
            "ticker", instrument_ticker
        )

        try:

            if "PERPETUAL" in data_orders["instrument_name"]:
                #log.info(data_orders)

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
            index_price: list = pickling.read_data(
                my_path_index
            )
            ticker_instrument: list = pickling.read_data(
                my_path_ticker
            )
            if ticker_instrument != []:
                # log.error(ticker_instrument)
                instrument_name = ticker_instrument[0][
                    "instrument_name"
                ]
                instrument: list = [
                    o
                    for o in instruments_kind
                    if o["instrument_name"] == instrument_name
                ][0]

                # combine analysis of each instrument futures result
                tickers = futures_analysis.combining_individual_futures_analysis(
                    index_price[0]["price"],
                    instrument,
                    ticker_instrument[0],
                )
                ticker_all: list = pickling.read_data(
                    my_path_futures_analysis
                )

                if ticker_all == None:
                    pickling.replace_data(
                        my_path_futures_analysis, ticker_all
                    )
                else:
                    ticker_all: list = [
                        o
                        for o in ticker_all
                        if o["instrument_name"]
                        != instrument_ticker
                    ]

                    #! double file operation. could be further improved
                    pickling.replace_data(
                        my_path_futures_analysis, ticker_all
                    )

                    pickling.append_and_replace_items_based_on_qty(
                        my_path_futures_analysis, tickers, 100
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
