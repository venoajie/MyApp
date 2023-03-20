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
    pct_daily_profit_target = 2 * pct
    pct_profit_per_transaction = pct/2
    pct_capital_risk = 2 * pct
    sizing_for_perpetual_grid = position_sizing.sizing_for_perpetual_grid(notional, pct_daily_profit_target, pct_profit_per_transaction, pct_capital_risk)
    assert sizing_for_perpetual_grid == 200
