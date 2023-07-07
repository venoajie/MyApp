#!/usr/bin/python3


# built ins
import asyncio

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
import deribit_get
from utilities import system_tools
from strategies import hedging_spot, market_maker as MM, basic_strategy

ONE_MINUTE: int = 60000
ONE_PCT: float = 1 / 100
NONE_DATA: None = [0, None, []]


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)


async def raise_error(error, idle: int = None) -> None:
    """ """
    await system_tools.raise_error_message(error, idle)


async def opening_transactions(
    instrument, portfolio, strategies, server_time,
) -> None:
    """ """

    try:
        log.critical(f"OPENING TRANSACTIONS")

        my_trades_open_sqlite: dict = await self.querying_all("my_trades_all_json")
        # log.error (my_trades_open_all)

        ticker: list = basic_strategy.reading_from_db("ticker", instrument)

        if ticker != []:

            # get bid and ask price
            best_bid_prc: float = ticker[0]["best_bid_price"]
            best_ask_prc: float = ticker[0]["best_ask_price"]

            # index price
            index_price: float = ticker[0]["index_price"]

            # obtain spot equity
            equity: float = portfolio[0]["equity"]

            # compute notional value
            notional: float = await self.compute_notional_value(index_price, equity)

            # execute each strategy
            for strategy_attr in strategies:
                strategy_label = strategy_attr["strategy"]

                log.critical(f" {strategy_label}")

                net_sum_strategy = await self.get_net_sum_strategy_super_main(
                    my_trades_open_sqlite, strategy_label
                )
                net_sum_strategy_main = await self.get_net_sum_strategy_main(
                    my_trades_open_sqlite, strategy_label
                )
                log.debug(
                    f"net_sum_strategy   {net_sum_strategy} net_sum_strategy_main   {net_sum_strategy_main}"
                )

                if "hedgingSpot" in strategy_attr["strategy"]:

                    THRESHOLD_TIME = 30

                    hedging = hedging_spot.HedgingSpot(strategy_label)

                    send_order: dict = await hedging.is_send_and_cancel_open_order_allowed(
                        notional, best_ask_prc, server_time, THRESHOLD_TIME
                    )

                    await self.if_order_is_true(send_order, instrument)
                    await self.if_cancel_is_true(send_order)

                if "marketMaker" in strategy_attr["strategy"]:

                    market_maker = MM.MarketMaker(strategy_label)

                    send_order: dict = await market_maker.is_send_and_cancel_open_order_allowed(
                        notional, best_ask_prc, best_bid_prc, server_time
                    )

                    await self.if_order_is_true(send_order, instrument)
                    await self.if_cancel_is_true(send_order)

    except Exception as error:
        await raise_error(error)
