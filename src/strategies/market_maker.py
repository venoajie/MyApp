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

    async def is_send_and_cancel_open_order_allowed(
        self, notional: float, ask_price: float, bid_price: float, server_time: int, market_condition: dict
    ) -> dict:
        """
        """
        open_orders_label_strategy: dict = await self.get_basic_params().transaction_attributes(
            "orders_all_json", "open"
        )

        len_orders: int = open_orders_label_strategy["transactions_len"]
        my_trades: dict = await self.get_basic_params().transaction_attributes(
            "my_trades_all_json"
        )
        len_my_trades: int = my_trades["transactions_len"]
        max_tstamp_my_trades: int = my_trades["max_time_stamp"]
        ratio = await self.get_basic_params().get_side_ratio()
        
        bullish = market_condition["rising_price"]
        bearish = market_condition["falling_price"]

        print(f" ratio {ratio}")

        params: dict = self.get_basic_params().get_basic_opening_paramaters(
            notional, ask_price, bid_price
        )

        time_interval: float = params["interval_time_between_order_in_ms"]

        order_allowed: bool = False
        cancel_allowed: bool = False

        if len_orders != [] and len_orders > 0:
            max_tstamp_orders: int = open_orders_label_strategy["max_time_stamp"]

            minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed(
                server_time, max_tstamp_orders, time_interval
            )
            if minimum_waiting_time_has_passed:
                cancel_allowed: bool = True

        else:
            if params["side"] == "buy":
                time_balancer = ratio["long_short_ratio"]
            if params["side"] == "sell":
                time_balancer = ratio["short_long_ratio"]

            len_my_trades = 1 if time_balancer == 1 else len_my_trades

            time_interval_qty: float = time_interval * len_my_trades * time_balancer
            print(
                f"time_interval_qty {time_interval_qty} len_orders {len_orders} time_balancer {time_balancer}"
            )
            minimum_waiting_time_has_passed: bool = is_minimum_waiting_time_has_passed(
                server_time, max_tstamp_my_trades, time_interval_qty
            )

            print(f"minimum_waiting_time_has_passed {minimum_waiting_time_has_passed} ")
            print(f"bullish {bullish} ")
            print(f"bearish {bearish} ")
            if minimum_waiting_time_has_passed and len_orders == []:
                    
                if params["side"] == "buy" and bullish:
                    order_allowed: bool = True
                if params["side"] == "sell" and bearish:
                    order_allowed: bool = True

        return dict(
            order_allowed=order_allowed,
            order_parameters=[] if order_allowed == False else params,
            cancel_allowed=cancel_allowed,
            cancel_id=open_orders_label_strategy["order_id_max_time_stamp"],
        )

    async def is_send_exit_order_allowed(
        self, ask_price: float, bid_price: float, selected_transaction: list
    ) -> dict:
        """
        """
        return await self.get_basic_params().is_send_exit_order_allowed(
            ask_price, bid_price, selected_transaction
        )
