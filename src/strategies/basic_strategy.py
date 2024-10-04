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
    executing_query_based_on_currency_or_instrument_and_strategy as get_query)
from utilities.string_modification import (
    parsing_label)
from loguru import logger as log


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


def positions_and_orders(current_size: int, 
                             current_orders_size: int) -> int:
    """ """

    return current_size + current_orders_size


def ensure_sign_consistency(side) -> float:
    """ """
    return -1 if side == "sell" else 1

def proforma_size(
    current_size: int, current_orders_size: int, 
    next_orders_size: int
) -> int:
    """ """

    return (
        positions_and_orders(current_size, current_orders_size) + next_orders_size #the sign is +
    )

def are_size_and_order_appropriate(
    purpose: str,
    current_size_or_open_position: float, 
    current_orders_size: int, 
    next_orders_size: int, 
    max_position: float= None) -> bool:
    """ 
    purpose: add_position/reduce_position
    for reduce: open position/individual trade
    for add: current position
    """
    
    proforma  = proforma_size(current_size_or_open_position, current_orders_size, next_orders_size) 
    ordering_is_ok= False
        
    if purpose=="add_position":
    
        if max_position < 0:
            ordering_is_ok= (proforma) > (max_position)
        
        if max_position > 0:
            ordering_is_ok= (proforma) < (max_position) 
        
    if purpose=="reduce_position":
    
        if current_size_or_open_position < 0:
            ordering_is_ok = proforma > current_size_or_open_position
        
        if current_size_or_open_position > 0:
            ordering_is_ok = proforma < current_size_or_open_position
    log.debug (f"ordering_is_ok  {ordering_is_ok} current_size_or_open_position  {current_size_or_open_position} proforma  {proforma} max_position  {max_position} current_orders_size  {current_orders_size} next_orders_size  {next_orders_size} ")
        
    return ordering_is_ok


def size_rounding(instrument_name: str, 
                  futures_instruments, 
                  proposed_size: float) -> int:
    """ """

    min_trade_amount=  [o["min_trade_amount"] for o in futures_instruments if o["instrument_name"]== instrument_name][0]    
    
    rounded_size= round(proposed_size/min_trade_amount)*min_trade_amount
    
    return (max(min_trade_amount, rounded_size)) #size is never 0


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
    #log.info (f"delta_time(server_time, time_stamp) {delta_time(server_time, time_stamp)} time_threshold {time_threshold} {delta_time(server_time, time_stamp)> time_threshold}")
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

def get_transaction_side(transaction: dict) -> str:
    """ 
    status: open/closed
    """
        
    try:
        return  transaction["direction"] 
    
    except:        
        return transaction["side"]
    

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

def get_label_integer(label: dict) -> bool:
    """ """

    return parsing_label(label)["int"]


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


def check_if_id_has_used_before(combined_result: str,
                                id_checked: str,
                                transaction_id: str) -> bool:
    """ 
    id_checked: order_id, trade_id, label
    
    verifier: order_id or label?
    - order_id only one per order 
    - one label could be processed couple of time (especially when closing the transactions)
    """

    id=f"{id_checked}"
    if combined_result !=[]:
        result_order_id= [o[id] for o in combined_result]

    label_is_exist: list = (False if (combined_result == [] or result_order_id== [])\
        else False if transaction_id not in result_order_id  else True)

    #log.debug (f"trasaction was existed before {label_is_exist}")
    return label_is_exist


def provide_side_to_close_transaction(transaction: dict) -> str:
    """ """

    # determine side
    transaction_side = get_transaction_side(transaction)
    
    if transaction_side == "sell":
        side = "buy"
        
    if transaction_side == "buy":
        side = "sell"

    return side


def sum_order_under_closed_label_int (closed_orders_label_strategy: list,
                                       label_integer_open: int) -> int:
    """ """
    
    if closed_orders_label_strategy:
        order_under_closed_label_int = ([o for o in closed_orders_label_strategy \
        if label_integer_open in o["label"]])
                
    return 0 if (closed_orders_label_strategy ==[] \
        or order_under_closed_label_int == []) \
            else sum([o["amount"] for o in order_under_closed_label_int])
                
def check_if_closing_size_will_exceed_the_original (basic_size: int,
                                                    combined_size: int,
                                                    sum_order_under_closed_label: int) -> bool:
    """ """
    if basic_size > 0:
        summing_ok = (basic_size) + (combined_size) <  (basic_size)
    if basic_size < 0:
        summing_ok = (basic_size) + (combined_size) > (basic_size)
    
    log.error (f" summing_ok {summing_ok} combined_size {basic_size} basic_size {basic_size}")
    return  abs(combined_size) < abs (basic_size) \
        and abs (sum_order_under_closed_label) < abs (basic_size) \
            and summing_ok
    
def provide_size_to_close_transaction (transaction: dict,
                                       closed_orders_label_strategy: list) -> int:
    """ """
    basic_size = get_transaction_size(transaction)
    
    label_integer_open = get_label_integer(transaction ["label"])
    
    sum_order_under_closed_label = sum_order_under_closed_label_int (
        closed_orders_label_strategy,
        label_integer_open)
                                       
    combined_size = (basic_size + sum_order_under_closed_label)
    log.error (f"combined_size {combined_size} sum_order_under_closed_label {sum_order_under_closed_label} label_integer_open {label_integer_open} ")
    closing_size_not_ok = check_if_closing_size_will_exceed_the_original (basic_size,
                                                                          combined_size,
                                                                          sum_order_under_closed_label)
                                
    return 0 if closing_size_not_ok else (min (basic_size, combined_size))

def convert_list_to_dict (transaction: list) -> dict:

    #convert list to dict
    try:
        return transaction[0]
    except:
        return transaction

def get_additional_params_for_futureSpread_transactions(transaction: list) -> None:
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


    log.debug (f"trade {transaction}")
    
    #convert list to dict
    transaction = convert_list_to_dict(transaction)
        
    timestamp= transaction["timestamp"]
    
    #get label
    
    if "futureSpread" not in transaction:
        label= combine_vars_to_get_future_spread_label(timestamp)
        transaction.update({"label":label})

    if "take_profit" not in transaction:
        transaction.update({"take_profit": 0})
        

async def get_additional_params_for_open_label(transaction: list, label: str) -> None:

    #convert list to dict
    transaction= convert_list_to_dict(transaction)
    
    #already have label, but not "futureSpreads"
    if "combo_id" in transaction:
        get_additional_params_for_futureSpread_transactions(transaction)

    additional_params = querying_additional_params()
    
    log.info (f"trade {transaction}")

    params = await executing_query_with_return(additional_params)
    
    #log.error (f""""label" not in trade {"label" not in transaction} label is None {label is None}""")
    
    # provide label
    if "label" not in transaction or label is None:
        side= get_transaction_side(transaction)
        label_open: str = get_label("open", f"custom{side.title()}")
        transaction.update({"label": label_open})
        
    additional_params_label = [] if params == [] else [o for o in params if label in o["label"]]
    
    log.error (f"additional_params_label {additional_params_label}")
    
    if additional_params_label !=[]:
        if "take_profit" not in transaction:
            try:
                transaction.update({"take_profit": additional_params_label["take_profit"]})
            
            except:
                transaction.update({"take_profit": 0})
    else:

        if "take_profit" not in transaction:
            transaction.update({"take_profit": 0})
            
    
async def get_basic_closing_paramaters(selected_transaction: list,
                                       closed_orders_label_strategy: list) -> dict:
    """ """
    transaction: dict = convert_list_to_dict(selected_transaction)
    
    # provide dict placeholder for params
    params = {}

    # default type: limit
    params.update({"type": "limit"})

    # determine side
    
    side = provide_side_to_close_transaction(transaction)
    params.update({"side": side})

    size_abs = provide_size_to_close_transaction(transaction,
                                                 closed_orders_label_strategy)
    log.debug (f"size_abs {size_abs}")
    log.debug (f"side {side}")
    size = size_abs * ensure_sign_consistency(side)
    # size=exactly amount of transaction size
    params.update({"size": size })

    label_closed: str = get_label("closed", transaction["label"])
    params.update({"label": label_closed})
    
    params.update({"instrument": transaction ["instrument_name"]})
    #log.info(f"params {params}")
        
    return params

def is_label_and_side_consistent(params) -> bool:
    """ """
    
    #log.error (f"params {params}")
    label = get_transaction_label(params)

    is_consistent = True if "closed" in label else False
    # log.warning(f"params {params}")

    if "open" in label:
        
        side = get_transaction_side(params)

        if side == "sell":
            is_consistent = True if ("Short" in label or "hedging" in label or "future" in label) else False

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
    #
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
    strategy_parameters: list

    def get_strategy_config(self, strategy_label: str = None) -> dict:
        """ """

        params: list = self. strategy_parameters
        
        if strategy_label != None:
            str_config: dict = [
                o for o in params if self.strategy_label in o["strategy_label"]
            ][0]

        else:
            str_config: dict = [
                o
                for o in params
                if parsing_label(self.strategy_label)["main"] in o["strategy_label"]
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

        if side == "sell":
            params.update({"entry_price": ask_price})

        if side == "buy":
            params.update({"entry_price": bid_price})
        
        if "hedgingSpot" not in self.strategy_label:
            params.update({"everything_is_consistent": are_size_and_order_appropriate (params)})
            label_open: str = get_label("open", self.strategy_label)
            params.update({"label": label_open})
     
        return params

    async def is_send_exit_order_allowed(
        self,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
        closed_orders_label_strategy
    ) -> dict:
        """ """
        # transform to dict
        transaction: dict = convert_list_to_dict(selected_transaction)

        transaction_side: str = get_transaction_side(transaction)

        strategy_config: list = self.get_strategy_config(
            get_transaction_label(transaction)
        )
        
        instrument_name= get_transaction_instrument(transaction)

        # get transaction parameters
        params: list = get_basic_closing_paramaters(selected_transaction)

        size_abs =  provide_size_to_close_transaction(transaction,
                                                      closed_orders_label_strategy)
        size = size_abs * ensure_sign_consistency(transaction_side)
        
        if transaction_side == "sell":
            params.update({"entry_price": bid_price})

        if transaction_side == "buy":
            params.update({"entry_price": ask_price})

        params.update({"instrument": instrument_name})
        params.update({"size": size})
        #log.info(f"params {params}")
        label = params["label"]
            

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
        )
