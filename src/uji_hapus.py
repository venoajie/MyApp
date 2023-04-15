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
my_trades_open =[
    {'trade_seq': 122931300, 'trade_id': 'ETH-167116030', 'timestamp': 1681519153211, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2092.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32885652532', 'mmp': False, 'matching_id': None, 'mark_price': 2092.46, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681519153211', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2092.69, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 80.0}, {'trade_seq': 122971608, 'trade_id': 'ETH-167163577', 'timestamp': 1681568402647, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -8.3e-07, 'price': 2102.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32892551162', 'mmp': False, 'matching_id': None, 'mark_price': 2102.45, 'liquidity': 'M', 'label': 'every5mtestLong-open-1681568392078', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2102.26, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, {'trade_seq': 122971920, 'trade_id': 'ETH-167164035', 'timestamp': 1681568896537, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2101.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32892630483', 'mmp': False, 'matching_id': None, 'mark_price': 2101.01, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681568871144', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2101.17, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 122971921, 'trade_id': 'ETH-167164036', 'timestamp': 1681568896537, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2101.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32892630487', 'mmp': False, 'matching_id': None, 'mark_price': 2101.01, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681568871192', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2101.17, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}, {'trade_seq': 122972053, 'trade_id': 'ETH-167164178', 'timestamp': 1681568987087, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -4e-07, 'price': 2100.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32892630480', 'mmp': False, 'matching_id': None, 'mark_price': 2101.42, 'liquidity': 'M', 'label': 'every5mtestLong-open-1681568871097', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2101.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, {'trade_seq': 122993401, 'trade_id': 'ETH-167190562', 'timestamp': 1681598206591, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2095.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32897249916', 'mmp': False, 'matching_id': None, 'mark_price': 2095.88, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681598206591', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2095.65, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}, {'trade_seq': 122993402, 'trade_id': 'ETH-167190564', 'timestamp': 1681598206600, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2095.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32897249937', 'mmp': False, 'matching_id': None, 'mark_price': 2095.88, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681598203627', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2095.65, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 122993403, 'trade_id': 'ETH-167190565', 'timestamp': 1681598206600, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 2095.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32897249948', 'mmp': False, 'matching_id': None, 'mark_price': 2095.88, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681598203718', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2095.65, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 3.0}
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

