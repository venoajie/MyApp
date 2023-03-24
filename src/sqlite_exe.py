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
    
    params= [{'trade_seq': 119459281, 'trade_id': 'ETH-162634254', 'timestamp': 1678610180143, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1473.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32205761779', 'mmp': False, 'matching_id': None, 'mark_price': 1472.79, 'liquidity': 'M', 'label': 'hedgingSpot-open-1678610144572', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1474.68, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}]
    
    await sqlite_management.insert_tables('myTradesOpen',params)
    
    params= [{
        "web": False,
        "triggered": False,
        "trigger_price": 1720.0,
        "trigger": "last_price",
        "time_in_force": "good_til_cancelled",
        "stop_price": 1720.0,
        "risk_reducing": False,
        "replaced": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": "market_price",
        "post_only": False,
        "order_type": "stop_market",
        "order_state": "untriggered",
        "order_id": "ETH-SLTB-5655271",
        "mmp": False,
        "max_show": 9.0,
        "last_update_timestamp": 1677934800237,
        "label": "supplyDemandShort60-closed-1677934800137",
        "is_liquidation": False,
        "instrument_name": "ETH-PERPETUAL",
        "direction": "buy",
        "creation_timestamp": 1677934800237,
        "api": True,
        "amount": 9.0,
    }, {
        "web": False,
        "triggered": False,
        "trigger_price": 1600.0,
        "trigger": "last_price",
        "time_in_force": "good_til_cancelled",
        "stop_price": 1600.0,
        "risk_reducing": False,
        "replaced": False,
        "reject_post_only": False,
        "reduce_only": False,
        "profit_loss": 0.0,
        "price": 1610.0,
        "post_only": True,
        "order_type": "take_limit",
        "order_state": "untriggered",
        "order_id": "ETH-TPTS-5655237",
        "mmp": False,
        "max_show": 5.0,
        "last_update_timestamp": 1677903684561,
        "label": "supplyDemandLong60B-closed-1677903684425",
        "is_liquidation": False,
        "instrument_name": "ETH-PERPETUAL",
        "direction": "sell",
        "creation_timestamp": 1677903684561,
        "api": True,
        "amount": 5.0,
    }, {
        "web":False,
        "time_in_force":"good_til_day",
        "risk_reducing":False,
        "replaced":False,
        "reject_post_only":False,
        "reduce_only":False,
        "profit_loss":0,
        "price":1000,
        "post_only":True,
        "order_type":"limit",
        "order_state":"open",
        "order_id":"ETH-32532905946",
        "mmp":False,
        "max_show":1,
        "last_update_timestamp":1679617201596,
        "label":"test",
        "is_liquidation":False,
        "instrument_name":"ETH-PERPETUAL",
        "filled_amount":0,
        "direction":"buy",
        "creation_timestamp":1679617201596,
        "commission":0,
        "average_price":0,
        "api":True,
        "amount":1,
}]
    
    await sqlite_management.insert_tables('ordersOpen',params)
    
    query=await sqlite_management.querying_table('ordersOpen')
    print (query)
    
    query=await sqlite_management.querying_table('ordersOpen', 'label', '=', 'test')
    print (query)
    
    query=await sqlite_management.querying_table('ordersOpen', 'price', '=', '1000')
    print (query)
    
    query=await sqlite_management.querying_table('ordersOpen', 'price', '=', 1000)
    print (query)
    
    query=await sqlite_management.querying_table('myTradesOpen')
    print (query)
    query=await sqlite_management.querying_table('myTradesOpen', 'state', '=', 'filled')
    print (query)
        
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())

    except (KeyboardInterrupt, SystemExit):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 10)

