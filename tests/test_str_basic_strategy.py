# -*- coding: utf-8 -*-

import strategies.basic_strategy as strategy

label_strategy = "marketMakerShort"
Strategy = strategy.BasicStrategy(label_strategy)


def test_get_strategy_config():

    result = Strategy.get_strategy_config()

    assert result == {
        "strategy": "marketMakerShort",
        "status": "active",
        "instrument": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 0.0025,
        "take_profit_pct_daily": 0.05,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": 0.02,
    }


def test_get_strategy_config():

    notional = 100

    result = Strategy.get_basic_opening_paramaters(notional)

    assert result == {"type": "limit", "size": 1}


def test_get_labels():

    from src.utilities import time_modification

    now_utc = time_modification.convert_time_to_utc()["utc_now"]
    now_unix = time_modification.convert_time_to_unix(now_utc)

    label_main_or_label_transactions = "hedgingSpot"

    result = Strategy.get_label("open", label_main_or_label_transactions)[:25]

    assert result == f"{label_main_or_label_transactions}-open-{now_unix}"[:25]

    label_main_or_label_transactions = "hedgingSpot-open-1683065013136"

    result = Strategy.get_label("closed", label_main_or_label_transactions)

    assert result == "hedgingSpot-closed-1683065013136"
