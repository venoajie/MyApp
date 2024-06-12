# # -*- coding: utf-8 -*-
"""
Compute:
- position sizing for each order send
- delta for current position
- leverage for current position
"""


def price_difference(cut_loss_price: float, entry_price: float) -> float:
    """
    Compute percentage difference between entry price vs cut loss price in USD

    Args:
        cut_loss_price (float)
        entry_price (float)

    Returns:
        float

    """
    return (cut_loss_price - entry_price) / entry_price


def max_loss_allowed(capital: float, pct_loss: float = 1 / 100 * 0.5) -> float:
    """
    Compute maximum loss allowed in USD

    Args:
        capital (float)
        pct_loss (float). Default= .5%

    Returns:
        float

    """

    return capital * pct_loss


def pos_sizing(
    cut_loss_price: float, entry_price: float, capital: float, pct_loss: float = 1 / 10
) -> float:
    """
    Compute position sizing for each order send

    Args:
        cut_loss_price (float)
        entry_price (float)
        capital (float)
        pct_loss (float)

    Returns:
        float

    Reference:
        https://
    """
    return int(
        abs(
            (
                max_loss_allowed(capital, pct_loss)
                / price_difference(entry_price, cut_loss_price)
            )
        )
    )


def compute_my_trade_based_on_side(my_trades_open: list) -> float:
    """

    Args:
        my_trades_open (list)

    Returns:
        dict

    """

    total_long = (
        0
        if my_trades_open == []
        else sum([o["amount"] for o in my_trades_open if o["direction"] == "buy"])
    )

    total_short = (
        0
        if my_trades_open == []
        else sum([o["amount"] for o in my_trades_open if o["direction"] == "sell"]) * -1
    )

    return {"total_long": total_long, "total_short": total_short}


def compute_delta(notional: float, total_long_qty: int, total_short_qty: int) -> float:
    """
    Compute delta for current position
    Args:
        notional (float)
        total_short_qty (int)
        total_short_qty (int)
    Returns:
        float
    Reference:
        https://
    """
    return (notional + total_long_qty + total_short_qty) / notional


def compute_leverage(
    notional: float, total_long_qty: int, total_short_qty: int
) -> float:
    """
    Compute leverage for current position
    Args:
        notional (float)
        total_short_qty (int)
        total_short_qty (int)
    Returns:
        float
    Reference:
        https://
    """
    return (total_long_qty + abs(total_short_qty)) / notional


def compute_position_leverage_and_delta(notional: float, my_trades_open: list) -> list:
    """
    Combining result of the computation:
    - Delta for current position
    - Leverage for current position

    Args:
        my_trades_open (list)

    Returns:
        float

    Reference:
        https://

    """
    trade_based_on_side = compute_my_trade_based_on_side(my_trades_open)
    total_long_qty = trade_based_on_side["total_long"]
    total_short_qty = trade_based_on_side["total_short"]
    return {
        "delta": compute_delta(notional, total_long_qty, total_short_qty),
        "leverage": compute_leverage(notional, total_long_qty, total_short_qty),
    }


def turnOver_times(
    pct_daily_profit_target: float,
    pct_profit_per_transaction: float,
    ordered_side: int = 2,
) -> float:
    """
    ordered_side = 2, consisted of long and short
    """
    daily = (pct_daily_profit_target / pct_profit_per_transaction) / ordered_side

    return {
        "daily": daily,
        "hourly": daily / 24,
    }


def hourly_sizing(
    notional: float, pct_daily_profit_target: float, pct_profit_per_transaction: float
) -> float:
    """ """
    SECONDS_IN_ONE_HOUR = 3600

    hourly_target_turn_over = turnOver_times(
        pct_daily_profit_target, pct_profit_per_transaction
    )["hourly"]

    qty_orders_per_hour = hourly_target_turn_over * notional

    return {
        "quantity_per_hour": max(1, int(qty_orders_per_hour)),
        "interval_time_before_reorder": (qty_orders_per_hour / notional)
        * SECONDS_IN_ONE_HOUR,
    }


def quantities_per_order(hourly_qty: float, SIXTY_MINUTES: int = 60) -> float:
    """ """
    return 1 if hourly_qty < SIXTY_MINUTES else int(hourly_qty / SIXTY_MINUTES)


def interval_time_before_reorder_in_ms(
    minute_delay_before_reorder: float, SIXTY_MINUTES: int = 60
) -> float:
    """ """

    return minute_delay_before_reorder * SIXTY_MINUTES * 1000


def qty_order_and_interval_time(
    notional: float,
    pct_daily_profit_target: float,
    pct_profit_per_transaction: float,
    SIXTY_MINUTES: int = 60,
) -> dict:
    """ """

    hourly_qty = hourly_sizing(
        notional, pct_daily_profit_target, pct_profit_per_transaction
    )
    print(f"{hourly_qty}")

    minute_delay_before_reorder = hourly_qty["interval_time_before_reorder"]

    return dict(
        interval_time_between_order=minute_delay_before_reorder,
        interval_time_between_order_in_ms=interval_time_before_reorder_in_ms(
            minute_delay_before_reorder
        ),
        qty_per_order=quantities_per_order(
            hourly_qty["quantity_per_hour"], SIXTY_MINUTES
        ),
    )
