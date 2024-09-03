#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

text = 'ETH-PERPETUAL.1'
test = text.partition('.')[0]

print (test)
print (text.partition('...')
)