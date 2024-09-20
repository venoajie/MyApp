# -*- coding: utf-8 -*-

"""
For strategy with many derivatives name (a/b/c):
    good strategy name: 1) 'supplyDemandShort60A'/'supplyDemandShort60B'/supplyDemandShort60C'
    bad strategy name: 'supplyDemandShort60'
    why? because in sorting process, supplyDemandShort60 means all strategy 
        contains 'supplyDemandShort60', not exclusively 'supplyDemandShort60'
"""

equity_risked_pct_default = 1 / 100 / 4  # .25%
TAKE_PROFIT_PCT_GRID = 1 / 100 / 4
TAKE_PROFIT_PCT_MM = (1 / 100) / 2
TAKE_PROFIT_PCT_DAILY = 0.03


def preferred_spot_currencies() -> list:
    """ """

    return ["BTC","ETH"]

def paramaters_to_balancing_transactions() -> list:
    """ """

    return dict(max_transactions_downloaded_from_exchange=100,
                max_closed_transactions_downloaded_from_sqlite=20
                )


def max_rows(table) -> int:
    """ """
    if "market_analytics_json" in table:
        threshold= 10
    if "ohlc" in table:
        threshold= 10000
    if "supporting_items_json" in table:
        threshold= 200
    return threshold
  
def hedging_spot_attributes() -> list:
    """ """
    hedging= [{
        "strategy": "hedgingSpot",
        "status": "active",
        "settlement_period": ["perpetual"],
        "contribute_to_hedging": True,
        "time_frame": 900,
        "side": "sell",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "weighted_factor": {"minimum": 1, "medium": 5, "extreme": 10, "flash_crash": 20},
        "waiting_minute_before_cancel": 3, #basis?
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": True,
        "delta_price_pct": .5/100
    }]

    return hedging
  
strategies = [
    {
        "strategy": "hedgingSpot",
        "status": "active",
        "settlement_period": ["PERPETUAL"],
        "contribute_to_hedging": True,
        "time_frame": 900,
        "side": "sell",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "weighted_factor": {"minimum": 1, "medium": 5, "extreme": 10, "flash_crash": 20},
        "waiting_minute_before_cancel": 3, #basis?
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": True,
        "delta_price_pct": .5/100
    },
    {
        "strategy": "futureSpreadShort",
        "status": "active",
        "settlement_period": ["PERPETUAL"],
        "contribute_to_hedging": False,
        "time_frame": 900,
        "side": "buy",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": False,
    },
    {
        "strategy": "futureSpreadLong",
        "status": "active",
        "settlement_period": ["PERPETUAL", "week"],
        "contribute_to_hedging": False,
        "time_frame": 900,
        "side": "buy",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": False,
    },
    {
        "strategy": "customLong",
        "status": "active",
        "settlement_period": ["PERPETUAL"],
        "contribute_to_hedging": False,
        "time_frame": 900,
        "side": "buy",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": False,
    },
    {
        "strategy": "customShort",
        "status": "active",
        "settlement_period": ["PERPETUAL"],
        "contribute_to_hedging": False,
        "time_frame": 900,
        "side": "sell",
        "entry_price": 1000,
        "invalidation_entry_price": None,
        "take_profit_usd": 0,
        "take_profit_pct": 0,
        "quantity_discrete": 15,
        "averaging": (5 / 100),
        "cut_loss_usd": 15,
        "cut_loss_pct": (3 / 100),
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": 60,
        "equity_risked_pct": (1 / 100),
        "cancellable": False,
    },
    {
        "strategy": "marketMakerShort",
        "status": "active",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": TAKE_PROFIT_PCT_MM,
        "take_profit_pct_daily": TAKE_PROFIT_PCT_DAILY,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
        "cancellable": True,
    },
    {
        "strategy": "marketMakerLong",
        "status": "active",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": TAKE_PROFIT_PCT_MM,
        "take_profit_pct_daily": TAKE_PROFIT_PCT_DAILY,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
        "cancellable": True,
    },
]


test = [
    {
        "strategy": "basicGridShort",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": TAKE_PROFIT_PCT_GRID,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "basicGridLong",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": TAKE_PROFIT_PCT_GRID,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "every5mLong",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100 / 5,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "every5mShort",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100 / 5,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 10,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "every1hoursLong",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100 / 2,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "every1hoursShort",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100 / 2,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 8,
    },
    {
        "strategy": "every4hoursLong",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 16,
    },
    {
        "strategy": "every4hoursShort",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": None,
        "invalidation_entry_price": None,
        "take_profit_usd": None,
        "take_profit_pct": 1 / 100,
        "quantity_discrete": None,
        "cut_loss_usd": None,
        "cut_loss_pct": None,
        "averaging": None,
        "halt_minute_before_reorder": 60 * 4,
        "equity_risked_usd": None,
        "equity_risked_pct": equity_risked_pct_default * 16,
    },
    {
        "strategy": "supplyDemandShort60A",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "sell",
        "entry_price": 1880,
        "invalidation_entry_price": 1920,
        "take_profit_usd": 1840,
        "take_profit_pct": 1 / 100,
        "quantity_discrete": 15,
        "cut_loss_usd": float(1950),
        "cut_loss_pct": (1 / 100) / 2,
        "averaging": 15,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": 60,
        "equity_risked_pct": equity_risked_pct_default / 2,
    },
    {
        "strategy": "supplyDemandLongB",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": 1860,
        "invalidation_entry_price": 1830,
        "take_profit_usd": float(1910),
        "take_profit_pct": 1 / 100,
        "quantity_discrete": 15,
        "cut_loss_usd": 1783,
        "cut_loss_pct": (1 / 100) / 5,
        "averaging": 15,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": 60,
        "equity_risked_pct": equity_risked_pct_default / 2,
    },
    {
        "strategy": "supplyDemandLongD",
        "status": "inactive",
        "contribute_to_hedging": True,
        "settlement_period": ["PERPETUAL"],
        "time_frame": 3600,
        "side": "buy",
        "entry_price": 1872,
        "invalidation_entry_price": 1860,
        "take_profit_usd": float(1910),
        "take_profit_pct": 1 / 100,
        "quantity_discrete": 15,
        "cut_loss_usd": 1850,
        "cut_loss_pct": (1 / 100) / 5,
        "averaging": 15,
        "halt_minute_before_reorder": 60,
        "equity_risked_usd": 60,
        "equity_risked_pct": equity_risked_pct_default * 2,
    },
]
