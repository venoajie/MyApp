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
my_trades_open =  [{'trade_seq': 119459281, 'trade_id': 'ETH-162634254', 'timestamp': 1678610180143, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1473.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32205761779', 'mmp': False, 'matching_id': None, 'mark_price': 1472.79, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678610144572', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1474.68, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}, {'trade_seq': 119653801, 'trade_id': 'ETH-162909430', 'timestamp': 1678706775993, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1583.75, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32231983208', 'mmp': False, 'matching_id': None, 'mark_price': 1583.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678706775367', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1583.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 5.0}, {'trade_seq': 119665688, 'trade_id': 'ETH-162925875', 'timestamp': 1678713118256, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1598.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32234303212', 'mmp': False, 'matching_id': None, 'mark_price': 1597.73, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678713106585', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1597.86, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 119736857, 'trade_id': 'ETH-163020718', 'timestamp': 1678727097665, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915623', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089260', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 119736858, 'trade_id': 'ETH-163020719', 'timestamp': 1678727097665, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915636', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089307', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 119736859, 'trade_id': 'ETH-163020720', 'timestamp': 1678727097665, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1666.15, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32243915644', 'mmp': False, 'matching_id': None, 'mark_price': 1666.07, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678727089354', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1666.08, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0},{'trade_seq': 120460950, 'trade_id': 'ETH-163959270', 'timestamp': 1679205009236, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1783.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32404150932', 'mmp': False, 'matching_id': None, 'mark_price': 1784.05, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679204971613', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1782.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 120460951, 'trade_id': 'ETH-163959271', 'timestamp': 1679205009236, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1783.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32404150944', 'mmp': False, 'matching_id': None, 'mark_price': 1784.05, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679204971663', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1782.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 120460952, 'trade_id': 'ETH-163959272', 'timestamp': 1679205009236, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1783.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32404150950', 'mmp': False, 'matching_id': None, 'mark_price': 1784.05, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679204971720', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1782.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 120473261, 'trade_id': 'ETH-163975417', 'timestamp': 1679218646776, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1780.65, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32406588944', 'mmp': False, 'matching_id': None, 'mark_price': 1780.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679218645798', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1779.95, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0},  {'trade_seq': 120460946, 'trade_id': 'ETH-163959266', 'timestamp': 1679205009236, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1783.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32404150901', 'mmp': False, 'matching_id': None, 'mark_price': 1784.05, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679204971425', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1782.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 120460945, 'trade_id': 'ETH-163959265', 'timestamp': 1679205009236, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1783.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32404150899', 'mmp': False, 'matching_id': None, 'mark_price': 1784.05, 'liquidity': 'M', 'label': 'hedgingSpot-open-1679204971378', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1782.8, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 5.0},{
        "trade_seq": 122152417,
        "trade_id": "ETH-166165415",
        "timestamp": 1680792445205,
        "tick_direction": 2,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.000007,
        "price": 1867.5,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32760078676",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1867.34,
        "liquidity": "M",
        "label": "supplyDemandLongB-open-1680792419318",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1867.44,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "buy",
        "api": True,
        "amount": 2
      },
      {
        "trade_seq": 122258310,
        "trade_id": "ETH-166290543",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770401302",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680865846651",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258311,
        "trade_id": "ETH-166290544",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770454869",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680866210552",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258312,
        "trade_id": "ETH-166290545",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770567741",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680867327123",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258313,
        "trade_id": "ETH-166290546",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770656891",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680867905588",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258314,
        "trade_id": "ETH-166290547",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770928726",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680869325060",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258315,
        "trade_id": "ETH-166290548",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32770962877",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680869601968",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258317,
        "trade_id": "ETH-166290550",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32772636223",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680877402717",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258318,
        "trade_id": "ETH-166290551",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32772819098",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680878191492",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      },
      {
        "trade_seq": 122258322,
        "trade_id": "ETH-166290555",
        "timestamp": 1680933604267,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1880,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32777881313",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1879.48,
        "liquidity": "M",
        "label": "supplyDemandShort60A-open-1680929656377",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1879.45,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 4
      }
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

