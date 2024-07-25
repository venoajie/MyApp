# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies.basic_strategy import (
    BasicStrategy,
    is_minimum_waiting_time_has_passed,
    delta_pct,
)
from db_management.sqlite_management import (
    querying_table,
)


def are_size_and_order_appropriate_for_ordering(
    notional: float, current_size: float, current_outstanding_order_len: int
) -> bool:
    """ """
    return abs(current_size) < notional and current_outstanding_order_len == 0


def hedged_value_to_notional(notional: float, hedged_value: float) -> float:
    """ """
    return abs(hedged_value / notional)


def determine_size(notional: float, factor: float) -> int:
    """ """
    return max(1, int(notional * factor))


def get_bearish_factor(strong_bearish: bool, bearish: bool) -> float:
    """
    Determine factor for size determination.
    strong bearish : 10% of total amount
    bearish        : 5% of total amount
    neutral        : 1% of total amount
    """

    ONE_PCT = 1 / 100

    BEARISH_FACTOR = 10 * ONE_PCT if strong_bearish else 5 * ONE_PCT

    return BEARISH_FACTOR if (strong_bearish or bearish) else ONE_PCT


def is_hedged_value_to_notional_exceed_threshold(
    notional: float, hedged_value: float, threshold: float
) -> float:
    """ """
    return hedged_value_to_notional(notional, hedged_value) > threshold


def get_timing_factor(strong_bearish: bool, bearish: bool, threshold: float) -> bool:
    """
    Determine order outstanding timing for size determination.
    strong bearish : 30% of normal interval
    bearish        : 6% of normal interval
    """

    ONE_PCT = 1 / 100

    ONE_MINUTE: int = 60000

    bearish_interval_threshold = (
        (threshold * ONE_PCT * 30) if strong_bearish else (threshold * ONE_PCT * 60)
    )

    return (
        ONE_MINUTE * bearish_interval_threshold
        if (strong_bearish or bearish)
        else threshold
    )


def is_cancelling_order_allowed(
    strong_bearish: bool,
    bearish: bool,
    threshold: float,
    len_orders: int,
    open_orders_label_strategy: dict,
    server_time: int,
) -> bool:
    """ """

    cancel_allowed: bool = False

    if len_orders != [] and len_orders > 0:

        time_interval = get_timing_factor(strong_bearish, bearish, threshold)

        max_tstamp_orders: int = open_orders_label_strategy["max_time_stamp"]

        minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed(
            server_time, max_tstamp_orders, time_interval
        )
        if minimum_waiting_time_has_passed:
            cancel_allowed: bool = True

    return cancel_allowed


async def get_market_condition_hedging(TA_result_data, index_price, threshold) -> dict:
    """ """
    neutral_price, rising_price, falling_price = False, False, False
    strong_rising_price, strong_falling_price = False, False

    # print(f" TA_result_data{TA_result_data}")

    open_60 = TA_result_data["60_open"]
    current_higher_open = TA_result_data["1m_current_higher_open"]

    delta_price_pct = delta_pct(index_price, open_60)

    if index_price > open_60:
        rising_price = True

        if delta_price_pct > threshold:
            strong_rising_price = True

    if index_price < open_60:
        falling_price = True

        if delta_price_pct > threshold:
            strong_falling_price = True

    if rising_price == False and falling_price == False:
        neutral_price = True

    return dict(
        rising_price=rising_price,
        strong_rising_price=strong_rising_price,
        neutral_price=neutral_price,
        falling_price=falling_price,
        strong_falling_price=strong_falling_price,
    )


@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):
    """ """

    def get_basic_params(self) -> dict:
        """ """
        return BasicStrategy(self.strategy_label)

    async def is_send_and_cancel_open_order_allowed(
        self,
        notional: float,
        index_price,
        ask_price: float,
        server_time: int,
        TA_result_data: dict,
        threshold_market_condition: float,
        threshold: float,
    ) -> dict:
        """ """

        open_orders_label_strategy: (
            dict
        ) = await self.get_basic_params().transaction_attributes(
            "orders_all_json", "open"
        )

        fluctuation_exceed_threshold = TA_result_data["fluctuation_exceed_threshold"]

        market_condition = await get_market_condition_hedging(
            TA_result_data, index_price, threshold_market_condition
        )

        bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]

        strong_bullish = market_condition["strong_rising_price"]
        strong_bearish = market_condition["strong_falling_price"]

        SIZE_FACTOR = get_bearish_factor(strong_bearish, bearish)

        size = determine_size(notional, SIZE_FACTOR)

        len_orders: int = open_orders_label_strategy["transactions_len"]
        my_trades: dict = await self.get_basic_params().transaction_attributes(
            "my_trades_all_json"
        )

        print(
            f"is_bearish {bearish} is_bullish {bullish} strong_bullish {strong_bullish} strong_bearish {strong_bearish}"
        )

        sum_my_trades: int = my_trades["transactions_sum"]
        params: dict = self.get_basic_params().get_basic_opening_parameters(
            ask_price, None, notional
        )

        params.update({"size": size})

        print(f"sum_my_trades {sum_my_trades} notional {notional}")
        size_and_order_appropriate_for_ordering: bool = (
            are_size_and_order_appropriate_for_ordering(
                notional, sum_my_trades, len_orders
            )
        )

        cancel_allowed: bool = is_cancelling_order_allowed(
            strong_bearish,
            bearish,
            threshold,
            len_orders,
            open_orders_label_strategy,
            server_time,
        )

        if params["everything_is_consistent"]:
            order_allowed: bool = size_and_order_appropriate_for_ordering \
                and (bearish or strong_bearish)\
                        and fluctuation_exceed_threshold

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=open_orders_label_strategy["order_id_max_time_stamp"],
        )

    async def is_send_exit_order_allowed(
        self,
        TA_result_data,
        threshold_market_condition: float,
        index_price: float,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
    ) -> dict:
        """ """

        market_condition = await get_market_condition_hedging(
            TA_result_data, index_price, threshold_market_condition
        )

        bullish = market_condition["rising_price"]
        strong_bullish = market_condition["strong_rising_price"]
        # is_bearish = market_condition["falling_price"]

        # my_trades: dict = await self.get_basic_params().transaction_attributes(
        #    "my_trades_all_json"
        # )

        # sum_my_trades: int = my_trades["transactions_sum"]

        # hedged_value_is_still_safe: bool = self.is_hedged_value_to_notional_exceed_threshold(
        #    notional, sum_my_trades, MIN_HEDGING_RATIO
        # )

        exit_params: dict = await self.get_basic_params().is_send_exit_order_allowed(
            market_condition, ask_price, bid_price, selected_transaction
        )

        exit_allowed: bool = exit_params["order_allowed"] and (
            bullish or strong_bullish
        )

        return dict(
            order_allowed=exit_allowed,
            order_parameters=(
                [] if exit_allowed == False else exit_params["order_parameters"]
            ),
        )
