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
    {'trade_seq': 122453526, 'trade_id': 'ETH-166526905', 'timestamp': 1681205341061, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1916.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32813880850', 'mmp': False, 'matching_id': None, 'mark_price': 1916.21, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681205341061', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1916.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 62.0}, {'trade_seq': 122508649, 'trade_id': 'ETH-166593801', 'timestamp': 1681268681797, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.46e-05, 'price': 1864.35, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32826579073', 'mmp': False, 'matching_id': None, 'mark_price': 1864.22, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681268675822', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1864.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, {'trade_seq': 122508668, 'trade_id': 'ETH-166593822', 'timestamp': 1681268729337, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 5.948e-05, 'price': 1863.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32826579085', 'mmp': False, 'matching_id': None, 'mark_price': 1863.45, 'liquidity': 'M', 'label': 'supplyDemandLongB-open-1681268675925', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1864.02, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 4.0}, {'trade_seq': 122508697, 'trade_id': 'ETH-166593851', 'timestamp': 1681268739156, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1864.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32826587978', 'mmp': False, 'matching_id': None, 'mark_price': 1864.35, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681268732640', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1864.93, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 122508698, 'trade_id': 'ETH-166593852', 'timestamp': 1681268739156, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1864.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32826587988', 'mmp': False, 'matching_id': None, 'mark_price': 1864.35, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681268732747', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1864.93, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 122511370, 'trade_id': 'ETH-166597031', 'timestamp': 1681272441296, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1864.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32827178211', 'mmp': False, 'matching_id': None, 'mark_price': 1864.22, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681272441197', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1864.88, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122514779, 'trade_id': 'ETH-166601113', 'timestamp': 1681275870518, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1870.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32827600608', 'mmp': False, 'matching_id': None, 'mark_price': 1871.01, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681276611320', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1870.73, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122522799, 'trade_id': 'ETH-166610161', 'timestamp': 1681284545193, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1875.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32828655224', 'mmp': False, 'matching_id': None, 'mark_price': 1875.87, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681268675726', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1875.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122517899, 'trade_id': 'ETH-166604508', 'timestamp': 1681278558686, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.285e-05, 'price': 1865.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32827912440', 'mmp': False, 'matching_id': None, 'mark_price': 1865.24, 'liquidity': 'M', 'label': 'every1hoursShort-long-1681268675726', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1865.59, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122521217, 'trade_id': 'ETH-166608267', 'timestamp': 1681282212815, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1870.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32828363853', 'mmp': False, 'matching_id': None, 'mark_price': 1870.68, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681282203280', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1870.79, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 122521732, 'trade_id': 'ETH-166608847', 'timestamp': 1681283112642, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.094e-05, 'price': 1870.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32828459447', 'mmp': False, 'matching_id': None, 'mark_price': 1870.29, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681283104091', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1870.1, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, {'trade_seq': 122521791, 'trade_id': 'ETH-166608906', 'timestamp': 1681283164134, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1870.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32828465339', 'mmp': False, 'matching_id': None, 'mark_price': 1870.91, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681283158173', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1870.64, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
        
    {'trade_seq': 122524970, 'trade_id': 'ETH-166612534', 'timestamp': 1681285835639, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1872.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32828835680', 'mmp': False, 'matching_id': None, 'mark_price': 1872.16, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681285828219', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1873.18, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}]

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

