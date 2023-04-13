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
    {'trade_seq': 122628217, 'trade_id': 'ETH-166736294', 'timestamp': 1681359527286, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1940.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32845591518', 'mmp': False, 'matching_id': None, 'mark_price': 1940.67, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681359527286', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1940.06, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': False, 'amount': 70.0}, 
    {'trade_seq': 122668128, 'trade_id': 'ETH-166788115', 'timestamp': 1681379087335, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1982.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850806120', 'mmp': False, 'matching_id': None, 'mark_price': 1982.48, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379086467', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.27, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 2.0}, 
    {'trade_seq': 122668132, 'trade_id': 'ETH-166788122', 'timestamp': 1681379091803, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1982.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850806898', 'mmp': False, 'matching_id': None, 'mark_price': 1982.71, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379088168', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.46, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 2.0}, 
    
    {'trade_seq': 122668143, 'trade_id': 'ETH-166788137', 'timestamp': 1681379092904, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1982.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850808573', 'mmp': False, 'matching_id': None, 'mark_price': 1982.75, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379092455', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.49, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668165, 'trade_id': 'ETH-166788161', 'timestamp': 1681379098189, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1983.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850808879', 'mmp': False, 'matching_id': None, 'mark_price': 1982.92, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379093097', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668171, 'trade_id': 'ETH-166788168', 'timestamp': 1681379102096, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1983.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850810139', 'mmp': False, 'matching_id': None, 'mark_price': 1983.03, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379098646', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.63, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668175, 'trade_id': 'ETH-166788176', 'timestamp': 1681379105603, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1983.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850811403', 'mmp': False, 'matching_id': None, 'mark_price': 1983.65, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379102577', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1982.16, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668454, 'trade_id': 'ETH-166788502', 'timestamp': 1681379208314, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1986.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850838999', 'mmp': False, 'matching_id': None, 'mark_price': 1986.23, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379202187', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1984.66, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668473, 'trade_id': 'ETH-166788526', 'timestamp': 1681379215498, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1986.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850839959', 'mmp': False, 'matching_id': None, 'mark_price': 1986.66, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379208787', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1985.01, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668530, 'trade_id': 'ETH-166788584', 'timestamp': 1681379222177, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1987.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850842190', 'mmp': False, 'matching_id': None, 'mark_price': 1987.23, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379215980', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1985.56, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122669374, 'trade_id': 'ETH-166789594', 'timestamp': 1681379438779, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1986.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850907737', 'mmp': False, 'matching_id': None, 'mark_price': 1986.88, 'liquidity': 'M', 'label': 'hedgingSpot-open-1681379437841', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1985.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},
    
    {'trade_seq': 122668129, 'trade_id': 'ETH-166788119', 'timestamp': 1681379091803, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1982.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850806806', 'mmp': False, 'matching_id': None, 'mark_price': 1982.71, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681379087881', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.46, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}
    , {'trade_seq': 122668130, 'trade_id': 'ETH-166788120', 'timestamp': 1681379091803, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1982.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850806885', 'mmp': False, 'matching_id': None, 'mark_price': 1982.71, 'liquidity': 'M', 'label': 'every4hoursShort-open-1681379088074', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.46, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0},
    {'trade_seq': 122674714, 'trade_id': 'ETH-166796420', 'timestamp': 1681382745707, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1991.35, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32851707794', 'mmp': False, 'matching_id': None, 'mark_price': 1991.35, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681382741149', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1989.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122668135, 'trade_id': 'ETH-166788129', 'timestamp': 1681379092527, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.95e-06, 'price': 1982.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850808539', 'mmp': False, 'matching_id': None, 'mark_price': 1982.75, 'liquidity': 'M', 'label': 'every4hoursLong-open-1681379092355', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.49, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122677804, 'trade_id': 'ETH-166800399', 'timestamp': 1681385696422, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -1.049e-05, 'price': 1990.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32852385212', 'mmp': False, 'matching_id': None, 'mark_price': 1990.63, 'liquidity': 'M', 'label': 'every1hoursLong-open-1681385642185', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1989.66, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0},
    
    {'trade_seq': 122668134, 'trade_id': 'ETH-166788128', 'timestamp': 1681379092527, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -9.95e-06, 'price': 1982.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32850808433', 'mmp': False, 'matching_id': None, 'mark_price': 1982.75, 'liquidity': 'M', 'label': 'every1hoursLong-open-1681379092257', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1981.49, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}, 
    {'trade_seq': 122672568, 'trade_id': 'ETH-166793734', 'timestamp': 1681381880280, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1988.55, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32851470026', 'mmp': False, 'matching_id': None, 'mark_price': 1988.19, 'liquidity': 'M', 'label': 'every1hoursLong-closed-1681379092257', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1986.77, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    
    {'trade_seq': 122672670, 'trade_id': 'ETH-166793894', 'timestamp': 1681381940152, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1988.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32851484653', 'mmp': False, 'matching_id': None, 'mark_price': 1988.04, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681381940152', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1986.74, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
    
    {'trade_seq': 122677947, 'trade_id': 'ETH-166800562', 'timestamp': 1681385893041, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1988.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32852419907', 'mmp': False, 'matching_id': None, 'mark_price': 1989.03, 'liquidity': 'M', 'label': 'every1hoursShort-open-1681385893041', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1988.11, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}]

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

