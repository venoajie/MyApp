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

async def get_hlc_vol(window: int = 9, table: str = "ohlc1_eth_perp_json") -> list:
    """
    """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_hlc_vol(table, window)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)
    #log.info(ohlc_all)

    return (ohlc_all)


async def get_price_ohlc(price: str="close", window: int = 100, table: str = "ohlc1_eth_perp_json") -> list:
    """
    """

    # get query for close price
    get_ohlc_query = sqlite_management.querying_ohlc_price_vol(price, table, window)

    # executing query above
    ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)

    return (ohlc_all)


async def cleaned_up_ohlc(price: str="close", window: int = 100, table: str = "ohlc1_eth_perp_json") -> list:
    """
    """

    # get query for close price
    ohlc_all = await get_price_ohlc(price, window, table)
    
    # pick value only
    ohlc = [o[price] for o in ohlc_all]

    return dict(ohlc=ohlc[: window - 1], last_price=ohlc[-1:][0])

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
    

def delta (last_price: float, prev_price: float) -> float:
    """
    """
    return last_price - prev_price

def delta_pct (last_price: float, prev_price: float) -> float:
    """
    """
    return abs(delta(last_price, prev_price)/prev_price)


async def get_market_condition(
    threshold, limit: int = 100, ratio: float = 0.9, table: str = "ohlc1_eth_perp_json"
) -> dict:
    """
    """
    import pandas as pd
    
    ohlc_high_9 = await cleaned_up_ohlc("high",9,table)
    ohlc_low_9 = await cleaned_up_ohlc("low",9,table)


#    log.error(f'ohlc_high_9 {ohlc_high_9}')
    ema_high_9 = await get_ema(ohlc_high_9["ohlc"], ratio)
#    log.error(f'ema_high_9 {ema_high_9}')

    ema_low_9 = await get_ema(ohlc_low_9["ohlc"], ratio)

#    log.error(f'ema_low_9 {ema_low_9}')
    delta_price_pct_ema_low_high = delta_pct(ema_low_9, ema_high_9)
    #log.warning(f'ema_high_9 {ema_high_9} ema_low_9 {ema_low_9} delta_price_pct_ema_low_high {delta_price_pct_ema_low_high}')
    ohlc_short = await cleaned_up_ohlc("close",9, table)
    ohlc_long = await cleaned_up_ohlc("close",20, table)
    

    ohlc = await cleaned_up_ohlc("close",limit, table)

    vwap_period = 100
    
    ohlc_all= await get_price_ohlc ("close", vwap_period)

    df  = pd.DataFrame(ohlc_all, columns=['close', 'volume'])
    #log.error(f'df {df}')
    df_vwap = await get_vwap(df, vwap_period)     
    vwap=df_vwap.iloc[-1]

    ema = await get_ema(ohlc["ohlc"], ratio)


    #log.error(ema)
    ema_short = await get_ema(ohlc_short["ohlc"], ratio)

    ema_long = await get_ema(ohlc_long["ohlc"], ratio)

    last_price = ohlc["last_price"]

    rising_price = False
    falling_price = False
    neutral_price = False
    
    log.debug (f'  last_market_price {last_price} vwap {vwap} ema {ema} ema_short {ema_short} ema_long {ema_long}')
    #log.warning (f'delta_price {delta_price} delta_price_pct {delta_price_pct} delta_price_pct > threshold {delta_price_pct > threshold} delta_price_pct < threshold {delta_price_pct < threshold}')
    #log.warning (f'  rising_price {rising_price} falling_price {falling_price}')
    #log.debug (f'  ohlc {ohlc}')

    if last_price > ema_short and ema_short > ema_long:
        rising_price = True
        
    if last_price < ema_short and ema_short < ema_long:
        falling_price = True

    if rising_price== False and falling_price== False:
        neutral_price = True

    return dict(
        rising_price=rising_price,
        neutral_price=neutral_price,
        falling_price=falling_price,
        last_price=last_price,
        profit_target_pct=delta_price_pct_ema_low_high,
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

def provide_side_to_close_transaction(transaction: dict) -> str:
    """ """

    # determine side
    transaction_side = transaction["direction"]
    if transaction_side == "sell":
        side="buy"
    if transaction_side == "buy":
        side= "sell"

    return side

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
    side=provide_side_to_close_transaction(transaction)
    params.update({"side": side})

    label_closed: str = get_label("closed", transaction["label"])
    params.update({"label": label_closed})

    return params

def get_strategy_config_all() -> list:
    """
    """
    from strategies import entries_exits

    return entries_exits.strategies

def is_everything_consistent(params) -> dict:
    """
    """
    label= params["label"]

    is_consistent= True if "closed" in label else False

    side= params["side"]
    
    if "open" in label:
        
        if side == "sell":
            is_consistent= True if ("Short" in label or "hedging" in label)\
                else False
                
        if side == "buy":
            is_consistent= True if "Long" in label else False

    return  is_consistent

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
    
    def get_basic_opening_parameters(
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

        side: str = strategy_config["side"]

        params.update({"side": side})
        
        try:
            cancellable= strategy_config["cancellable"]
        except:
            cancellable= False

        # get transaction label and update the respective parameters
        params.update({"cancellable": cancellable})
        label_open: str = get_label("open", self.strategy_label)
        params.update({"label": label_open})
        
        if side == "sell":
            params.update({"entry_price": ask_price})
                
        if side == "buy":
            params.update({"entry_price": bid_price})

        params.update({"everything_is_consistent": is_everything_consistent(params
                                 )})
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
        self, market_condition: dict, ask_price: float, bid_price: float, selected_transaction: list
    ) -> dict:
        """
        """
        # transform to dict
        transaction: dict = selected_transaction[0]

        # get price
        last_transaction_price: float = transaction["price"]

        transaction_side: str = transaction["direction"]

        strategy_config: list = self.get_strategy_config(transaction["label"])

        # get transaction parameters
        params: list = get_basic_closing_paramaters(selected_transaction)

        supported_by_market: bool= False

        # get take profit pct
        try:
            tp_pct: float = transaction["profit_target_pct_transaction"]
        except:
            tp_pct: float = strategy_config["take_profit_pct"]

        if transaction_side == "sell":
            tp_price_reached: bool = is_transaction_price_minus_below_threshold(
                last_transaction_price, bid_price, tp_pct
            )
            
            supported_by_market: bool= market_condition["falling_price"]\
            and bid_price<last_transaction_price
            print(f"transaction_side {transaction_side} supported_by_market {supported_by_market} last_transaction_price {last_transaction_price}")
            params.update({"entry_price": bid_price})

        if transaction_side == "buy":
            tp_price_reached: bool = is_transaction_price_plus_above_threshold(
                last_transaction_price, ask_price, tp_pct
            )
            supported_by_market: bool= market_condition["rising_price"]\
            and ask_price > last_transaction_price
            print(f"transaction_side {transaction_side} supported_by_market {supported_by_market} last_transaction_price {last_transaction_price}")
            params.update({"entry_price": ask_price})

        orders = await self.transaction_attributes("orders_all_json", "closed")

        len_orders: int = orders["transactions_len"]

        no_outstanding_order: bool = len_orders == 0

        order_allowed: bool = (tp_price_reached or supported_by_market) and no_outstanding_order

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
