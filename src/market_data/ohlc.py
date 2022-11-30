import asyncio
import websockets
import json, orjson
from utils import time_modification, formula
from datetime import datetime
from loguru import logger as log

async def call_api(msg):
   async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # do something with the response...
           #response: Dict = orjson.loads(response)
           return response

def get_ohlc(instrument_name: str, start_timestamp: int, end_timestamp: int, resolution: str):


    msg = \
    {
    "jsonrpc" : "2.0",
    "id" : 833,
    "method" : "public/get_tradingview_chart_data",
    "params" : {
        "instrument_name" : instrument_name,
        "start_timestamp" : start_timestamp,
        "end_timestamp" : end_timestamp,
        "resolution" : resolution
    }
    }
    result =   asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))
     
    #print (result)
    return orjson.loads(result) ["result"]

def check_and_save_every_1_minutes ():
    from utils import pickling

    qty_candles = 500
        
    now_time = datetime.now()
    now_unix = time_modification.convert_time_to_unix (now_time)
    start_timestamp = now_unix - 60000 * qty_candles
    
    result = ohlc.get_ohlc(instrument, start_timestamp, now_unix, resolution)
    log.warning(result)
    pickling.replace_data('ohlc_1m.pkl', ohlc_1m)
    formula.sleep_and_restart_program (45)


if __name__ == "__main__":
    
    try:

        #check_and_save_every_1_minutes()
        app.run()
        #check_and_save_every_5_minutes()
        #formula.sleep_and_restart_program (600)
                
        #file_name = 'TRXBTC_1h.bin'
        #home_path = str(pathlib.Path.home())
        #data_path = os.path.join(home_path, file_name)
        
    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        
        formula.log_error('open interest','open interest main', error, 10)
        