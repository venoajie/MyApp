from utils import pickling
from loguru import logger as log
import pickle

resp = {
      "volume": 0,
      "tick": 1669939620000,
      "open": 1276.65,
      "low": 1276.65,
      "high": 1276.65,
      "cost": 0,
      "close": 1276.65
    }

data = pickling.read_data ('test.pkl')
#log.critical (([o   for o in data ]))

pickling.append_data('test', resp)
data = pickling.read_data ('test.pkl')
#log.warning ([o   for o in data ])

len_tick_data = len ([o['tick']  for o in data ])  
#log.error (len_tick_data)

if len_tick_data > 3:
  filter = [min([o['tick']  for o in data ])]
  log.critical (filter)
  result = ([o for o in data if o['tick'] not in filter ])
 # print (result)

  with open('test.pkl','wb') as handle:
      pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
result = pickling.read_data ('test.pkl')
log.debug (result)
