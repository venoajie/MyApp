import json
import time
import asyncio
import websockets


def init_md_heartbeat(md_hb_value, running):

    while running:
        if(md_hb_value.value <= 0): #i used a multiprocessing value, to share memory across processes
            md_hb_value.value = 1
            # print("md_heartbeat   -- beating setting value to -- [{0}]".format(md_hb_value.value))
        else:
            # print("md_heartbeat -- SKIP beating VALUE -- [{0}] SLEEPING".format(md_hb_value.value))
            pass
        time.sleep(1.5) #probably don't want to hardcoded values like these


async def websocket_connect(access_token, ws_url):
    warmup   = True
    msg      = None
    init_msg = None
    init_s   = None
    a_seq_n  = 0     #this is a good habit of recording certain sequence numbers to match when you get a response from the websocket api.
    init     = "authorize\n{0}\n\n{1}".format(a_seq_n, access_token)
    mdws     = await websockets.connect(ws_url, ssl=True, compression=None)

    while warmup:
        try:
            msg = await mdws.recv()
        except Exception as e:
            print("websocket_connect -- await mdws.recv() Exception -- [{0}]\n\n".format(str(e)))

        if(msg[0] == "o"):
            try:
                await mdws.send(init)
            except Exception as e:
                print("websocket_connect -- await mdws.send(init) Exception -- [{0}]\n\n".format(str(e)))

        if(msg != "o"):
            try:
                init_s = json.loads(msg[2:-1])
                if(init_s["s"] == 200 and init_s['d']['i'] == a_seq_n): #use this seq_num check pattern 
                    print("websocket_connect -- successfully authorized -- \n[{0}]\n[{1}]\n\n".format(ws_url, msg))
                    warmup = False
                    break
            except Exception as e:
                    print("websocket_connect -- Exception -- [{0}]".format(str(e)))

                    
        if(warmup == False):
            print("websocket_connect -- exiting warmup -- ")
            break

    return mdws



async def marketdata_run(management_pkg):
    payload          = management_pkg['payload'] #payload is the json payload you get back from the authentication request
    """ I keep predefine certain commonly used variables to avoid creating garbage doing my main loop"""
    md_hb_value      = management_pkg['md_hb_value']
    access_token     = payload['accessToken']

    heartbeat_thread = None
    heartbeat_count  = 0
    running          = False
    item             = None
    bid              = 0.0
    ask              = 0.0

    low              = 0.0
    high             = 0.0
    last_bid         = 0.0
    last_ask         = 0.0
    last_trade       = 0.0


    last_trade_price = 0.0
    bid_low_price    = 0.0
    bid_hig_price    = 0.0
    ask_low_price    = 0.0
    ask_hig_price    = 0.0
    open_position    = False
    open_price       = 0.0



    DEMO = True


    if(DEMO):
        WS_URL  = management_pkg['md_demo_wss'] 
        accountSpec      = payload['DEMO_ACCOUNT_SPEC'] #REPLACE THESE
        accountId        = payload['DEMO_USER_ID']

    else:
        accountSpec      = payload['name']
        accountId        = payload['userId']
        WS_URL  = management_pkg['md_live_wss'] 

    ws  = await websocket_connect(access_token, MD_WS_URL)
    if(ws):
        heartbeat_thread = threading.Thread(target=init_md_heartbeat, args=(md_hb_value, True))
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        running = True


    while running:
        try:
            msg = await ws.recv()
        except Exception as e:
            print("marketdata_run -- msg = await ws.recv() got exception -- [{0}]".format(str(e)))


        if(msg):
            msg_t = msg[0]
            if(msg_t == "a"):
                jmsg = json.loads(msg[2:-1])
                try:
                    event_msg = jmsg['e']
                    response_msg = False
                except Exception as e:
                    response_msg = jmsg['s']
                    event_msg = False

                if(event_msg):
                    try:
                        item             = jmsg['d']['quotes']
                    except Exception as e:
                        item = None

                    if(item == None):
                        continue
                    else
                        for ix, itm in enumerate(item):
                            low        = itm['entries']['LowPrice']['price']
                            high       = itm['entries']['HighPrice']['price']
                            bid        = itm['entries']['Bid']['price']
                            ask        = itm['entries']['Offer']['price']
                            last       = itm['entries']['Trade']['price']
                            #================ USE MARKETDATA TO do SOMETHING USEFUL BEGIN ============================
                            #
                            #
                            #
                            #================ USE MARKETDATA TO do SOMETHING USEFUL  END  ============================
                else:
                    response_status = jmsg['s']
                    if(response_status == 200):
                        response_id     = jmsg['i']
                        response_pld    = jmsg['d']

                    else:
                        print("got response ERROR --\n{0}\n".format(jmsg))
            elif(msg_t == "h"):
                print("\tmarketdata_run -- MD -- heartbeat -- ")
            elif(msg_t == "c"):
                print("marketdata_run -- close message -- [{0}]".format(msg))
            else:
                pass


        if(md_hb_value.value >= 1.0):
            try:
                await ws.send("[]")
                md_hb_value.value -= 1
            except Exception as e:
                print("\nmarketdata_run -- WEBSOCKET -- sent heartbeat EXCEPTION -- [{0}] [{1}]".format(md_hb_value.value, str(e)))




def marketdata_init(management_pkg):
    marketdata_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(marketdata_loop)
    marketdata_loop.run_until_complete(marketdata_run(management_pkg))