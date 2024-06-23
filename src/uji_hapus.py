#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log


async def run_every_15_seconds() -> None:
    """ """
    import datetime
    stop_time = datetime.datetime.now() + datetime.timedelta(hours=1)

    # ...
    print (f"stop_time {stop_time} datetime.datetime.now() {datetime.datetime.now()}")

    # in relevant function ...
    if datetime.datetime.now() > stop_time:
        print (f"test")

if __name__ == "__main__":

    try:
        # asyncio.get_event_loop().run_until_complete(check_and_save_every_60_minutes())

        schedule.every(1).seconds.do(run_every_15_seconds)

        loop = asyncio.get_event_loop()

        while True:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(0.91)

    except Exception as error:
        print(error)
