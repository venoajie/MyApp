# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies.basic_strategy import BasicStrategy, is_minimum_waiting_time_has_passed


@dataclass(unsafe_hash=True, slots=True)
class MarketMaker(BasicStrategy):

    """ """

    def get_basic_params(self) -> dict:
        """
        """
        return BasicStrategy(self.strategy_label)

    async def is_cancel_order_allowed(self, len_orders: int, 
                                server_time: int, 
                                max_tstamp_orders: int, 
                                time_interval: float 
                                ) -> bool:
        """
        """
        
        cancel_allowed: bool = False

        if len_orders != [] and len_orders > 0:
            minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed(
                server_time, max_tstamp_orders, time_interval
            )
            if minimum_waiting_time_has_passed:
                cancel_allowed: bool = True

            print(f"minimum_waiting_time_has_passed {minimum_waiting_time_has_passed} len_orders {len_orders} ")
            
        return cancel_allowed

    async def is_send_order_allowed(self, size_from_positions: int, len_orders: int, side: str,
                                market_condition: dict 
                                ) -> bool:
        """
        """

        order_allowed: bool = False
        
        bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]
        ranging = market_condition["neutral_price"]
        
        if (len_orders == [] or len_orders == 0):
                
            if side == "buy" and bullish:
                order_allowed: bool = True
            if side == "sell" and bearish:
                order_allowed: bool = True
            if ranging:
                order_allowed: bool = True
        print(f"side {side} bullish {bullish} bearish {bearish} order_allowed {order_allowed} ")

        return order_allowed
    
    async def is_send_and_cancel_open_order_allowed(
        self, size_from_positions: int, notional: float, ask_price: float, bid_price: float, server_time: int, market_condition: dict,take_profit_pct_daily: float=1/100
    ) -> dict:
        """
        """
        from risk_management.position_sizing import (
                qty_order_and_interval_time as order_and_interval)
        
        open_orders_label_strategy: dict = await self.get_basic_params().transaction_attributes(
            "orders_all_json", "open"
        )

        len_orders: int = open_orders_label_strategy["transactions_len"]
        
        params: dict = self.get_basic_params().get_basic_opening_parameters(
            notional, ask_price, bid_price
        )

        profit_target_pct_transaction= market_condition["profit_target_pct"]
        
        qty_order_and_interval_time: dict = order_and_interval(
                notional, take_profit_pct_daily, profit_target_pct_transaction
            )

        params.update({"size": qty_order_and_interval_time["qty_per_order"]})
        params.update({"profit_target_pct_transaction": profit_target_pct_transaction})
        print(
                    f"profit_target_pct_transaction   {profit_target_pct_transaction} qty_order_and_interval_time   {qty_order_and_interval_time}" 
                ) 
        params.update(
            {
                "interval_time_between_order_in_ms": qty_order_and_interval_time[
                    "interval_time_between_order_in_ms"
                ]
            }
            )
        time_interval: float = params["interval_time_between_order_in_ms"]
        max_tstamp_orders: int = open_orders_label_strategy["max_time_stamp"]

        #is cancel order allowed?
        cancel_allowed: bool = await self.is_cancel_order_allowed(len_orders, 
                                server_time, 
                                max_tstamp_orders, 
                                time_interval)         

        #resizing qty
        side= params["side"]

        if size_from_positions < 0 and side=="buy"  and market_condition["rising_price"]\
            or size_from_positions > 0 and side == "sell" and market_condition["falling_price"]:

            params.update({"size": max(abs(size_from_positions), 
                                       int(notional)) }
                          )
                        
        print(f"params {params} ")

        #is open order allowed?
        if params["everything_is_consistent"]:
            order_allowed: bool=await self.is_send_order_allowed(size_from_positions, len_orders, params["side"],
                                market_condition 
                                )
        
        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=open_orders_label_strategy["order_id_max_time_stamp"],
        )

    async def is_send_exit_order_allowed(
        self, market_condition: dict, ask_price: float, bid_price: float, selected_transaction: list
    ) -> dict:
        """
        """
        return await self.get_basic_params().is_send_exit_order_allowed(
            market_condition,ask_price, bid_price, selected_transaction
        )
