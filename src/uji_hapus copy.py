#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

transaction_order_id=1
result_order_id=[4,5,6,7,8,1]
print(False if transaction_order_id not in result_order_id  else True)