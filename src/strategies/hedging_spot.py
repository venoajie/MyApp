# # -*- coding: utf-8 -*-

# built ins
import asyncio
from loguru import logger as log
# installed
from dataclassy import dataclass
#from strategies.config_strategies import hedging_spot_attributes

# user defined formula
from strategies.basic_strategy import (
    BasicStrategy,
    are_size_and_order_appropriate,
    check_if_id_has_used_before,
    delta_pct,
    ensure_sign_consistency,
    get_basic_closing_paramaters,
    get_label,
    get_max_time_stamp,
    get_order_id_max_time_stamp,
    is_label_and_side_consistent,
    is_minimum_waiting_time_has_passed,
    size_rounding,)
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query
    )
from utilities.string_modification import (
    extract_currency_from_text,
    parsing_label)

def get_transactions_len(result_strategy_label) -> int:
    """ """
    return 0 if result_strategy_label == [] else len([o for o in result_strategy_label])

def get_transactions_sum(result_strategy_label) -> int:
    """ """
    return 0 if result_strategy_label == [] else sum([o["amount"] for o in result_strategy_label])


def get_label_integer(label: dict) -> bool:
    """ """

    return parsing_label(label)["int"]


def hedged_value_to_notional(notional: float, 
                             hedged_value: float) -> float:
    """ """
    return abs(hedged_value / notional)


def determine_opening_size(instrument_name: str, 
                           futures_instruments,
                           side: str, 
                           max_position: float, 
                           factor: float) -> int:
    """ """
    sign = ensure_sign_consistency(side)
    
    proposed_size= max(1, int(abs(max_position) * factor)) 
    
    return size_rounding(instrument_name, futures_instruments, proposed_size) * sign

def get_waiting_time_factor(weighted_factor, 
                            strong_fluctuation: bool, 
                            some_fluctuation: bool,) -> float:
    """
    Provide factor for size determination.
    """

    ONE_PCT = 1 / 100
    
    BEARISH_FACTOR = weighted_factor["extreme"] * ONE_PCT if strong_fluctuation else weighted_factor["medium"]  * ONE_PCT

    return BEARISH_FACTOR if (strong_fluctuation or some_fluctuation) else ONE_PCT


def is_hedged_value_to_notional_exceed_threshold(
    notional: float, hedged_value: float, threshold: float
) -> float:
    """ """
    return hedged_value_to_notional(notional, hedged_value) > threshold


def max_order_stack_has_not_exceeded(
    len_orders: float, 
    strong_market: float) -> bool:
    """ """
    if strong_market:
        max_order = True
        
    else:
        max_order = True if len_orders == 0 else False
    
    return max_order


def get_timing_factor(strong_bearish: bool, bearish: bool, threshold: float) -> bool:
    """
    Determine order outstanding timing for size determination.
    strong bearish : 30% of normal interval
    bearish        : 6% of normal interval
    """

    ONE_PCT = 1 / 100

    ONE_MINUTE: int = 60000

    bearish_interval_threshold = (
        (threshold * ONE_PCT * 30) if strong_bearish else (threshold * ONE_PCT * 60)
    )
    
    #print (f"bearish_interval_threshold {bearish_interval_threshold} {ONE_MINUTE * bearish_interval_threshold if (strong_bearish or bearish) else ONE_MINUTE *  threshold}")

    return (
        ONE_MINUTE * bearish_interval_threshold
        if (strong_bearish or bearish)
        else ONE_MINUTE *  threshold
    )


def is_cancelling_order_allowed(
    strong_bullish: bool,
    bullish: bool,
    threshold: float,
    len_orders: int,
    open_orders_label_strategy: dict,
    server_time: int,
) -> bool:
    """ """

    cancel_allowed: bool = False

    if len_orders != [] and len_orders > 0:

        time_interval = get_timing_factor(strong_bullish, bullish, threshold)

        max_tstamp_orders: int = get_max_time_stamp(open_orders_label_strategy)
        
        minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed (
            server_time, max_tstamp_orders, time_interval
        )
        if minimum_waiting_time_has_passed:
            cancel_allowed: bool = True

    return cancel_allowed


async def get_market_condition_hedging(currency,TA_result_data, index_price, threshold) -> dict:
    """ """
    neutral_price, rising_price, falling_price = False, False, False
    strong_rising_price, strong_falling_price = False, False
    
    TA_data=[o for o in TA_result_data if o["tick"] == max([i["tick"] for i in TA_result_data])][0]

    open_60 = TA_data["60_open"]

    fluctuation_exceed_threshold = TA_data["1m_fluctuation_exceed_threshold"]

    delta_price_pct = delta_pct(index_price, open_60)
    
    if fluctuation_exceed_threshold or True:

        if index_price > open_60:
            rising_price = True

            if delta_price_pct > threshold:
                strong_rising_price = True

        if index_price < open_60:
            falling_price = True

            if delta_price_pct > threshold:
                strong_falling_price = True

    if rising_price == False and falling_price == False:
        neutral_price = True

    return dict(
        rising_price=rising_price,
        strong_rising_price=strong_rising_price,
        neutral_price=neutral_price,
        falling_price=falling_price,
        strong_falling_price=strong_falling_price,
    )

@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):
    """ """

    def get_basic_params(self) -> dict:
        """ """
        return BasicStrategy(self.strategy_label, 
                             self.strategy_parameters)

    async def is_send_and_cancel_open_order_allowed(
        self,
        currency,
        instrument_name: str,
        futures_instruments,
        sum_my_trades_currency_strategy_open: int,
        orders_currency_strategy: list,
        max_position: float,
        index_price,
        ask_price: float,
        server_time: int,
        TA_result_data: dict
    ) -> dict:
        """ """

        ONE_SECOND,  ONE_MINUTE = 1000, 60000
                
        order_allowed, cancel_allowed, cancel_id = False, False, None
        
        open_orders_label_strategy: list=  [o for o in orders_currency_strategy if "open" in o["label"]]
        
        len_orders: int = get_transactions_len(open_orders_label_strategy)

        hedging_attributes= self.strategy_parameters[0]
        
        threshold_market_condition= hedging_attributes ["delta_price_pct"]
        
        market_condition = await get_market_condition_hedging(currency,
                                                              TA_result_data, 
                                                              index_price, 
                                                              threshold_market_condition)

        #bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]

        #strong_bullish = market_condition["strong_rising_price"]
        strong_bearish = market_condition["strong_falling_price"]
        #neutral = market_condition["neutral_price"]
        params: dict = self.get_basic_params().get_basic_opening_parameters(ask_price)
        
        weighted_factor= hedging_attributes["weighted_factor"]

        waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"] * ONE_MINUTE
                               
        if len_orders == 0:
            fluctuation_exceed_threshold = True#TA_result_data["1m_fluctuation_exceed_threshold"]

            SIZE_FACTOR = get_waiting_time_factor(weighted_factor, strong_bearish, bearish)

            size = determine_opening_size(instrument_name, 
                                        futures_instruments, 
                                        params["side"], 
                                        max_position, 
                                        SIZE_FACTOR)

            
            #log.debug (f"open_orders_label_strategy {open_orders_label_strategy}")

            
            sum_orders: int = get_transactions_sum(open_orders_label_strategy)
            
            #log.info  (f"params {params} max_position {max_position}")
            
            size_and_order_appropriate_for_ordering: bool = (
                are_size_and_order_appropriate (
                    "add_position",
                    sum_my_trades_currency_strategy_open, 
                    sum_orders, 
                    size, 
                    max_position
                )
            )
            
            order_allowed: bool = (
                    size_and_order_appropriate_for_ordering
                    and (bearish or strong_bearish)
                    and fluctuation_exceed_threshold
                )
            
            if order_allowed :
                label_open: str = get_label("open", self.strategy_label)
                params.update({"label": label_open})
                label_and_side_consistent= is_label_and_side_consistent(params)
                        
                #order_has_sent_before =  check_if_id_has_used_before (combined_result, "label", params["label"])
                
                if label_and_side_consistent:# and not order_has_sent_before:
                    
                    params.update({"size": abs(size)})
                    params.update({"is_label_and_side_consistent": label_and_side_consistent})
                            
                else:
                    
                    order_allowed=False
        
        else:
            
            cancel_allowed: bool = is_cancelling_order_allowed(
                strong_bearish,
                bearish,
                waiting_minute_before_cancel,
                len_orders,
                open_orders_label_strategy,
                server_time,
            )


        return dict(
            order_allowed=order_allowed and len_orders == 0,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=get_order_id_max_time_stamp(open_orders_label_strategy)
        )


    async def is_send_exit_order_allowed(
        self,
        TA_result_data,
        max_position,
        sum_my_trades_currency_strategy,
        orders_currency_strategy_label_closed,
        index_price: float,
        bid_price: float,
        selected_transaction: list,
        server_time: int
    ) -> dict:
        """
        

        Args:
            TA_result_data (_type_): _description_
            index_price (float): _description_
            bid_price (float): _description_
            selected_transaction (list): example [  
                                                {'instrument_name': 'BTC-PERPETUAL', 
                                                'label': 'hedgingSpot-open-1726878876878', 
                                                'amount': -10.0, 
                                                'price': 63218.0, 
                                                'side': 'sell', 
                                                'has_closed_label': 0}
                                                    ]
            server_time (int): _description_

        Returns:
            dict: _description_
        """
        order_allowed, cancel_allowed, cancel_id = False, False, None
        
        transaction = selected_transaction[0]
        
        log.warning (f"sum_my_trades_currency_strategy {sum_my_trades_currency_strategy} max_position {max_position}")
        
        current_position_exceed_max_position =  abs(sum_my_trades_currency_strategy) > abs(max_position) or sum_my_trades_currency_strategy > 0
        
        if current_position_exceed_max_position:
            exit_params: dict = await get_basic_closing_paramaters (selected_transaction,
                                                                    orders_currency_strategy_label_closed,)                       
            exit_params.update({"entry_price": bid_price})
                
            #convert size to positive sign
            exit_params.update({"size": abs (exit_params["size"])})
            log.info (f"exit_params {exit_params}")
            
            if bid_price < transaction ["price"]:
                order_allowed = True

        else:
                        
            hedging_attributes = self.strategy_parameters[0]
            
            currency = extract_currency_from_text(transaction ["instrument_name"]).lower()

            threshold_market_condition = hedging_attributes ["delta_price_pct"]
            
            market_condition = await get_market_condition_hedging (currency,
                                                                TA_result_data, 
                                                                index_price, 
                                                                threshold_market_condition)

            bullish, strong_bullish = market_condition["rising_price"], market_condition["strong_rising_price"]
            
            exit_params: dict = await get_basic_closing_paramaters (selected_transaction,
                                                                    orders_currency_strategy_label_closed,)
                
            size = exit_params["size"]      
            #log.info (f"exit_params {exit_params}")
            order_allowed: bool = True if size != 0 else False
            
            if order_allowed:
                
                if (bullish or strong_bullish) \
                    and bid_price < transaction ["price"]:
                
                    
                    len_orders: int = get_transactions_len(orders_currency_strategy_label_closed)
                    
                    ONE_SECOND = 1000
                    ONE_MINUTE = ONE_SECOND * 60
                    
                    waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"] * ONE_MINUTE

                    cancel_allowed: bool = is_cancelling_order_allowed(
                        strong_bullish,
                        bullish,
                        waiting_minute_before_cancel,
                        len_orders,
                        orders_currency_strategy_label_closed,
                        server_time,)
                        
                    if cancel_allowed:
                        cancel_id= min ([o["order_id"] for o in orders_currency_strategy_label_closed])  
                        
                    log.error (f"closed_orders_label_strategy {orders_currency_strategy_label_closed}")

                    #max_order = max_order_stack_has_not_exceeded (len_orders, bullish)
                        
                
                    if (False if size == 0 else True) and len_orders == 0:# and max_order:
                        
                        
                        exit_params.update({"entry_price": bid_price})
                            
                        #convert size to positive sign
                        exit_params.update({"size": abs (size)})
                    
        #log.error (f"order_allowed {order_allowed}")
        #log.info (f"cancel_allowed {cancel_allowed} ")
        return dict(
            order_allowed= order_allowed,
            order_parameters=(
                [] if order_allowed == False else exit_params
            ),
            cancel_allowed=cancel_allowed,
            cancel_id=cancel_id
        )
