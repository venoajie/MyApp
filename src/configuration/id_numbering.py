#!/usr/bin/env python
def id (operation, ws_channel):
    
    id_method = 0
    if 'subscribe' in operation:
        id_method = 3
    if 'get' in operation:
        id_method = 4
    id_item = 0
    if 'book' in ws_channel:
        id_item = 1
    if 'user' in ws_channel:
        id_item = 2
    if 'chart' in ws_channel:
        id_item = 3
    if 'index' in ws_channel:
        id_item = 4
    if 'order' in ws_channel:
        id_item = 5
    if 'position' in ws_channel:
        id_item = 6
    id_instrument = 0
    if 'BTC'or 'btc' in ws_channel:
        id_instrument = 1
    if 'ETH' or 'eth' in ws_channel:
        id_instrument = 2
    return int(f'{id_method}{id_item}{id_instrument}')
