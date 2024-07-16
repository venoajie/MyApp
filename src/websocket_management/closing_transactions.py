# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from loguru import logger as log

from websocket_management.ws_management import reading_from_db, if_order_is_true

from utilities.string_modification import (
    remove_redundant_elements,
    parsing_label,
    my_trades_open_sqlite_detailing,
    parsing_sqlite_json_output,
)

from utilities.number_modification import get_closest_value

# from market_understanding import futures_analysis
from strategies import hedging_spot, market_maker as MM


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


async def closing_outstanding_transactions(
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

    label_transaction_main = get_label_transaction_main(label_transaction_net)

    for label in label_transaction_main:
        log.debug(f"label {label}")

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
            # get bid and ask price
            best_bid_prc: float = ticker[0]["best_bid_price"]
            best_ask_prc: float = ticker[0]["best_ask_price"]

            if "hedgingSpot" in strategy_attr["strategy"]:

                closest_price = get_closest_value(
                    get_prices_in_label_transaction_main, best_bid_prc
                )

                if "hedging" in label:
                    nearest_transaction_to_index = [
                        o
                        for o in my_trades_open_strategy
                        if o["price"] == closest_price
                    ]

                hedging = hedging_spot.HedgingSpot(label_main)

                send_closing_order: dict = await hedging.is_send_exit_order_allowed(
                    market_condition,
                    best_ask_prc,
                    best_bid_prc,
                    nearest_transaction_to_index,
                )

                # await if_order_is_true(send_closing_order, instrument)

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
                # await if_order_is_true(send_closing_order, instrument)

    log.critical(f"CLOSING TRANSACTIONS-DONE")
