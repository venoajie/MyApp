# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log
from utilities import pickling, system_tools, string_modification as str_mod


def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    result = await deribit_get.telegram_bot_sendtext(bot_message, purpose)

    return result


@dataclass(unsafe_hash=True, slots=True)
class MyTrades:
    """

    +----------------------------------------------------------------------------------------------+
    #  clean up my trades data
    """

    my_trades: list

    def my_trades_api(self) -> list:
        """ """
        return [o for o in self.my_trades if o["api"] == True]

