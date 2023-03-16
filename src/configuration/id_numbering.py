#!/usr/bin/env python
def id(operation, ws_channel):
    """

    id convention

    method
    subscription    3
    get             4

    auth
    public	        1
    private	        2

    instruments
    all             0
    btc             1
    eth             2

    subscription
    --------------  method      auth    seq    inst
    portfolio	        3	    1	    01
    user_order	        3	    1	    02
    my_trade	        3	    1	    03
    order_book	        3	    2	    04
    trade	            3	    1	    05
    index	            3	    1	    06
    announcement	    3	    1	    07

    get
    --------------
    currencies	        4	    2	    01
    instruments	        4	    2	    02
    positions	        4	    1	    03

    """
    id_auth = 1
    if "user" in ws_channel:
        id_auth = 9

    id_method = 0
    if "subscribe" in operation:
        id_method = 3
    if "get" in operation:
        id_method = 4
    id_item = 0
    if "book" in ws_channel:
        id_item = 1
    if "user" in ws_channel:
        id_item = 2
    if "chart" in ws_channel:
        id_item = 3
    if "index" in ws_channel:
        id_item = 4
    if "order" in ws_channel:
        id_item = 5
    if "position" in ws_channel:
        id_item = 6
    id_instrument = 0
    if "BTC" or "btc" in ws_channel:
        id_instrument = 1
    if "ETH" or "eth" in ws_channel:
        id_instrument = 2
    return int(f"{id_auth}{id_method}{id_item}{id_instrument}")
