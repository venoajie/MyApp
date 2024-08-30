# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass


# user defined formula
from strategies.basic_strategy import (
    BasicStrategy, get_instruments_kind)

async def get_futures_combo_instruments(currency: str) -> list:
    """_summary_

    Args:
        currency (str): _description_
        Instance:  [
                    {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1,'counter_currency': 'USD', 
                    'settlement_period': 'month', 'settlement_currency': 'ETH', 'creation_timestamp': 1719564006000, 
                    'instrument_id': 342036, 'base_currency': 'ETH', 'tick_size': 0.05, 'contract_size': 1, 'is_active': True, 
                    'expiration_timestamp': 1725004800000, 'instrument_type': 'reversed', 'taker_commission': 0.0, 
                    'maker_commission': 0.0, 'instrument_name': 'ETH-FS-27SEP24_30AUG24', 'kind': 'future_combo', 
                    'rfq': False, 'price_index': 'eth_usd'}, 
                    {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1, 'counter_currency': 'USD', 
                    'settlement_period': 'week', 'settlement_currency': 'ETH', 'creation_timestamp': 1724402396000, 
                    'instrument_id': 362593, 'base_currency': 'ETH', 'tick_size': 0.05, 'contract_size': 1, 'is_active': True, 
                    'expiration_timestamp': 1725609600000, 'instrument_type': 'reversed', 'taker_commission': 0.0, 
                    'maker_commission': 0.0, 'instrument_name': 'ETH-FS-27SEP24_6SEP24', 'kind': 'future_combo', 
                    'rfq': False, 'price_index': 'eth_usd'}]

    Returns:
        list: _description_
    """
    
    return get_instruments_kind (currency,"future_combo" )



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
