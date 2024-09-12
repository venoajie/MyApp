# # -*- coding: utf-8 -*-

# built ins
import asyncio
from loguru import logger as log
# installed
from dataclassy import dataclass
from strategies.config_strategies import hedging_spot_attributes

# user defined formula
from strategies.basic_strategy import (
    BasicStrategy,
    get_order_id_max_time_stamp,
    is_minimum_waiting_time_has_passed,
    delta_pct,get_label,
    get_max_time_stamp,
    check_if_id_has_used_before,
    size_rounding,
    is_everything_consistent
)
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy
    )
from utilities.string_modification import (extract_currency_from_text)

def get_transactions_len(result_strategy_label) -> int:
    """ """
    return 0 if result_strategy_label == [] else len([o for o in result_strategy_label])

def get_transactions_sum(result_strategy_label) -> int:
    """ """
    return 0 if result_strategy_label == [] else sum([o["amount"] for o in result_strategy_label])


def hedged_value_to_notional(notional: float, hedged_value: float) -> float:
    """ """
    return abs(hedged_value / notional)


def determine_size(instrument_name: str, notional: float, factor: float) -> int:
    """ """
    proposed_size= max(1, int(notional * factor))
    
    return size_rounding(instrument_name, proposed_size)

def positions_and_orders(current_size: int, current_orders: int) -> int:
    """ """

    return current_size + current_orders

def proforma_size(
    current_size: int, current_orders: int, next_orders: int
) -> int:
    """ """

    return (
        positions_and_orders(current_size, current_orders) - next_orders #the sign is +
    )

def are_size_and_order_appropriate_for_ordering(
    notional: float, current_size: float, current_orders: int, next_orders: int) -> bool:
    """ """
    
    proforma  = proforma_size(current_size, current_orders, next_orders) 
    log.debug (f"proforma  {proforma} current_size  {current_size} current_orders  {current_orders} next_orders  {next_orders} notional  {notional} (proforma) < abs(notional)   {abs(proforma) < (notional) }")
    
    return abs(proforma) < (notional) 

def get_bearish_factor(weighted_factor, strong_bearish: bool, bearish: bool) -> float:
    """
    Determine factor for size determination.
    strong bearish : 10% of total amount
    bearish        : 5% of total amount
    neutral        : 1% of total amount
    """

    ONE_PCT = 1 / 100
    
    BEARISH_FACTOR = weighted_factor["extreme"] * ONE_PCT if strong_bearish else weighted_factor["medium"]  * ONE_PCT

    return BEARISH_FACTOR if (strong_bearish or bearish) else ONE_PCT


def is_hedged_value_to_notional_exceed_threshold(
    notional: float, hedged_value: float, threshold: float
) -> float:
    """ """
    return hedged_value_to_notional(notional, hedged_value) > threshold


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
    
    print (f"bearish_interval_threshold {bearish_interval_threshold} {ONE_MINUTE * bearish_interval_threshold if (strong_bearish or bearish) else ONE_MINUTE *  threshold}")

    return (
        ONE_MINUTE * bearish_interval_threshold
        if (strong_bearish or bearish)
        else ONE_MINUTE *  threshold
    )


def is_cancelling_order_allowed(
    strong_bearish: bool,
    bearish: bool,
    threshold: float,
    len_orders: int,
    open_orders_label_strategy: dict,
    server_time: int,
) -> bool:
    """ """

    cancel_allowed: bool = False

    if len_orders != [] and len_orders > 0:

        time_interval = get_timing_factor(strong_bearish, bearish, threshold)

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
        return BasicStrategy(self.strategy_label)

    async def is_send_and_cancel_open_order_allowed(
        self,
        currency,
        instrument_name: str,
        notional: float,
        index_price,
        ask_price: float,
        server_time: int,
        TA_result_data: dict
    ) -> dict:
        """ """
        
        #one_minute=60000

        #open_orders_label_strategy: dict = await self.get_basic_params().transaction_attributes(
        #    "orders_all_json", "open"
        #)
        fluctuation_exceed_threshold = True#TA_result_data["1m_fluctuation_exceed_threshold"]

        params: dict = self.get_basic_params().get_basic_opening_parameters(
            ask_price, None, notional
        )
        #log.info  (f"params {params}")
        hedging_attributes= hedging_spot_attributes()[0]

        threshold_market_condition= hedging_attributes ["delta_price_pct"]
        
        market_condition = await get_market_condition_hedging(currency,
            TA_result_data, index_price, threshold_market_condition
        )

        #bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]

        #strong_bullish = market_condition["strong_rising_price"]
        strong_bearish = market_condition["strong_falling_price"]
        #neutral = market_condition["neutral_price"]
        
        weighted_factor= hedging_attributes["weighted_factor"]
        waiting_minute_before_cancel= hedging_attributes["waiting_minute_before_cancel"]
        
        SIZE_FACTOR = get_bearish_factor(weighted_factor, strong_bearish, bearish)

        size = determine_size(instrument_name, notional, SIZE_FACTOR)

        open_orders_label_strategy: list=  await executing_query_based_on_currency_or_instrument_and_strategy("orders_all_json", 
                                                                                                              currency.upper(), 
                                                                                                              self.strategy_label,
                                                                                                              "open")
        #log.debug (f"open_orders_label_strategy {open_orders_label_strategy}")

        len_orders: int = get_transactions_len(open_orders_label_strategy)
        sum_orders: int = get_transactions_sum(open_orders_label_strategy)
        
        my_trades_currency_strategy: list= await executing_query_based_on_currency_or_instrument_and_strategy("my_trades_all_json", currency.upper(), self.strategy_label)

        sum_my_trades: int = sum([o["amount"] for o in my_trades_currency_strategy ])        
        
        size_and_order_appropriate_for_ordering: bool = (
            are_size_and_order_appropriate_for_ordering(
                notional, sum_my_trades, sum_orders, size
            )
        )

        cancel_allowed: bool = is_cancelling_order_allowed(
            strong_bearish,
            bearish,
            waiting_minute_before_cancel,
            len_orders,
            open_orders_label_strategy,
            server_time,
        )

        order_allowed: bool = (
                size_and_order_appropriate_for_ordering
                and (bearish or strong_bearish)
                and fluctuation_exceed_threshold
            )
        #print(f"order_allowed {order_allowed}")
        
        if order_allowed:
            label_open: str = get_label("open", self.strategy_label)
            params.update({"label": label_open})
            everything_is_consistent= is_everything_consistent(params)
            
            order_has_sent_before = await check_if_id_has_used_before (instrument_name, "label", params["label"], 100)
            if everything_is_consistent:
                
                params.update({"size": size})
                params.update({"everything_is_consistent": everything_is_consistent})
                           
                
            else:
                
                order_allowed=False
        
        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=get_order_id_max_time_stamp(open_orders_label_strategy)
        )

    async def is_send_exit_order_allowed(
        self,
        TA_result_data,
        index_price: float,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
    ) -> dict:
        """ """
        {'liquidity': 'M', 'risk_reducing': False, 'order_type': 'limit', 'trade_id': 'ETH-216360019', 'fee_currency': 'ETH', 
         'contracts': 4.0, 'reduce_only': False, 'self_trade': False, 'post_only': True, 'mmp': False, 'tick_direction': 3, 
         'matching_id': None, 'order_id': 'ETH-48539980959', 'fee': 0.0, 'mark_price': 2455.62, 'amount': 4.0, 'api': True, 
         'trade_seq': 157460588, 'instrument_name': 'ETH-PERPETUAL', 'profit_loss': 0.0, 'index_price': 2456.25, 'direction': 'sell', 
         'price': 2455.25, 'state': 'filled', 'timestamp': 1725198276199, 'label': 'hedgingSpot-open-1725198275948'}
        
        hedging_attributes= hedging_spot_attributes()[0]
        
        #log.error (f"selected_transaction {selected_transaction}")

        currency=extract_currency_from_text(selected_transaction[0]["instrument_name"]).lower()

        threshold_market_condition= hedging_attributes ["delta_price_pct"]
        
        market_condition = await get_market_condition_hedging(currency,
            TA_result_data, index_price, threshold_market_condition
        )

        bullish = market_condition["rising_price"]
        strong_bullish = market_condition["strong_rising_price"]
        #neutral = market_condition["neutral_price"]
        bearish = market_condition["falling_price"]

        exit_params: dict = await self.get_basic_params().is_send_exit_order_allowed(
            market_condition, ask_price, bid_price, selected_transaction
        )

        exit_allowed: bool = exit_params["order_allowed"] and (
            bullish or strong_bullish
        )
        
        cancel_allowed: bool = False
        cancel_id: str = None
        
        open_orders_label_strategy: list=  await executing_query_based_on_currency_or_instrument_and_strategy("orders_all_json", 
                                                                                                              currency.upper(), 
                                                                                                              self.strategy_label,
                                                                                                              "closed")
        
        len_orders: int = get_transactions_len(open_orders_label_strategy)
        
        if len_orders != [] and len_orders > 0 and bearish:
            log.error (f"order_parameters {exit_params}")
            log.debug (f"cancel_allowed {cancel_allowed}")
            cancel_allowed: bool = True
            cancel_id= min ([o["order_id"] for o in open_orders_label_strategy])


        return dict(
            order_allowed=exit_allowed,
            order_parameters=(
                [] if exit_allowed == False else exit_params["order_parameters"]
            ),
            cancel_allowed=cancel_allowed,
            cancel_id=cancel_id
        )
