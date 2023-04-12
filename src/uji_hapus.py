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


# from loguru import logger as log
my_trades_open = [
  
    
    {'trade_seq': 122453041, 'trade_id': 'ETH-166526243', 'timestamp': 1681204338247, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.09e-05, 'price': 1918.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32813955804', 'mmp': False, 'matching_id': None, 'mark_price': 1918.84, 'liquidity': 'M', 'label': 'every1hoursShort-open-12345678', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1918.67, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 10.0}, 
    {'trade_seq': 122453042, 'trade_id': 'ETH-166526244', 'timestamp': 1681204338458, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1918.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32813955804', 'mmp': False, 'matching_id': None, 'mark_price': 1918.84, 'liquidity': 'M', 'label': 'every1hoursShort-closed-12345678', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1918.67, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 10.0},
    {'trade_seq': 122453526, 'trade_id': 'ETH-166526905', 'timestamp': 1681205341061, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1916.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32813880850', 'mmp': False, 'matching_id': None, 'mark_price': 1916.21, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681205341061', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1916.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 62.0}]

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

