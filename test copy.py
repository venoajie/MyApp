#!/usr/bin/env python

import random
import asyncio
import websockets
import time
from loguru import logger as log

async def say_after(delay, what):
    await asyncio.sleep(delay)
    log.error(what)

async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello')) # not block here

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    log.debug(f"started at {time.strftime('%X')}") # time0

    await task1 # block here!

    log.info(f"finished at {time.strftime('%X')}") 
    
    await task2 # block here!

    log.warning(f"finished at {time.strftime('%X')}")

async def main2():
    task1 = asyncio.create_task(
        say_after(1, 'hello')) # not block here
    log.info(f"finished at {time.strftime('%X')}") # time0
    await asyncio.sleep(2) # not await task1
    log.warning(f"finished at {time.strftime('%X')}") # time0+2
 
asyncio.run(main())
print ('ganti')
asyncio.run(main2())