# -*- coding: utf-8 -*-

"""
For strategy with many derivatives name (a/b/c):
    good strategy name: 1) 'supplyDemandShort60A'/'supplyDemandShort60B'/supplyDemandShort60C'
    bad strategy name: 'supplyDemandShort60'
    why? because in sorting process, supplyDemandShort60 means all strategy 
        contains 'supplyDemandShort60', not exclusively 'supplyDemandShort60'
"""

equity_risked_pct_default = 1 / 100 / 4

strategies = [
    {
        "strategy": "supplyDemandShort60",
        "instrument": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": 2050,
        "invalidation_entry_price": 2100,
        "take_profit_usd": 1640,
        "take_profit_pct": 1 / 100,
        "quantity_discrete": 15,
        "cut_loss_usd": float(1850),
        "cut_loss_pct": (1 / 100) / 2,
        "averaging": 15,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": 60,
        "equity_risked_pct": equity_risked_pct_default,
    },
    {
        "strategy": "supplyDemandLongA",
        "instrument": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": 1800,
        "invalidation_entry_price": 1820,
        "take_profit_usd": float(1850),
        "take_profit_pct": 1 / 100,
        "quantity_discrete": 15,
        "cut_loss_usd": 1740,
        "cut_loss_pct": (1 / 100) / 5,
        "averaging": 15,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": 60,
        "equity_risked_pct": equity_risked_pct_default * 4,
    },
    {
        "strategy": "hedgingSpot",
        "instrument": ["PERPETUAL"],
        "time_frame": 900,
        "side": "sell",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": (1 / 100) / 15,
        "take_profit_pct": (1 / 100)/2,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
    },
]
