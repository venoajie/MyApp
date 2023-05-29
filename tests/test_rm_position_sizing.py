# -*- coding: utf-8 -*-
from src.risk_management import position_sizing


def test_pos_sizing():
    assert (
        position_sizing.pos_sizing(
            cut_loss_price=100, entry_price=90, capital=1000, pct_loss=0.5 / 100
        )
        == 50
    )
    assert (
        position_sizing.pos_sizing(
            cut_loss_price=90, entry_price=100, capital=1000, pct_loss=0.5 / 100
        )
        == 45
    )
    assert (
        position_sizing.pos_sizing(
            cut_loss_price=100, entry_price=90, capital=1000, pct_loss=1 / 100
        )
        == 100
    )
    assert (
        position_sizing.pos_sizing(
            cut_loss_price=90, entry_price=100, capital=1000, pct_loss=1 / 100
        )
        == 90
    )

def test_compute_delta():
    notional = 100
    long = 0
    short = -100
    compute_delta = position_sizing.compute_delta(notional, long, short)
    assert compute_delta == 0

def test_compute_leverage():
    notional = 100
    long = 0
    short = -100
    compute_delta = position_sizing.compute_leverage(notional, long, short)
    assert compute_delta == 1

def test_sizing_for_perpetual_grid():
    notional = 100
    pct = 1/100
    pct_daily_profit_target = 3 * pct
    pct_profit_per_transaction = pct/4
    daily_turn_over = position_sizing.daily_turn_over(pct_daily_profit_target, pct_profit_per_transaction)
    assert daily_turn_over == 6
    
    hourly_sizing = position_sizing.hourly_sizing_for_perpetual_grid(notional, pct_daily_profit_target, pct_profit_per_transaction)
    assert hourly_sizing == 25
    
    ONE_MINUTE= 60

    quantities_order = position_sizing.quantities_per_order(hourly_sizing, ONE_MINUTE)
    assert quantities_order == 1

    time_delay_  = position_sizing.time_delay_before_reorder(hourly_sizing, ONE_MINUTE)
    assert time_delay_ == 2.4

    qties_order_and_time_delay  = position_sizing.qty_order_and_time_delay(notional, pct_daily_profit_target, pct_profit_per_transaction)
    assert qties_order_and_time_delay == {'minute_delay': 02.4, 'qty_per_order': 1}
