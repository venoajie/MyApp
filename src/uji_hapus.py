from collections import OrderedDict
from utils import string_modification

data_from_db =  [{'timestamp': 1672371033716, 'instrument_name': 'ETH-27JAN23', 'change_id': 3183551047, 'bids': [[1194.5, 1343.0], [1194.4, 3853.0], [1194.2, 1356.0], [1194.1, 1352.0], [1194.0, 1356.0], [1193.8, 1358.0], [1193.7, 9570.0], [1193.5, 9721.0], [1193.2, 16001.0], [1192.7, 399.0]], 'asks': [[1195.0, 495.0], [1195.1, 1361.0], [1195.2, 11066.0], [1195.4, 1360.0], [1195.5, 1361.0], [1195.7, 1360.0], [1195.8, 3867.0], [1195.9, 1370.0], [1196.0, 11731.0], [1196.1, 403.0]]}]

#sum_data_from_db =    sum( [o['amount'] for o in data_from_db  ] )
#print(f'{sum_data_from_db=}')

data_from_db =    list({frozenset(item.items()):item for item in data_from_db}.values())
print(data_from_db)
data_from_db =  string_modification.remove_redundant_elements (data_from_db)
print(data_from_db)

