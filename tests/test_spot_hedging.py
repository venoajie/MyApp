# -*- coding: utf-8 -*-

from src.risk_management import spot_hedging

myTrades1 = [
    {
        "trade_seq": 119459281,
        "trade_id": "ETH-162634254",
        "timestamp": 1678610180143,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1473.05,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32205761779",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1472.79,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678610144572",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1474.68,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 78.0,
    },
    {
        "trade_seq": 119653801,
        "trade_id": "ETH-162909430",
        "timestamp": 1678706775993,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1583.75,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32231983208",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1583.81,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678706775367",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1583.99,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 5.0,
    },
    {
        "trade_seq": 119665688,
        "trade_id": "ETH-162925875",
        "timestamp": 1678713118256,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1598.0,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32234303212",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1597.73,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678713106585",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1597.86,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 1.0,
    },
    {
        "trade_seq": 119736857,
        "trade_id": "ETH-163020718",
        "timestamp": 1678727097665,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1666.15,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32243915623",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1666.07,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678727089260",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1666.08,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 4.0,
    },
    {
        "trade_seq": 119736858,
        "trade_id": "ETH-163020719",
        "timestamp": 1678727097665,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1666.15,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32243915636",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1666.07,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678727089307",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1666.08,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 4.0,
    },
    {
        "trade_seq": 119736859,
        "trade_id": "ETH-163020720",
        "timestamp": 1678727097665,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1666.15,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32243915644",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1666.07,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678727089354",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1666.08,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 4.0,
    },
    {
        "trade_seq": 119773081,
        "trade_id": "ETH-163068627",
        "timestamp": 1678755677524,
        "tick_direction": 3,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1671.55,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32252020677",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1671.66,
        "liquidity": "M",
        "label": "hedgingSpot-open-1678755675478",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1673.29,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 68.0,
    },
    {
        "trade_seq": 119946512,
        "trade_id": "ETH-163294790",
        "timestamp": 1678828105145,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1679.8,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32281785727",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1679.01,
        "liquidity": "M",
        "label": "supplyDemandShort60-open-1678828104726",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1677.09,
        "fee_currency": "ETH",
        "fee": 0.0,
        "direction": "sell",
        "api": True,
        "amount": 10.0,
    },
]

label_hedging1 = "hedgingSpot"
spot_hedging1 = spot_hedging.SpotHedging(label_hedging1, myTrades1)

open_orders = [
    {
        "web": False,
        "time_in_force": "good_til_cancelled",
        "risk_reducing": False,
        "replaced": False,
        "reject_post_only": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1216.7,
        "post_only": True,
        "order_type": "limit",
        "order_state": "open",
        "order_id": "ETH-3149033807",
        "mmp": False,
        "max_show": 9.0,
        "last_update_timestamp": 1671757441131,
        "label": "hedging spot-open-1671757441111",
        "is_liquidation": False,
        "instrument_name": "ETH-PERPETUAL",
        "filled_amount": 0.0,
        "direction": "sell",
        "creation_timestamp": 1671757441131,
        "commission": 0.0,
        "average_price": 0.0,
        "api": True,
        "amount": 9.0,
    },
    {
        "web": False,
        "time_in_force": "good_til_cancelled",
        "risk_reducing": False,
        "replaced": False,
        "reject_post_only": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1216.7,
        "post_only": True,
        "order_type": "limit",
        "order_state": "open",
        "order_id": "ETH-3149033894",
        "mmp": False,
        "max_show": 9.0,
        "last_update_timestamp": 1671757441796,
        "label": "hedging spot-open-1671757441776",
        "is_liquidation": False,
        "instrument_name": "ETH-PERPETUAL",
        "filled_amount": 0.0,
        "direction": "sell",
        "creation_timestamp": 1671757441796,
        "commission": 0.0,
        "average_price": 0.0,
        "api": True,
        "amount": 9.0,
    },
    {
        "web": False,
        "time_in_force": "good_til_cancelled",
        "risk_reducing": False,
        "replaced": False,
        "reject_post_only": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1216.7,
        "post_only": True,
        "order_type": "limit",
        "order_state": "open",
        "order_id": "ETH-3149033897",
        "mmp": False,
        "max_show": 9.0,
        "last_update_timestamp": 1671757442106,
        "label": "hedging spot-open-1671757442085",
        "is_liquidation": False,
        "instrument_name": "ETH-PERPETUAL",
        "filled_amount": 0.0,
        "direction": "sell",
        "creation_timestamp": 1671757442106,
        "commission": 0.0,
        "average_price": 0.0,
        "api": True,
        "amount": 9.0,
    },
]

myTrades = [
    {
        "trade_seq": 1814,
        "trade_id": "ETH-16709238",
        "timestamp": 1671190012391,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1211.9,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-3105705292",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1211.74,
        "liquidity": "M",
        "label": "hedging spot-open-1671189554374",
        "instrument_name": "ETH-23DEC22",
        "index_price": 1211.95,
        "fee_currency": "ETH",
        "fee": -8.17e-06,
        "direction": "sell",
        "api": True,
        "amount": 99.0,
    },
    {
        "trade_seq": 1941,
        "trade_id": "ETH-16709956",
        "timestamp": 1671200629432,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1211.9,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-3106655076",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1212.25,
        "liquidity": "M",
        "label": "hedging spot-open-1671200377734",
        "instrument_name": "ETH-23DEC22",
        "index_price": 1212.58,
        "fee_currency": "ETH",
        "fee": -8.17e-06,
        "direction": "sell",
        "api": True,
        "amount": 99.0,
    },
    {
        "trade_seq": 1945,
        "trade_id": "ETH-16709992",
        "timestamp": 1671200864490,
        "tick_direction": 0,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1211.9,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-3106695378",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1211.74,
        "liquidity": "M",
        "label": "hedging spot-open-1671200747737",
        "instrument_name": "ETH-23DEC22",
        "index_price": 1211.78,
        "fee_currency": "ETH",
        "fee": -8.17e-06,
        "direction": "sell",
        "api": True,
        "amount": 99.0,
    },
]

label_hedging = "hedging spot"
spot_hedging = spot_hedging.SpotHedging(label_hedging, myTrades)


def test_summing_size_open_orders():
    assert spot_hedging.net_position(open_orders) == -27


def test_compute_minimum_hedging_size():
    notional = 107.38056472000001
    min_trade_amount = 1
    contract_size = 1
    assert (
        spot_hedging.compute_minimum_hedging_size(
            notional, min_trade_amount, contract_size
        )
        == -108
    )


def test_compute_actual_hedging_size():
    assert spot_hedging.compute_actual_hedging_size() == -297
    assert spot_hedging1.compute_actual_hedging_size() == -164


def is_over_hedged():
    minimum_hedging_size = 108
    assert (
        spot_hedging.is_over_hedged(
            open_orders, minimum_hedging_size, "hedging spot-open"
        )
        == False
    )

    minimum_hedging_size = 106
    assert (
        spot_hedging.is_over_hedged(
            open_orders, minimum_hedging_size, "hedging spot-open"
        )
        == True
    )

    minimum_hedging_size = 107
    assert (
        spot_hedging.is_over_hedged(
            open_orders, minimum_hedging_size, "hedging spot-open"
        )
        == False
    )


def test_compute_remain_unhedged():
    notional = 107.38056472000001
    min_trade_amount = 1
    contract_size = 1

    assert (
        spot_hedging.compute_remain_unhedged(notional, min_trade_amount, contract_size)
        == 189
    )


def test_myTrades_max_price_plus_threshold():
    threshold = 2 / 100
    assert (
        spot_hedging.my_trades_max_price_plus_threshold(threshold, 1215)[
            "index_price_higher_than_threshold"
        ]
        == False
    )
    assert (
        spot_hedging.my_trades_max_price_plus_threshold(threshold, 1250)[
            "index_price_higher_than_threshold"
        ]
        == True
    )
    assert (
        spot_hedging.my_trades_max_price_plus_threshold(threshold, 1150)[
            "index_price_lower_than_threshold"
        ]
        == True
    )
    assert (
        spot_hedging.my_trades_max_price_plus_threshold(threshold, 1209)[
            "index_price_lower_than_threshold"
        ]
        == False
    )


def separate_open_trades_which_have_closed():
    closed_label = "close"
    all_trades = [
        {
            "trade_seq": 1815,
            "trade_id": "ETH-16709238",
            "timestamp": 1671190012392,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3105705293",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-closed-1671189554374",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.95,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
        {
            "trade_seq": 1814,
            "trade_id": "ETH-16709238",
            "timestamp": 1671190012391,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3105705292",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-open-1671189554374",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.95,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
        {
            "trade_seq": 1941,
            "trade_id": "ETH-16709956",
            "timestamp": 1671200629432,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3106655076",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1212.25,
            "liquidity": "M",
            "label": "hedging spot-open-1671200377734",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1212.58,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
        {
            "trade_seq": 1945,
            "trade_id": "ETH-16709992",
            "timestamp": 1671200864490,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3106695378",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-open-1671200747737",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.78,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
    ]
    closed_trades = [
        {
            "trade_seq": 1815,
            "trade_id": "ETH-16709238",
            "timestamp": 1671190012392,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3105705293",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-closed-1671189554374",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.95,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
        {
            "trade_seq": 1814,
            "trade_id": "ETH-16709238",
            "timestamp": 1671190012391,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3105705292",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-open-1671189554374",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.95,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
    ]
    open_trades = [
        {
            "trade_seq": 1941,
            "trade_id": "ETH-16709956",
            "timestamp": 1671200629432,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3106655076",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1212.25,
            "liquidity": "M",
            "label": "hedging spot-open-1671200377734",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1212.58,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
        {
            "trade_seq": 1945,
            "trade_id": "ETH-16709992",
            "timestamp": 1671200864490,
            "tick_direction": 0,
            "state": "filled",
            "self_trade": False,
            "risk_reducing": False,
            "reduce_only": False,
            "profit_loss": 0.0,
            "price": 1211.9,
            "post_only": True,
            "order_type": "limit",
            "order_id": "ETH-3106695378",
            "mmp": False,
            "matching_id": None,
            "mark_price": 1211.74,
            "liquidity": "M",
            "label": "hedging spot-open-1671200747737",
            "instrument_name": "ETH-23DEC22",
            "index_price": 1211.78,
            "fee_currency": "ETH",
            "fee": -8.17e-06,
            "direction": "sell",
            "api": True,
            "amount": 99.0,
        },
    ]
    assert (
        spot_hedging.separate_open_trades_pair_which_have_closed(
            "eth", "hedging spot", closed_label, all_trades
        )["closed_trades"]
        == closed_trades
    )
    assert (
        spot_hedging.separate_open_trades_pair_which_have_closed(
            "eth", "hedging spot", closed_label, all_trades
        )["remaining_open_trades"]
        == open_trades
    )
