#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from loguru import logger as log
from unsync import unsync
from dataclassy import dataclass
from functools import lru_cache
import ccxt.async_support as ccxt

            
def get_orderbook(self, instrument, depth=5):
    params = {
        "instrument_name": instrument,
        "depth": depth
    }
    self.msg["method"] = "public/get_order_book"
    self.msg["params"] = params

    return self.async_loop(self.pub_api, json.dumps(self.msg))


if __name__ == "__main__":
        
    try:

        print(asyncio.run(fetch_tickers()))
        
    except Exception as error:
        import traceback
        log.error(f'{error=}')
        log.error(traceback.format_exc())
        print (f" sleep dan restart setelah error 10 detik ")
