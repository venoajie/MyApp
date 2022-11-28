import asyncio
import websockets
import json, orjson

msg = \
{
  "jsonrpc" : "2.0",
  "id" : 833,
  "method" : "public/get_tradingview_chart_data",
  "params" : {
    "instrument_name" : "ETH-PERPETUAL",
    "start_timestamp" : 1554373800000,
    "end_timestamp" : 1554376800000,
    "resolution" : "30"
  }
}

async def call_api(msg):
   async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # do something with the response...
           #response: Dict = orjson.loads(response)
           return (response)

response = asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))
print (response)
