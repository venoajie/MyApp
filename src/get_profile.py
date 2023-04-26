#!/usr/bin/python3

# built ins
import asyncio
#from time import sleep
#import orjson

# installed
from loguru import logger as log

# user defined formula
import deribit_get
from utilities import  system_tools, string_modification as str_mod
from db_management import sqlite_management
from market_understanding import tpo_project
# from market_understanding import futures_analysis

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)

def main():
    try:
        tpo_project

    except Exception as error:
        catch_error(error, 30)

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 30)
