#!/usr/bin/python3

# built ins
import asyncio
#import orjson
import cachetools.func

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
import deribit_get
from transaction_management.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools, string_modification as str_mod
from configuration import label_numbering, config
from strategies import entries_exits
from db_management import sqlite_management
# from market_understanding import futures_analysis

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)

@dataclass(unsafe_hash=True, slots=True)
class GridPerpetual:

    """ """

    
    active_trade_item: list = None
    strategy_from_config: str = None

    async def get_strategy_from_active_trade_item (self) -> list:
        """
        """
        result = [o['label'] for o in self.active_trade_item][0]
        return dict(
            main= str_mod.parsing_label(result)['main'],
            transaction_net= str_mod.parsing_label(result)['transaction_net'])
        
    async def get_trades_as_per_label(self) -> list:
        """
        """
        result = []
        if self.my_trades_open != []:
            if self.sub_stratey == None:
                result =([
                o for o in self.my_trades_open  ['all'] \
                    if  str_mod.parsing_label(o['label_main'])['main'] == self.stratey_from_config ]
                                                    )
            if self.active_trade_item == None:
                result =([
                o for o in self.my_trades_open ['all'] \
                    if  str_mod.parsing_label(o['label_main'])['main'] == self.stratey_from_config ]
                                                    )

        return result

    async def is_send_order_allowed(self) -> list:
        """
        """
        pass

    async def provide_params_for_order(self) -> list:
        """
        """
        pass
    
    async def is_send_close_order_allowed(self) -> list:
        """
        """
        pass
    
    async def is_cancel_current_order_allowed(self) -> list:
        """
        """
        pass