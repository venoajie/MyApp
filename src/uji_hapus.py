from utilities import string_modification, number_modification, pickling, system_tools
from configuration import config
import asyncio
import os
import sqlite3
import time
import ast
from db_management import sqlite_management
#standardize database file location
import json, orjson

path = os.getcwd()
db_name = 'multistrike_oi.db'

#
# from loguru import logger as log
my_trades_open = [
    {'trade_seq': 122931300, 'trade_id': 'ETH-167116030', 'timestamp': 1681519153211, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2092.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32885652532', 'mmp': False, 'matching_id': None, 'mark_price': 2092.46, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681519153211','instrument_name': 'ETH-PERPETUAL', 'index_price': 2092.69, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 80.0}
    
                  ]

my_trades_path = system_tools.provide_path_for_file("myTrades", "eth", "open")

my_trades_path_open_recovery = system_tools.provide_path_for_file(
    "myTrades", "eth", "open-recovery-point"
)
my_trades  = pickling.read_data(my_trades_path_open_recovery)

net = number_modification.net_position(my_trades_open)
print (net)


async  def main() -> list:
    """ """
    await sqlite_management.insert_tables ('my_trades_all_json',
                                 my_trades_open)    
    await sqlite_management.insert_tables ('my_trades_all',
                                 my_trades_open)

    
if __name__ == "__main__":
        
    try:
        pickling.replace_data(my_trades_path, my_trades_open, True)
        pickling.replace_data(my_trades_path_open_recovery, my_trades_open, True)
        asyncio.get_event_loop().run_until_complete(main())

    except Exception as error:
        print (error)

