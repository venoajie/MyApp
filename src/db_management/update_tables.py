from db_management import sqlite_management
from loguru import logger as log
def update_table_strategy_entries (strategyId, params)->list:

    '''
            Reference:
            https://stackoverflow.com/questions/43174403/python-sqlite-update-multiple-values
            https://stackoverflow.com/questions/19191704/how-to-update-several-specific-columns-using-sqlite3-python
    ''' 
    
    query_table = ("""UPDATE strategy_entries SET orderDate =?, orderId =? WHERE strategyId = ?""") 

    log.warning (query_table)
    params_result = {'info': {'id': '196667997628', 'clientId': None, 'market': 'BTC-MOVE-WK-1125', 'type': 'limit', 'side': 'sell', 'price': '1037.0', 'size': '0.0001', 'status': 'new', 'filledSize': '0.0', 'remainingSize': '0.0001', 'reduceOnly': False, 'liquidation': None, 'avgFillPrice': None, 'postOnly': True, 'ioc': False, 'createdAt': '2022-11-03T06:55:23.875812+00:00', 'future': 'BTC-MOVE-WK-1125'}, 'id': '196667997628', 'clientOrderId': None, 'timestamp': 1667458523875, 'datetime': '2022-11-03T06:55:23.875Z', 'lastTradeTimestamp': None, 'symbol': 'BTC-MOVE-WK/USD:USD-221126', 'type': 'limit', 'timeInForce': 'PO', 'postOnly': True, 'reduceOnly': False, 'side': 'sell', 'price': 1037.0, 'stopPrice': None, 'amount': 0.0001, 'cost': 0.0, 'average': None, 'filled': 0.0, 'remaining': 0.0001, 'status': 'open', 'fee': None, 'trades': [], 'fees': []}
    
    params_info = (params['info'])
    params_info = (params_info['createdAt'], params_info['id'], strategyId)
    log.warning (params_info)
    
    try:
        with sqlite_management.db_ops() as cur:
            
            cur.execute ((f'{query_table}'), params_info)  
            
    except Exception as error:
        from utils import formula
        formula.log_error('update table', 'update table strategy_entries', error, 30)    
                