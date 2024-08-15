# # -*- coding: utf-8 -*-

# in super bearish: 100% hedged in less than x minutes
# in bearish: 80% hedged in less than x minutes
# other than that: release all inventories

# issues:
# -liquidity
# -order: possibility executed more than one time

# determine size and open order o/s minute agrresiveness
# condition     : super_bearish      bearish    relatively_bearish
# qty in 1 hour :     120%              80%             50%
# os order sec  :       1m              3 m             m

# tf: 5 min, 15 min, 60 min

# what is relatively_bearish?
# current < open (1 tf)

# what is bearish?
# current < open (2 tf)

# what is super bearish?
# current < open (3 tf)

# what is bullish?
# current > open (2 tf)
# current > open (2 tf)


# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies.basic_strategy import (
    BasicStrategy,
    is_minimum_waiting_time_has_passed,
    delta_pct,
    proforma_size,
)
from db_management.sqlite_management import (
    querying_table,
)


def are_size_and_order_appropriate_for_ordering(
    notional: float, current_size: float, current_outstanding_order_len: int
) -> bool:
    """ """
    return abs(current_size) < notional and current_outstanding_order_len == 0


def are_future_size_and_order_appropriate_for_ordering(
    notional: float,
    proforma_size: float,
    current_outstanding_order_len: int,
    threshold: float,
) -> bool:
    """ """
    return abs(proforma_size) < notional and current_outstanding_order_len < threshold


def hedged_value_to_notional(notional: float, hedged_value: float) -> float:
    """ """
    return abs(hedged_value / notional)


def determine_size(notional: float, factor: float) -> int:
    """ """
    return max(1, int(notional * factor))


def bearish_size_factor() -> int:
    """ """
    return 100


def strong_bearish_size_factor() -> int:
    """ """
    return 100

def max_len_orders(params, 
            strong_bearish, bearish, relatively_bearish) -> int:
    """ """
    max_len_orders = params["weighted_factor"]
    max_len=max_len_orders["relatively"]
    if strong_bearish:
        max_len=max_len_orders["extreme"]
    if bearish:
        max_len=max_len_orders["normal"]
    if relatively_bearish:
        max_len=max_len_orders["relatively"]

    return max_len


def get_bearish_factor_size(
    strong_bearish: bool, bearish: bool, relatively_bearish: bool
) -> float:
    """
    Determine factor for size determination.
    strong bearish      : 10% of total amount
    bearish             : 5% of total amount
    relatively_bearish  : 5% of total amount
    neutral             : 1% of total amount
    """

    ONE_PCT = 1 / 100

    SIZE_FACTOR=100

    if relatively_bearish or bearish:
        SIZE_FACTOR = bearish_size_factor()

    if strong_bearish:
        SIZE_FACTOR = strong_bearish_size_factor()

    return SIZE_FACTOR * ONE_PCT


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
    strong_rising_price, super_bearish, relatively_bearish = False, False, False

    open_60 = TA_result_data["60_open"]
    current_higher_open = TA_result_data["1m_current_higher_open"]
    # print (f"TA_result_data {TA_result_data}")
    fluctuation_exceed_threshold = TA_result_data["1m_fluctuation_exceed_threshold"]

    delta_price_pct = delta_pct(index_price, open_60)

    if fluctuation_exceed_threshold:

        if index_price > open_60:
            rising_price = True

            if delta_price_pct > threshold:
                strong_rising_price = True

        if index_price < open_60:
            falling_price = True

            if delta_price_pct > threshold:
                super_bearish = True

    if rising_price == False and falling_price == False:
        neutral_price = True

    return dict(
        rising_price=rising_price,
        strong_rising_price=strong_rising_price,
        neutral_price=neutral_price,
        falling_price=falling_price,
        super_bearish=super_bearish,
        relatively_bearish=relatively_bearish,
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
        # print (f"TA_result_data {TA_result_data}")

        fluctuation_exceed_threshold = TA_result_data["1m_fluctuation_exceed_threshold"]

        market_condition = await get_market_condition_hedging(
            TA_result_data, index_price, threshold_market_condition
        )

        bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]
        relatively_bearish = market_condition["relatively_bearish"]

        strong_bullish = market_condition["strong_rising_price"]
        strong_bearish = market_condition["super_bearish"]
        neutral = market_condition["neutral_price"]

        SIZE_FACTOR = get_bearish_factor_size(
            strong_bearish, bearish, relatively_bearish
        )

        size = determine_size(notional, SIZE_FACTOR)

        len_orders: int = open_orders_label_strategy["transactions_len"]

        my_trades: dict = await self.get_basic_params().transaction_attributes(
            "my_trades_all_json"
        )

        print(
            f"is_neutral {neutral} is_bearish {bearish} is_bullish {bullish} strong_bullish {strong_bullish} strong_bearish {strong_bearish}"
        )

        sum_my_trades: int = my_trades["transactions_sum"]
        sum_my_orders: int = open_orders_label_strategy["transactions_sum"]
        params: dict = self.get_basic_params().get_basic_opening_parameters(
            ask_price, None, notional
        )

        params.update({"size": size})

        max_len_orders = max_len_orders(params, 
            strong_bearish, bearish, relatively_bearish)
        proforma_qty = proforma_size(
            sum_my_trades, sum_my_orders, size)

        print(
            f"max_len_orders {max_len_orders} sum_my_trades {sum_my_trades} sum_my_orders {sum_my_orders} proforma_qty {proforma_qty} notional {notional}"
        )

        size_and_order_appropriate_for_ordering: bool = (
            are_future_size_and_order_appropriate_for_ordering(notional, proforma_qty,len_orders,max_len_orders)
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
            order_allowed: bool = (
                size_and_order_appropriate_for_ordering
                and (bearish or strong_bearish)
                and fluctuation_exceed_threshold
            )

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
