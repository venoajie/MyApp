# # -*- coding: utf-8 -*-

# user defined formula
from db_management import sqlite_management

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)
    
if __name__ == "__main__":
    try:
        sqlite_management.create_dataBase_sqlite('databases/trading.sqlite3')
        sqlite_management.create_table_mytrades()
        params= [{'trade_seq': 119459281, 'trade_id': 'ETH-162634254', 'timestamp': 1678610180143, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1473.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32205761779', 'mmp': False, 'matching_id': None, 'mark_price': 1472.79, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678610144572', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1474.68, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}]
        
        sqlite_management.insert_table_mytrades('myTradesOpen',params)
        
        query=sqlite_management.querying_table('myTradesOpen')
        print (query)
        
        query=sqlite_management.querying_table('myTradesOpen', 'state', '=', 'filled')
        print (query)
        

    except (KeyboardInterrupt, SystemExit):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 10)

