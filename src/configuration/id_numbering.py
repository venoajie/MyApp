#!/usr/bin/env python
def id (operation, ws_channel):
    id_method = 0
    if 'subscribe' in operation:
        id_method = 3
    if 'get' in operation:
        id_method = 4
    id_auth = 0
    if 'book' in ws_channel:
        id_auth = 1
    if 'user' in ws_channel:
        id_auth = 2
    if 'private' in operation:
        id_auth = 2
    id_instrument = 0
    if 'BTC'or 'btc' in ws_channel:
        id_instrument = 1
    if 'ETH' or 'eth' in ws_channel:
        id_instrument = 2
    return int(f'{id_method}{id_auth}{id_instrument}')
