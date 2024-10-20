
from utilities.string_modification import (
    extract_integers_from_text)

from_transaction_log_instrument = [{'instrument_name': 'BTC-1NOV24', 'position': -10, 'timestamp': 1729248478708}, {'instrument_name': 'BTC-1NOV24', 'position': -20, 'timestamp': 1729248478708}] 

last_time_stamp_log = [] if from_transaction_log_instrument == []\
            else str(max([extract_integers_from_text(o["trade_id"]) for o in from_transaction_log_instrument ]))
            
print (last_time_stamp_log)