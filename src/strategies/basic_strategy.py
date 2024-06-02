# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from db_management import sqlite_management
from utilities import string_modification as str_mod
from loguru import logger as log


async def querying_label_and_size(table) -> list:
    """
    """

    # execute query
    return await sqlite_management.executing_label_and_size_query(table)

async def get_closed_ohlc(limit: int = 100, table: str = "ohlc1_eth_perp_json") -> list:
    """
    """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_ohlc_closed_vol("close", table, limit)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)
    print (ohlc_all)

    # reversing result as price will be processed from the latest to current one
    ohlc_all.reverse()

    return (ohlc_all)


async def cleaned_up_ohlc(limit: int = 100, table: str = "ohlc1_eth_perp_json") -> list:
    """
    """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_ohlc_closed("close", table, limit)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)

    # pick value only
    ohlc = [o["close"] for o in ohlc_all]

    # reversing result as price will be processed from the latest to current one
    ohlc.reverse()

    # exclude last price to minimize its impact to TA calc
    ohlc_reversed = ohlc[: limit - 1]

    return dict(ohlc_reversed=ohlc_reversed, last_price=ohlc[-1:][0])


async def get_ema(ohlc, ratio: float = 0.9) -> dict:
    """
    https://stackoverflow.com/questions/488670/calculate-exponential-moving-average-in-python
    https://stackoverflow.com/questions/59294024/in-python-what-is-the-faster-way-to-calculate-an-ema-by-reusing-the-previous-ca
    """

    return round(
        sum([ratio * ohlc[-x - 1] * ((1 - ratio) ** x) for x in range(len(ohlc))]), 2
    )


async def get_vwap(df, vwap_period) -> dict:
    """
    https://github.com/vishnugovind10/emacrossover/blob/main/emavwap1.0.py
    https://stackoverflow.com/questions/44854512/how-to-calculate-vwap-volume-weighted-average-price-using-groupby-and-apply

    """
    import numpy as np
    
    return df['volume'].rolling(window=vwap_period).apply(lambda x: np.dot(x, df['close']) / x.sum(), raw=False)
    

def delta (last_price, prev_price) -> float:
    """
    """
    return last_price - prev_price


async def get_market_condition(
    threshold, limit: int = 100, ratio: float = 0.9, table: str = "ohlc1_eth_perp_json"
) -> dict:
    """
    """
    import pandas as pd
    
    ohlc_short = await cleaned_up_ohlc(9, table)

    ohlc_long = await cleaned_up_ohlc(20, table)

    ohlc = await cleaned_up_ohlc(limit, table)

    vwap_period = 100
    
    ohlc_all= await get_closed_ohlc(vwap_period)
    #log.error(f'ohlc_all {ohlc_all}')

    df  = pd.DataFrame(ohlc_all, columns=['close', 'volume'])
    log.error(f'df {df}')
    vwap = await get_vwap(df, vwap_period)
    log.error(vwap)
        

    ema = await get_ema(ohlc["ohlc_reversed"], ratio)

    log.error(ema)
    ema_short = await get_ema(ohlc_short["ohlc_reversed"], ratio)

    ema_long = await get_ema(ohlc_long["ohlc_reversed"], ratio)

    last_price = ohlc["last_price"]

    delta_price = delta(last_price, ema)
    delta_price_pct = abs(delta_price / ema)

    rising_price = False
    falling_price = False
    neutral_price = False
    
    log.debug (f'  last_market_price {last_price} ema {ema} ema_short {ema_short} ema_long {ema_long} delta_price_pct {delta_price_pct}')
    #log.warning (f'delta_price {delta_price} delta_price_pct {delta_price_pct} delta_price_pct > threshold {delta_price_pct > threshold} delta_price_pct < threshold {delta_price_pct < threshold}')
    #log.warning (f'  rising_price {rising_price} falling_price {falling_price}')
    #log.debug (f'  ohlc {ohlc}')

    if last_price > ema and ema_short > ema_long:
        rising_price = True
        
    if last_price < ema and ema_short < ema_long:
        falling_price = True

    if rising_price== False and falling_price== False:
        neutral_price = True

    return dict(
        rising_price=rising_price,
        neutral_price=neutral_price,
        falling_price=falling_price,
        last_price=last_price,
        delta_price_pct=delta_price_pct,
        ema=ema,
    )


def get_label(status: str, label_main_or_label_transactions: str) -> str:
    """
    provide transaction label
    """
    from configuration import label_numbering

    if status == "open":
        # get open label
        label = label_numbering.labelling("open", label_main_or_label_transactions)

    if status == "closed":

        # parsing label id
        label_id: int = str_mod.parsing_label(label_main_or_label_transactions)["int"]

        # parsing label strategy
        label_main: str = str_mod.parsing_label(label_main_or_label_transactions)[
            "main"
        ]

        # combine id + label strategy
        label: str = f"""{label_main}-closed-{label_id}"""

    return label


def delta_time(server_time, time_stamp) -> int:
    """
    get difference between now and transaction time
    """
    return server_time - time_stamp


def is_minimum_waiting_time_has_passed(server_time, time_stamp, time_threshold) -> bool:
    """
    check whether delta time has exceed time threhold
    """
    log.debug (f'  server_time {server_time} time_stamp {time_stamp} time_threshold {time_threshold}')
    return True if time_stamp==[] else delta_time(server_time, time_stamp) > time_threshold


def pct_price_in_usd(price: float, pct_threshold: float) -> float:
    return price * pct_threshold


def price_plus_pct(price: float, pct_threshold: float) -> float:
    return price + pct_price_in_usd(price, pct_threshold)


def price_minus_pct(price: float, pct_threshold: float) -> float:
    return price - pct_price_in_usd(price, pct_threshold)


def is_transaction_price_minus_below_threshold(
    last_transaction_price: float, current_price: float, pct_threshold: float
) -> bool:

    return price_minus_pct(last_transaction_price, pct_threshold) >= current_price


def is_transaction_price_plus_above_threshold(
    last_transaction_price: float, current_price: float, pct_threshold: float
) -> bool:

    return price_plus_pct(last_transaction_price, pct_threshold) < current_price


def get_max_time_stamp(result_strategy_label) -> int:
    """
    """
    return (
        []
        if result_strategy_label == []
        else max([o["timestamp"] for o in result_strategy_label])
    )


def get_order_id_max_time_stamp(result_strategy_label) -> int:
    """
    """
    return (
        0
        if get_max_time_stamp(result_strategy_label) == []
        else [
            o["order_id"]
            for o in result_strategy_label
            if o["timestamp"] == get_max_time_stamp(result_strategy_label)
        ][0]
    )


def get_transactions_len(result_strategy_label) -> int:
    """
    """
    return 0 if result_strategy_label == [] else len([o for o in result_strategy_label])


def get_transactions_sum(result_strategy_label) -> int:
    """
    summing transaction under SAME strategy label
    """
    return (
        0
        if result_strategy_label == []
        else sum([o["amount_dir"] for o in result_strategy_label])
    )


def reading_from_db(end_point, instrument: str = None, status: str = None) -> list:
    """ """
    from utilities import pickling, system_tools

    return pickling.read_data(
        system_tools.provide_path_for_file(end_point, instrument, status)
    )


def get_basic_closing_paramaters(selected_transaction: list) -> dict:
    """
    """
    transaction: dict = selected_transaction[0]

    # provide dict placeholder for params
    params = {}

    # default type: limit
    params.update({"type": "limit"})

    # size=exactly amount of transaction size
    params.update({"size": transaction["amount"]})

    # determine side
    transaction_side = transaction["direction"]
    if transaction_side == "sell":
        params.update({"side": "buy"})
    if transaction_side == "buy":
        params.update({"side": "sell"})

    label_closed: str = get_label("closed", transaction["label"])
    params.update({"label": label_closed})

    return params


def get_strategy_config_all() -> list:
    """
    """
    from strategies import entries_exits

    return entries_exits.strategies


@dataclass(unsafe_hash=True, slots=True)
class BasicStrategy:

    """ """

    strategy_label: str

    def get_strategy_config(self, strategy_label: str = None) -> dict:
        """
        """

        params: list = get_strategy_config_all()

        if strategy_label != None:
            str_config: dict = [
                o for o in params if self.strategy_label in o["strategy"]
            ][0]

        else:

            str_config: dict = [
                o
                for o in params
                if str_mod.parsing_label(self.strategy_label)["main"] in o["strategy"]
            ][0]

        return str_config

    def get_basic_opening_paramaters(
        self, notional: float = None, ask_price: float = None, bid_price: float = None
    ) -> dict:
        """
        """

        # provide placeholder for params
        params = {}

        # default type: limit
        params.update({"type": "limit"})

        strategy_config: dict = self.get_strategy_config()
        strategy_config_label: str = strategy_config["strategy"]

        take_profit_pct_transaction: float = strategy_config["take_profit_pct"]
        side: str = strategy_config["side"]

        params.update({"side": side})

        # get transaction label and update the respective parameters
        label_open: str = get_label("open", self.strategy_label)
        params.update({"label": label_open})

        if side == "sell":
            params.update({"entry_price": ask_price})
            everything_is_consistent= True if ("Short" in label_open or "hedging" in label_open)\
                else False
                
        if side == "buy":
            params.update({"entry_price": bid_price})
            everything_is_consistent= True if "Long" in label_open else False

        params.update({"everything_is_consistent": everything_is_consistent})

        if "marketMaker" in strategy_config_label:
            from risk_management.position_sizing import (
                qty_order_and_interval_time as order_and_interval,
            )

            take_profit_pct_daily: float = strategy_config["take_profit_pct_daily"]

            qty_order_and_interval_time: dict = order_and_interval(
                notional, take_profit_pct_daily, take_profit_pct_transaction
            )

            params.update({"size": qty_order_and_interval_time["qty_per_order"]})
            params.update(
                {
                    "interval_time_between_order_in_ms": qty_order_and_interval_time[
                        "interval_time_between_order_in_ms"
                    ]
                }
            )
        if "hedgingSpot" in strategy_config_label:

            params.update({"size": max(1, int(notional / 10))})

        return params

    async def transaction_per_label(self, table, label_filter: str = None) -> dict:
        """ """

        result: list = await querying_label_and_size(table)

        # clean up result with no label main
        result_cleaned = [o for o in result if o["label_main"] != None]

        result_strategy_label: list = [
            o for o in result_cleaned if self.strategy_label in o["label_main"]
        ]

        if result != []:

            if label_filter != None:
                result_strategy_label: list = [
                    o for o in result_strategy_label if label_filter in o["label_main"]
                ]

            if label_filter == "super_main":
                result_strategy_label: list = [
                    o
                    for o in result
                    if str_mod.parsing_label(self.strategy_label)["super_main"]
                    == str_mod.parsing_label(o["label_main"])["super_main"]
                ]

        return dict(
            result_strategy_label=result_strategy_label, result_all=result_cleaned,
        )

    async def get_side_ratio(self) -> dict:
        """ """
        my_trades_attributes = await self.transaction_attributes(
            "my_trades_all_json", "super_main"
        )

        result_strategy_label = my_trades_attributes["transactions_strategy_label"]

        if result_strategy_label != []:
            long_transactions: list = (
                [
                    o["amount_dir"]
                    for o in result_strategy_label
                    if "Long" in o["label_main"]
                ]
            )
            short_transactions: list = (
                [
                    o["amount_dir"]
                    for o in result_strategy_label
                    if "Short" in o["label_main"]
                ]
            )
            print(
                f"basic str-long_transactions {long_transactions} short_transactions {short_transactions}"
            )

            sum_long_transactions: float = 0 if long_transactions == [] else sum(
                long_transactions
            )
            sum_short_transactions: float = 0 if short_transactions == [] else sum(
                short_transactions
            )
            print(
                f"sum_long_transactions {sum_long_transactions} sum_short_transactions {sum_short_transactions}"
            )

            if sum_long_transactions == 0:
                short_long: float = sum_short_transactions
            else:
                short_long: float = sum_short_transactions / sum_long_transactions

            if sum_short_transactions == 0:
                long_short: float = sum_long_transactions
            else:
                long_short: float = sum_long_transactions / sum_short_transactions

        return dict(
            long_short_ratio=0 if result_strategy_label == [] else abs(long_short),
            short_long_ratio=0 if result_strategy_label == [] else abs(short_long),
        )

    async def transaction_attributes(self, table, label_filter: str = None) -> dict:
        """ """

        result: list = await self.transaction_per_label(table, label_filter)

        result_strategy_label: list = result["result_strategy_label"]

        return dict(
            result_all=result["result_all"],
            transactions_strategy_label=result_strategy_label,
            max_time_stamp=get_max_time_stamp(result_strategy_label),
            order_id_max_time_stamp=get_order_id_max_time_stamp(result_strategy_label),
            transactions_sum=get_transactions_sum(result_strategy_label),
            transactions_len=get_transactions_len(result_strategy_label),
        )

    async def is_order_has_sent_before(self, trade_seq) -> bool:
        """ """
        get_my_trades_attributes_closed = await self.transaction_attributes(
            "my_trades_all_json", "closed"
        )

        my_trades_attributes_closed = get_my_trades_attributes_closed[
            "transactions_strategy_label"
        ]
        # assuming only 1
        trade_seq_is_exist: list = False if my_trades_attributes_closed == [] else [
            o for o in my_trades_attributes_closed if trade_seq == o["trade_seq"]
        ] != []
        print(f"trade_seq_is_exist {trade_seq_is_exist}")
        return trade_seq_is_exist

    async def is_send_exit_order_allowed(
        self, ask_price: float, bid_price: float, selected_transaction: list
    ) -> dict:
        """
        """
        # transform to dict
        transaction: dict = selected_transaction[0]

        # get price
        last_transaction_price: float = transaction["price"]

        transaction_side: str = transaction["direction"]

        strategy_config: list = self.get_strategy_config(transaction["label"])

        # get take profit pct
        tp_pct: float = strategy_config["take_profit_pct"]

        # get transaction parameters
        params: list = get_basic_closing_paramaters(selected_transaction)

        if transaction_side == "sell":
            tp_price_reached: bool = is_transaction_price_minus_below_threshold(
                last_transaction_price, bid_price, tp_pct
            )
            params.update({"entry_price": bid_price})

        if transaction_side == "buy":
            tp_price_reached: bool = is_transaction_price_plus_above_threshold(
                last_transaction_price, ask_price, tp_pct
            )
            params.update({"entry_price": ask_price})

        orders = await self.transaction_attributes("orders_all_json", "closed")

        len_orders: int = orders["transactions_len"]

        no_outstanding_order: bool = len_orders == 0

        order_allowed: bool = tp_price_reached and no_outstanding_order

        if order_allowed:

            params.update({"instrument": transaction["instrument_name"]})
            trade_seq = params["label"]

            order_has_sent_before = await self.is_order_has_sent_before(trade_seq)
            print(f"order_has_sent_before {order_has_sent_before}")
            if order_has_sent_before:
                order_allowed == False

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
        )
