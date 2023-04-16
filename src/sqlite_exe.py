# # -*- coding: utf-8 -*-
import asyncio
# user defined formula
from db_management import sqlite_management

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)
    
async  def main() -> list:
    """ """
    await sqlite_management.create_dataBase_sqlite('databases/trading.sqlite3')

    await sqlite_management.create_tables()
    #query=await sqlite_management.querying_table('myTradesOpen', 'state', '=', 'filled')
    #print (query)
    result_to_dict = [{'trade_seq': 123004813, 'trade_id': 'ETH-167203783', 'timestamp': 1681617031649, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.39e-06, 'price': 2090.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32899417160', 'mmp': False, 'matching_id': None, 'mark_price': 2090.82, 'liquidity': 'M', 'label': 'every5mtestLong-open-1681617021717A', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2090.11, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}]
    await sqlite_management.insert_tables('my_trades_closed_json',result_to_dict)
    result_to_dict = {'trade_seq': 123004813, 'trade_id': 'ETH-167203783', 'timestamp': 1681617031649, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 1.39e-06, 'price': 2090.7, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32899417160', 'mmp': False, 'matching_id': None, 'mark_price': 2090.82, 'liquidity': 'M', 'label': 'every5mtestLong-open-1681617021717', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 2090.11, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 1.0}
    await sqlite_management.insert_tables('my_trades_closed_json',result_to_dict)
    
if __name__ == "__main__":
        
    try:
        asyncio.get_event_loop().run_until_complete(main())

    except (KeyboardInterrupt, SystemExit):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 10)

