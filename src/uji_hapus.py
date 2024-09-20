
from utilities.string_modification import (
    extract_integers_from_text)

from_sqlite_open= {'jsonrpc': '2.0', 'error': {'message': 'not_open_order', 'code': 11044}, 'testnet': False, 'usIn': 1726812977039648, 'usOut': 1726812977039907, 'usDiff': 259}

print(from_sqlite_open["error"]["message"])