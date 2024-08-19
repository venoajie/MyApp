# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass


# user defined formula
from strategies.basic_strategy import (
    BasicStrategy)

from utilities.pickling import (
    read_data)
from utilities.system_tools import (
    provide_path_for_file)

async def get_futures_combo_instruments(
    currency: str) -> list:
    """ """
    
    my_path_instruments = provide_path_for_file(
        "instruments", currency
    )

    instruments_raw = read_data(my_path_instruments)
    instruments = instruments_raw[0]["result"]

    instruments_kind: list = [
        o for o in instruments if o["kind"] =="future_combo"
    ]

    print (f"instruments_kind {instruments_kind}")

    return instruments_kind



@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):
    """ """

    async def is_send_and_cancel_open_order_allowed(
        self,
        notional: float,
        index_price,
        ask_price: float,
        server_time: int,
        TA_result_data: dict,
        threshold_market_condition: float,
        threshold: float,
    ) -> dict:
        """ """

        open_orders_label_strategy: (
            dict
        ) = await self.get_basic_params().transaction_attributes(
            "orders_all_json", "open"
        )
