# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies.basic_strategy import BasicStrategy, is_minimum_waiting_time_has_passed


@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):

    """ """

    def get_basic_params(self) -> dict:
        """
        """
        return BasicStrategy(self.strategy_label)
    
    async def get_ema(self) -> dict:
        """
        https://stackoverflow.com/questions/488670/calculate-exponential-moving-average-in-python
        https://stackoverflow.com/questions/59294024/in-python-what-is-the-faster-way-to-calculate-an-ema-by-reusing-the-previous-ca
        """
            
        from db_management import sqlite_management
            
        table: str = "ohlc1_eth_perp_json"
        limit: int = 100
        ratio: float= 0.9
        get_ohlc_query = sqlite_management.querying_ohlc_closed("close", table, limit)
        print (f' get_ohlc {get_ohlc_query}')
        ohlc_all = await sqlite_management.executing_query_with_return(get_ohlc_query)
        ohlc_all.reverse()
        print (f' ohlc_all {ohlc_all}')
        ohlc = [o['close'] for o in ohlc_all]
        print (f' ohlc {ohlc}')
        
        return sum([ratio*ohlc[-x-1]*((1-ratio)**x) for x in range(len(ohlc))])

    def are_size_and_order_appropriate_for_ordering(
        self, notional: float, current_size: float, current_outstanding_order_len: int
    ) -> bool:
        """

        """
        return abs(current_size) < notional and current_outstanding_order_len == 0

    async def is_send_and_cancel_open_order_allowed(
        self, notional: float, ask_price: float, server_time: int, threshold: float = 30
    ) -> dict:
        """

        """

        open_orders_label_strategy: dict = await self.get_basic_params().get_orders_attributes(
            "open"
        )

        len_orders: int = open_orders_label_strategy["transactions_len"]
        my_trades: dict = await self.get_basic_params().get_my_trades_attributes()
        sum_my_trades: int = my_trades["transactions_sum"]
        params: dict = self.get_basic_params().get_basic_opening_paramaters(
            notional, ask_price, None
        )

        order_allowed: bool = self.are_size_and_order_appropriate_for_ordering(
            notional, sum_my_trades, len_orders
        )
        cancel_allowed: bool = False

        if len_orders != [] and len_orders > 0:
            ONE_MINUTE: int = 60000
            time_interval = ONE_MINUTE * threshold
            max_tstamp_orders: int = open_orders_label_strategy["max_time_stamp"]

            minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed(
                server_time, max_tstamp_orders, time_interval
            )
            if minimum_waiting_time_has_passed:
                cancel_allowed: bool = True

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=open_orders_label_strategy["order_id_max_time_stamp"],
        )

    def hedged_value_to_notional(self, notional: float, hedged_value: float) -> float:
        """ 
        """
        return abs(hedged_value / notional)

    def is_hedged_value_to_notional_exceed_threshold(
        self, notional: float, hedged_value: float, threshold: float
    ) -> float:
        """ 
        """
        return self.hedged_value_to_notional(notional, hedged_value) > threshold

    async def is_send_exit_order_allowed(
        self,
        notional: float,
        ask_price: float,
        bid_price: float,
        selected_transaction: list,
        MIN_HEDGING_RATIO: float = 0.8,
    ) -> dict:
        """
        """
        my_trades: dict = await self.get_basic_params().get_my_trades_attributes()

        sum_my_trades: int = my_trades["transactions_sum"]

        hedged_value_is_still_safe: bool = self.is_hedged_value_to_notional_exceed_threshold(
            notional, sum_my_trades, MIN_HEDGING_RATIO
        )

        exit_params: dict = await self.get_basic_params().is_send_exit_order_allowed(
            ask_price, bid_price, selected_transaction
        )

        open_orders_label_strategy: dict = await self.get_basic_params().get_orders_attributes(
            "open"
        )

        len_orders: int = open_orders_label_strategy["transactions_len"]

        no_outstanding_order: bool = len_orders == []

        exit_allowed: bool = exit_params[
            "order_allowed"
        ] and hedged_value_is_still_safe and no_outstanding_order

        return dict(
            order_allowed=exit_allowed,
            order_parameters=[]
            if exit_allowed == False
            else exit_params["order_parameters"],
        )
