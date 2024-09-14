# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from db_management.sqlite_management import (
    querying_hlc_vol,
    executing_query_with_return,
    querying_ohlc_price_vol,
    querying_additional_params,
    querying_table,
    executing_query_based_on_currency_or_instrument_and_strategy
)
from utilities.string_modification import parsing_label,extract_currency_from_text,remove_redundant_elements,remove_double_brackets_in_list
from loguru import logger as log
from utilities.pickling import (
    read_data)
from utilities.system_tools import (
    provide_path_for_file)


async def get_hlc_vol(window: int = 9, table: str = "ohlc1_eth_perp_json") -> list:
    """ """

    # get query for close price
    get_ohlc_query = querying_hlc_vol(table, window)

    # executing query above
    ohlc_all = await executing_query_with_return(get_ohlc_query)
    # log.info(ohlc_all)

    return ohlc_all


async def get_price_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    get_ohlc_query = querying_ohlc_price_vol(price, table, window)

    # executing query above
    ohlc_all = await executing_query_with_return(get_ohlc_query)

    return ohlc_all


async def cleaned_up_ohlc(
    price: str = "close", window: int = 100, table: str = "ohlc1_eth_perp_json"
) -> list:
    """ """

    # get query for close price
    ohlc_all = await get_price_ohlc(price, window, table)

    # pick value only
    ohlc = [o[price] for o in ohlc_all]

    ohlc.reverse()

    return dict(ohlc=ohlc[: window - 1], last_price=ohlc[-1:][0])


async def get_ema(ohlc, ratio: float = 0.9) -> dict:
    """
    https://stackoverflow.com/questions/488670/calculate-exponential-moving-average-in-python
    https://stackoverflow.com/questions/59294024/in-python-what-is-the-faster-way-to-calculate-an-ema-by-reusing-the-previous-ca
    """

    return round(
        sum([ratio * ohlc[-x - 1] * ((1 - ratio) ** x) for x in range(len(ohlc))]), 2
    )


async def get_vwap(ohlc_all, vwap_period) -> dict:
    """
    https://github.com/vishnugovind10/emacrossover/blob/main/emavwap1.0.py
    https://stackoverflow.com/questions/44854512/how-to-calculate-vwap-volume-weighted-average-price-using-groupby-and-apply

    """
    import numpy as np
    import pandas as pd

    df = pd.DataFrame(ohlc_all, columns=["close", "volume"])

    return (
        df["volume"]
        .rolling(window=vwap_period)
        .apply(lambda x: np.dot(x, df["close"]) / x.sum(), raw=False)
    )


def size_rounding(instrument_name: str, proposed_size: float) -> int:
    """ """

    currency=extract_currency_from_text(instrument_name).upper()

    instruments= get_instruments_kind(currency, "all")

    min_trade_amount=  [o["min_trade_amount"] for o in instruments if o["instrument_name"]== instrument_name][0]    
    
    rounded_size= round(proposed_size/min_trade_amount)*min_trade_amount
    
    return int(max(min_trade_amount, rounded_size)) #size is never 0


def delta(last_price: float, prev_price: float) -> float:
    """ """
    return last_price - prev_price


def delta_pct(last_price: float, prev_price: float) -> float:
    """ """
    return abs(delta(last_price, prev_price) / prev_price)


async def get_market_condition(
    limit: int = 100, table: str = "ohlc1_eth_perp_json"
) -> dict:
    """ """
    rising_price, falling_price, neutral_price = False, False, False

    TA_result = await querying_table("market_analytics_json-last")
    TA_result_data = TA_result["list_data_only"][0]

    ema_short = TA_result_data["1m_ema_close_9"]
    ema_long = TA_result_data["1m_ema_close_20"]
    ema_low_9 = TA_result_data["1m_ema_low_9"]
    ema_high_9 = TA_result_data["1m_ema_high_9"]

    ema = TA_result_data["1m_ema_close_9"]

    #    log.error(f'ema_low_9 {ema_low_9}')
    delta_price_pct_ema_low_high = delta_pct(ema_low_9, ema_high_9)

    last_price = TA_result_data["last_price"]

    if last_price > ema_short and ema_short > ema_long:
        rising_price = True

    if last_price < ema_short and ema_short < ema_long:
        falling_price = True

    if rising_price == False and falling_price == False:
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
        label_id: int = parsing_label(label_main_or_label_transactions)["int"]

        # parsing label strategy
        label_main: str = parsing_label(label_main_or_label_transactions)["main"]

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
    print (f"delta_time(server_time, time_stamp) {delta_time(server_time, time_stamp)} time_threshold {time_threshold} {delta_time(server_time, time_stamp)> time_threshold}")
    return (
        True
        if time_stamp == []
        
        else delta_time(server_time, time_stamp) > time_threshold
    )
    
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
    """ """
    return (
        []
        if result_strategy_label == []
        else max([o["timestamp"] for o in result_strategy_label])
    )


def get_order_id_max_time_stamp(result_strategy_label) -> int:
    """ """
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
    """ """
    return 0 if result_strategy_label == [] else len([o for o in result_strategy_label])


def get_transactions_sum(result_strategy_label) -> int:
    """
    summing transaction under SAME strategy label
    """
    return (
        0
        if result_strategy_label == []
        else sum([o["amount"] for o in result_strategy_label])
    )


def get_settlement_period () -> list:
    from strategies.config_strategies import hedging_spot_attributes, strategies
    
    return (remove_redundant_elements(remove_double_brackets_in_list([o["settlement_period"]for o in (strategies+hedging_spot_attributes())])))


def get_instruments_kind(currency: str, kind: str= "all") -> list:
    """_summary_

    Args:
        currency (str): _description_
        kind (str): "future_combo",  "future"
        Instance:  [
                    {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1,'counter_currency': 'USD', 
                    'settlement_period': 'month', 'settlement_currency': 'ETH', 'creation_timestamp': 1719564006000, 
                    'instrument_id': 342036, 'base_currency': 'ETH', 'tick_size': 0.05, 'contract_size': 1, 'is_active': True, 
                    'expiration_timestamp': 1725004800000, 'instrument_type': 'reversed', 'taker_commission': 0.0, 
                    'maker_commission': 0.0, 'instrument_name': 'ETH-FS-27SEP24_30AUG24', 'kind': 'future_combo', 
                    'rfq': False, 'price_index': 'eth_usd'}, ]
     Returns:
        list: _description_
        
        
    """ 
    
    my_path_instruments = provide_path_for_file(
        "instruments", currency
    )

    instruments_raw = read_data(my_path_instruments)
    instruments = instruments_raw[0]["result"]
    non_spot_instruments=  [
        o for o in instruments if o["kind"] != "spot"]
    instruments_kind= non_spot_instruments if kind =="all" else  [
        o for o in instruments if o["kind"] == kind]
    
    settlement_periods= get_settlement_period()
    
    return  [o for o in instruments_kind if o["settlement_period"] in settlement_periods]


def get_transaction_side(transaction: dict) -> str:
    """ """

    try:
        side = transaction["direction"]

    except:
        try:
            
            side = transaction["side"]

        except:
            side = "sell" if transaction["amount"]< 0 else "buy"

    return side


def provide_side_to_close_transaction(transaction: dict) -> str:
    """ """

    # determine side
    transaction_side = get_transaction_side(transaction)
    if transaction_side == "sell":
        side = "buy"
    if transaction_side == "buy":
        side = "sell"

    return side


def get_transaction_size(transaction: dict) -> int:
    """ """
    return transaction["amount"]


def get_transaction_instrument(transaction: dict) -> int:
    """ """
    return transaction["instrument_name"]


def get_transaction_label(transaction: dict) -> str:
    """ """
    return transaction["label"]


def get_transaction_price(transaction: dict) -> float:
    """ """
    return transaction["price"]


def has_closed_label(transaction: dict) -> bool:
    """ """
    return transaction["has_closed_label"]


def get_label_integer(label: dict) -> bool:
    """ """

    return parsing_label(label)


def get_order_label(data_from_db: list) -> list:
    """ """

    return [o["label"] for o in data_from_db]

def get_label_super_main(result: list, strategy_label) -> list:
    """ """

    return [o for o in result if parsing_label(strategy_label)["super_main"]
                    == parsing_label(o["label"])["super_main"]
                ]

def combine_vars_to_get_future_spread_label(timestamp: int) -> str:
    """ """

    return f"futureSpread-open-{timestamp}"


async def check_if_id_has_used_before(instrument_name: str,
                                      id_checked: str,
                                      transaction_id: str, 
                                      max_transactions_for_closed_label: int= 100) -> bool:
    """ 
    id_checked: order_id, trade_id, label
    
    verifier: order_id or label?
    - order_id only one per order 
    - one label could be processed couple of time (especially when closing the transactions)
    """
    if id_checked=="order_id":
        column= "order_id","label"
    if id_checked=="trade_id":
        column= "trade_id","label"
    if id_checked=="label":
        column= "label","order_id"
    
    data_from_db_trade_open = await executing_query_based_on_currency_or_instrument_and_strategy("my_trades_all_json", 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column)     
    
    data_from_db_order_open = await executing_query_based_on_currency_or_instrument_and_strategy("orders_all_json", 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column)     
    
    data_from_db_trade_closed = await executing_query_based_on_currency_or_instrument_and_strategy("my_trades_closed_json", 
                                                                                            instrument_name, 
                                                                                            "all", 
                                                                                            "all", 
                                                                                            column,
                                                                                            max_transactions_for_closed_label, 
                                                                                            "id") 
    
    combined_result = data_from_db_trade_open + data_from_db_trade_closed + data_from_db_order_open
    id=f"{id_checked}"
    
    result_order_id= [o[id] for o in combined_result]
    
    label_is_exist: list = (False if transaction_id not in result_order_id  else True)

    #log.debug (f"trasaction was existed before {label_is_exist}")
    return label_is_exist


async def summing_transactions_under_label_int(
    transaction: dict, transactions_all: list = None
) -> str:
    """ """
    
    label = get_transaction_label(transaction)

    label_integer = get_label_integer(label)["int"]
    
    if transactions_all is None:
        tabel= "my_trades_all_json"
        column_list: str= "label", "amount"
        instrument_name= get_transaction_instrument(transaction)
        transactions_all: list = await executing_query_based_on_currency_or_instrument_and_strategy(tabel, 
                                                                                         instrument_name, 
                                                                                         "all", 
                                                                                         "all", 
                                                                                         column_list)
    transactions_under_label_main = [
        o["amount"] for o in transactions_all if label_integer in o["label"]
    ]

    return sum(transactions_under_label_main)


async def provide_size_to_close_transaction(
    transaction: dict, transactions_all: list = None
) -> str:
    """ """
    basic_size = get_transaction_size(transaction)
    label = get_transaction_label(transaction)
    has_closed = 0
    # print(f"transaction {transaction}")

    if "open" in label:
        has_closed = has_closed_label(transaction)

    sum_transactions_under_label_main = await summing_transactions_under_label_int(
        transaction, transactions_all
    )

    return abs(basic_size if (has_closed == 0) else (sum_transactions_under_label_main))


async def get_additional_params_for_futureSpread_transactions(trade: list) -> None:
    """ 
    send order:
    {'is_liquidation': False, 'risk_reducing': False, 'creation_timestamp': 1724306764758, 'order_type': 'market', 
     'order_state': 'filled', 'contracts': 1.0, 'average_price': -0.6, 'reduce_only': False, 'post_only': False, 
     'last_update_timestamp': 1724306764758, 'filled_amount': 1.0, 'replaced': False, 'mmp': False, 
     'order_id': 'ETH-48095626085', 'amount': 1.0, 'web': False, 'api': True, 'instrument_name': 'ETH-FS-23AUG24_PERP', 
     'max_show': 1.0, 'time_in_force': 'good_til_cancelled', 'direction': 'sell', 'price': -11.45, 'label': 'futureSpread-123'}
    
    trades:
    {'liquidity': 'T', 'risk_reducing': False, 'order_type': 'market', 
    'trade_id': 'ETH-215726649', 'fee_currency': 'ETH', 'contracts': 0.0, 
    'reduce_only': False, 'self_trade': False, 'post_only': False,'mmp': False, 'tick_direction': 3,
    'matching_id': None, 'order_id': 'ETH-48108854807', 'fee': 0.0, 'mark_price': 0.15, 'amount': 1.0, 
    'api': False, 'trade_seq': 325, 'instrument_name': 'ETH-FS-23AUG24_PERP', 'profit_loss': None, 
    'index_price': 2611.71, 'direction': 'sell', 'price': -0.65, 'state': 'filled', 'timestamp': 1724334628439}
    
    {'liquidity': 'T', 'risk_reducing': False, 'order_type': 'limit', 'combo_trade_id': 'ETH-215711231', 
     'trade_id': 'ETH-215711232', 'fee_currency': 'ETH', 'contracts': 1.0, 'combo_id': 'ETH-FS-23AUG24_PERP', 
     'reduce_only': False, 'self_trade': False, 'post_only': False, 'mmp': False, 'tick_direction': 0, 
     'matching_id': None, 'order_id': 'ETH-48095626087', 'fee': 0.0, 'mark_price': 2624.63, 'amount': 1.0, 
     'api': False, 'trade_seq': 53960, 'instrument_name': 'ETH-23AUG24', 'profit_loss': 3.28e-06, 
     'index_price': 2625.7, 'direction': 'sell', 'price': 2624.85, 'state': 'filled', 'timestamp': 1724306764758, 
     'label': 'futureSpread-123'}
    
    {'liquidity': 'T', 'risk_reducing': False, 'order_type': 'limit', 'combo_trade_id': 'ETH-215711231', 
     'trade_id': 'ETH-215711233', 'fee_currency': 'ETH', 'contracts': 1.0, 'combo_id': 'ETH-FS-23AUG24_PERP', 
     'reduce_only': False, 'self_trade': False, 'post_only': False, 'mmp': False, 'tick_direction': 0, 
     'matching_id': None, 'order_id': 'ETH-48095626089', 'fee': 1.9e-07, 'mark_price': 2625.61, 'amount': 1.0, 
     'api': False, 'trade_seq': 157027471, 'instrument_name': 'ETH-PERPETUAL', 'profit_loss': -3.61e-06, 
     'index_price': 2625.7, 'direction': 'buy', 'price': 2625.45, 'state': 'filled', 'timestamp': 1724306764758, 
     'label': 'futureSpread-123'}
     
     approach for now: ignore orders
     
     """
     
    side= trade["direction"]
    side_buy= side=="buy"
    timestamp= trade["timestamp"] + 1 if side_buy else trade["timestamp"]-1
    
    #get label
    label= combine_vars_to_get_future_spread_label(timestamp)

    trade.update({"label":label})


async def get_additional_params_for_open_label(trade: list, label: str) -> None:

    additional_params = querying_additional_params()

    params = await executing_query_with_return(additional_params)
    
    log.error (f""""label" not in trade {"label" not in trade} label is None {label is None}""")
    
    if "label" not in trade or label is None:
        side= get_transaction_side(trade)
        label_open: str = get_label("open", f"custom{side.title()}")
        trade.update({"label": label_open})
        

    if params !=0:

        additional_params_label = [o for o in params if label in o["label"]][0]    
        
        if "take_profit" not in trade:
            trade.update({"take_profit": additional_params_label["take_profit"]})
            
        if "has_closed_label" not in trade:
            trade.update({"has_closed_label": False})
            
    else:

        if "take_profit" not in trade:
            trade.update({"take_profit": 0})
            
        if "has_closed_label" not in trade:
            trade.update({"has_closed_label": False})


def get_basic_closing_paramaters(selected_transaction: list) -> dict:
    """ """
    transaction: dict = selected_transaction[0]

    # provide dict placeholder for params
    params = {}

    # default type: limit
    params.update({"type": "limit"})

    # size=exactly amount of transaction size
    params.update({"size": transaction["amount"]})

    # determine side
    side = provide_side_to_close_transaction(transaction)
    params.update({"side": side})

    label_closed: str = get_label("closed", transaction["label"])
    params.update({"label": label_closed})

    return params


def get_strategy_config_all() -> list:
    """ """
    from strategies import config_strategies

    return config_strategies.strategies

def is_everything_consistent(params) -> bool:
    """ """
    
    #log.error (f"params {params}")
    label = get_transaction_label(params)

    is_consistent = True if "closed" in label else False
    # log.warning(f"params {params}")

    side = get_transaction_side(params)

    if "open" in label:

        if side == "sell":
            is_consistent = True if ("Short" in label or "hedging" in label) else False

        if side == "buy":
            is_consistent = True if "Long" in label else False

    return is_consistent


def get_take_profit_pct(transaction: dict, strategy_config: dict) -> float:
    """ """

    try:
        tp_pct: float = transaction["profit_target_pct_transaction"]
    except:
        tp_pct: float = strategy_config["take_profit_pct"]

    return tp_pct


def reading_from_pkl_database(end_point, currency, status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, currency, status)
    data = read_data(path)

    return data [0]


def reading_from_db(end_point, instrument: str = None, status: str = None) -> list:
    """ """
    from utilities import pickling, system_tools

    return pickling.read_data(
        system_tools.provide_path_for_file(end_point, instrument, status)
    )

def get_non_label_from_transaction(transactions) -> list:
    """ """


    return [] if transactions ==[] else [o for o in transactions if o["label"]==""]


def check_db_consistencies (instrument_name: str,
                            trades_from_sqlite: list, 
                            positions_from_sub_account: list,
                            order_from_sqlite_open: list, 
                            open_orders_from_sub_accounts: list) -> bool:
    """ """

    no_non_label_from_from_sqlite_open= False if get_non_label_from_transaction(order_from_sqlite_open) != [] else True 
    
    len_from_sqlite_open= len(order_from_sqlite_open)
    
    len_open_orders_from_sub_accounts=len(open_orders_from_sub_accounts)
    
    log.error (f"positions_from_sub_account {positions_from_sub_account}")
        
    sum_my_trades_sqlite = 0 if  trades_from_sqlite == [] else sum([o["amount"] for o in trades_from_sqlite])

    size_from_position: int = (0 if positions_from_sub_account == [] \
        else sum([o["size"] for o in positions_from_sub_account if o["instrument_name"]==instrument_name]))

    log.error(
        f"size_is_consistent {sum_my_trades_sqlite == size_from_position} sum_my_trades_sqlite {sum_my_trades_sqlite} size_from_positions {size_from_position} "
    )
    return dict(trade_size_is_consistent=sum_my_trades_sqlite == size_from_position,                
                order_is_consistent= (len_open_orders_from_sub_accounts == len_from_sqlite_open \
                    and no_non_label_from_from_sqlite_open),
                no_non_label_from_from_sqlite_open= False \
                    if get_non_label_from_transaction(order_from_sqlite_open) != [] else True )


@dataclass(unsafe_hash=True, slots=True)
class BasicStrategy:
    """ """

    strategy_label: str

    def get_strategy_config(self, strategy_label: str = None) -> dict:
        """ """

        params: list = get_strategy_config_all()

        if strategy_label != None:
            str_config: dict = [
                o for o in params if self.strategy_label in o["strategy"]
            ][0]

        else:
            str_config: dict = [
                o
                for o in params
                if parsing_label(self.strategy_label)["main"] in o["strategy"]
            ][0]

        return str_config

    def get_basic_opening_parameters(
        self, ask_price: float = None, bid_price: float = None, notional: float = None
    ) -> dict:
        """ """

        # provide placeholder for params
        params = {}

        # default type: limit
        params.update({"type": "limit"})

        strategy_config: dict = self.get_strategy_config()

        side: str = strategy_config["side"]

        params.update({"side": side})

        try:
            cancellable = strategy_config["cancellable"]
        except:
            cancellable = False
       
        # get transaction label and update the respective parameters
        params.update({"cancellable": cancellable})
        params.update({"has_closed_label": False})

        if side == "sell":
            params.update({"entry_price": ask_price})

        if side == "buy":
            params.update({"entry_price": bid_price})
        
        if "hedgingSpot" not in self.strategy_label:
            params.update({"everything_is_consistent": is_everything_consistent(params)})
            label_open: str = get_label("open", self.strategy_label)
            params.update({"label": label_open})
     
        return params

    async def is_send_exit_order_allowed(
        self,
        market_condition: dict,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
    ) -> dict:
        """ """
        # transform to dict
        transaction: dict = selected_transaction[0]

        # get price
        last_transaction_price: float = get_transaction_price(transaction)

        transaction_side: str = get_transaction_side(transaction)

        strategy_config: list = self.get_strategy_config(
            get_transaction_label(transaction)
        )
        
        instrument_name= get_transaction_instrument(transaction)

        # get transaction parameters
        params: list = get_basic_closing_paramaters(selected_transaction)

        supported_by_market: bool = False

        tp_pct = get_take_profit_pct(transaction, strategy_config)

        size = await provide_size_to_close_transaction(transaction)

        if transaction_side == "sell":
            try:
                tp_price_reached = bid_price < transaction["take_profit"]

            except:
                tp_price_reached: bool = is_transaction_price_minus_below_threshold(
                    last_transaction_price, bid_price, tp_pct
                )

            supported_by_market: bool = (
                market_condition["falling_price"] and bid_price < last_transaction_price
            )

            params.update({"entry_price": bid_price})

        if transaction_side == "buy":
            try:
                tp_price_reached = ask_price > transaction["take_profit"]

            except:
                tp_price_reached: bool = is_transaction_price_plus_above_threshold(
                    last_transaction_price, ask_price, tp_pct
                )
            supported_by_market: bool = (
                market_condition["rising_price"] and ask_price > last_transaction_price
            )

            params.update({"entry_price": ask_price})

        column_list= "amount",
        status= "closed"
        orders: list = await executing_query_based_on_currency_or_instrument_and_strategy("orders_all_json", 
                                                                                    instrument_name, 
                                                                                    self.strategy_label,
                                                                                    status,column_list)

        len_orders: int = get_transactions_len(orders)

        no_outstanding_order: bool = len_orders == 0

        order_allowed: bool = (
            tp_price_reached or supported_by_market
        ) and no_outstanding_order

        if order_allowed:
            params.update({"instrument": instrument_name})
            params.update({"size": size})
            #log.info(f"params {params}")
            label = params["label"]

            max_transactions= 100
            
            order_has_sent_before = await check_if_id_has_used_before (instrument_name, "label", label, max_transactions)

            if order_has_sent_before or size == 0:
                order_allowed = False
            # log.critical(
            #    f"order_allowed {order_allowed} size {size} order_has_sent_before {order_has_sent_before}  {order_has_sent_before or size==0}"
            # )

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
        )
