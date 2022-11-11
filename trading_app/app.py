import websocket
import json
import time
from datetime import datetime

def main():
    
    # 거래소에서 발급 받은 publick, secret key
    client_id = 'F1Gp2cmS'
    client_secret = 'gp9Vh9ft9qeaLWwBlCTnhobz1MwDFLrg84L9Spx7haQ'
    
    def on_message(ws, message):
        # 아래 ws.send() 에서 보낸 return message 받는 func
        msg = json.loads(message)
        
        try:
            price = msg['params']['data']['close']
            
            # 현재 가격을 불러와 5000$ 이하일 경우 40$ 만큼 시장가로 주문
            if price < 5000:
                data = {
                    "method": "/private/buy",
                    "params": {
                        "amount": 40,
                        "instrument_name": "BTC-PERPETUAL",
                        "label": "market0000234",
                        "type": "market"
                    },
                    "jsonrpc": "2.0",
                    "id": 34
                }
                ws.send(json.dumps(data))
            
        except:
            pass

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        
        data = {
            "id" :  27,
            "method": "public/auth",
            "params":{
                "grant_type": "client_credentials",
                "scope": "session:apiconsole-aiczudeyx0n",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            "jsonrpc": "2.0"
        }
        # access token 값 받기
        ws.send(json.dumps(data))

        data = {
            "method": "/private/subscribe",
            "params": {
                "channels": ["chart.trades.BTC-PERPETUAL.60"],
            }
        }
        # 위에서 받아온 access token 값으로 private 값 불러 오기
        ws.send(json.dumps(data))
    
    websocket.enableTrace(True)
    
    ws = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v2/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    main()
