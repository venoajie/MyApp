# # -*- coding: utf-8 -*-

# built ins
import asyncio
from loguru import logger as log
# installed
from dataclassy import dataclass, fields

# user defined formula
from strategies.basic_strategy import (
    BasicStrategy,
    are_size_and_order_appropriate,
    delta_pct,
    ensure_sign_consistency,
    get_max_time_stamp,
    get_order_id_max_time_stamp,
    is_label_and_side_consistent,
    is_minimum_waiting_time_has_passed,
    size_rounding,)
from utilities.string_modification import (
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


async def get_market_condition_hedging(TA_result_data, index_price, threshold) -> dict:
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


def current_position_exceed_max_position (sum_my_trades_currency_str: int, max_position: float) -> bool:
    """ """
    
    return abs(sum_my_trades_currency_str) > abs(max_position) or sum_my_trades_currency_str > 0

@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):
    """ """
    
    max_position: float
    my_trades_currency_strategy: int
    TA_result_data: list
    index_price: float
    server_time: int
    sum_my_trades_currency_strategy: int= fields 
    over_hedged_opening: bool= fields 
    over_hedged_closing: bool= fields 

    def __post_init__(self):
        self.over_hedged_opening = current_position_exceed_max_position (self.sum_my_trades_currency_strategy, 
                                                                         self.max_position)        
        
        self.over_hedged_closing = self.sum_my_trades_currency_strategy > 0       
        self.sum_my_trades_currency_strategy =  get_transactions_sum (self.my_trades_currency_strategy)   
    
    async def get_basic_params(self) -> dict:
        """ """
        return BasicStrategy(self.strategy_label, 
                             self.strategy_parameters)

    async def understanding_the_market (self, threshold_market_condition) -> None:
        """ """       

    async def risk_managament (self) -> None:
        """ """
        pass
    
    def opening_position (self, 
                          instrument_name,
                          futures_instruments,
                          open_orders_label_strategy,
                          market_condition,
                          params,
                          SIZE_FACTOR,
                          len_orders) -> bool:
        """ """

        order_allowed: bool = False

        if len_orders == 0:
            #bullish = market_condition["rising_price"]
            bearish = market_condition["falling_price"]

            #strong_bullish = market_condition["strong_rising_price"]
            strong_bearish = market_condition["strong_falling_price"]                   
        
            max_position = self.max_position
        
            fluctuation_exceed_threshold = True#TA_result_data["1m_fluctuation_exceed_threshold"]

            size = determine_opening_size(instrument_name, 
                                        futures_instruments, 
                                        params["side"], 
                                        self.max_position, 
                                        SIZE_FACTOR)

            sum_orders: int = get_transactions_sum(open_orders_label_strategy)
            
            size_and_order_appropriate_for_ordering: bool = (
                are_size_and_order_appropriate (
                    "add_position",
                    self.sum_my_trades_currency_strategy, 
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
                
                label_and_side_consistent= is_label_and_side_consistent(params)
                
                if label_and_side_consistent:# and not order_has_sent_before:
                    
                    params.update({"size": abs(size)})
                    params.update({"is_label_and_side_consistent": label_and_side_consistent})
                            
                else:
                    
                    order_allowed=False

        return order_allowed

    def closing_position (self,
                          transaction,
                          exit_params,
                          bullish, 
                          strong_bullish,
                          over_hedged,
                          len_orders,
                          bid_price,
                          ) -> bool:
        """ """
        
        order_allowed: bool = False

        bid_price_is_lower = bid_price < transaction ["price"]
        
        if over_hedged :                       
            
            if  len_orders == 0:
                
                if bid_price_is_lower:
                    exit_params.update({"entry_price": bid_price})
                    
                    size = exit_params["size"]     
                    
                    log.warning (f"""size {size}""")
                    
                    if size != 0:    
                        #convert size to positive sign
                        exit_params.update({"size": abs (exit_params["size"])})
                        log.info (f"exit_params {exit_params}")
                        order_allowed = True
            else:     
                size = exit_params["size"]      
                #log.info (f"exit_params {exit_params}")
                #order_allowed: bool = True if size != 0 else False
                
                if size != 0 :
                    
                    if (bullish or strong_bullish) \
                        and bid_price_is_lower:
                    
                        if (False if size == 0 else True) and len_orders == 0:# and max_order:
                            
                            exit_params.update({"entry_price": bid_price})
                                
                            #convert size to positive sign
                            exit_params.update({"size": abs (size)})
                            
                            order_allowed: bool = True

        return order_allowed


    async def cancelling_order (self) -> None:
        """ """
        pass
    

    async def modifying_order (self) -> None:
        """ """
        pass
    
    async def is_send_and_cancel_open_order_allowed(
        self,
        instrument_name: str,
        futures_instruments,
        orders_currency_strategy: list,
        ask_price: float,
    ) -> dict:
        """ """
        
        order_allowed, cancel_allowed, cancel_id = False, False, None
        
        open_orders_label_strategy: list=  [o for o in orders_currency_strategy if "open" in o["label"]]
        
        len_orders: int = get_transactions_len(open_orders_label_strategy)
        
        hedging_attributes= self.strategy_parameters
        
        threshold_market_condition= hedging_attributes ["delta_price_pct"]
        
        market_condition = await get_market_condition_hedging(self.TA_result_data, 
                                                            self.index_price, 
                                                            threshold_market_condition)

        
        #bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]

        #strong_bullish = market_condition["strong_rising_price"]
        strong_bearish = market_condition["strong_falling_price"]
        #neutral = market_condition["neutral_price"]
        params: dict = self.get_basic_params().get_basic_opening_parameters(ask_price)
        
        weighted_factor= hedging_attributes["weighted_factor"]

        waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"] * ONE_MINUTE

        over_hedged  =  self.over_hedged_opening
        
        log.warning (f"sum_my_trades_currency_strategy {self.sum_my_trades_currency_strategy} over_hedged {self.over_hedged}  len_orders == 0 { len_orders == 0}" )
        
        SIZE_FACTOR = get_waiting_time_factor(weighted_factor, strong_bearish, bearish)
    
        if not over_hedged:
            
            order_allowed: bool = self. opening_position (instrument_name,
                                                          futures_instruments,
                                                          open_orders_label_strategy,
                                                          market_condition,
                                                          params,
                                                          SIZE_FACTOR,
                                                          len_orders)
            
            cancel_allowed: bool = is_cancelling_order_allowed(
                strong_bearish,
                bearish,
                waiting_minute_before_cancel,
                len_orders,
                open_orders_label_strategy,
                self.server_time,
            )

        else:
            
            if len_orders > 0:
                cancel_allowed = True

        return dict(
            order_allowed=order_allowed and len_orders == 0,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id= None if not cancel_allowed \
            else get_order_id_max_time_stamp(open_orders_label_strategy)
        )


    async def is_send_exit_order_allowed(
        self,
        orders_currency_strategy_label_closed,
        bid_price: float,
        selected_transaction: list,
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
            
        market_condition = await get_market_condition_hedging (self.TA_result_data, 
                                                                self.index_price, 
                                                                threshold_market_condition)

        bullish, strong_bullish = market_condition["rising_price"], market_condition["strong_rising_price"]

        len_orders: int = get_transactions_len(orders_currency_strategy_label_closed)

        hedging_attributes = self.strategy_parameters
    
        threshold_market_condition = hedging_attributes ["delta_price_pct"]
        

        ONE_SECOND = 1000
        ONE_MINUTE = ONE_SECOND * 60
        
        waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"] * ONE_MINUTE
                        
        over_hedged  =  self.over_hedged
            
        exit_params: dict = self.get_basic_params(). get_basic_closing_paramaters (selected_transaction,
                                                                orders_currency_strategy_label_closed,)

        log.warning (f"sum_my_trades_currency_strategy {self.sum_my_trades_currency_strategy} over_hedged {self.over_hedged} len_orders == 0 {len_orders == 0}")
        
        log.warning (f"""bid_price {bid_price} transaction ["price"] {transaction ["price"]}""")
                
        order_allowed = self. closing_position (transaction,
                                                exit_params,
                                                bullish, 
                                                strong_bullish,
                                                over_hedged,
                                                len_orders,
                                                bid_price,)
        
        if len_orders> 0:          
            
            cancel_allowed: bool = is_cancelling_order_allowed(
                strong_bullish,
                bullish,
                waiting_minute_before_cancel,
                len_orders,
                orders_currency_strategy_label_closed,
                self.server_time,)
            
            if cancel_allowed:
                cancel_id= min ([o["order_id"] for o in orders_currency_strategy_label_closed])  
        
        return dict(
            order_allowed= order_allowed,
            order_parameters=(
                [] if order_allowed == False else exit_params
            ),
            cancel_allowed=cancel_allowed,
            cancel_id=None if not cancel_allowed else cancel_id
        )
