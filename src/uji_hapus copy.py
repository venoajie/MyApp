#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

text =  "instrument_name", "label", "amount_dir as amount"
print(','.join(str(i) for i in text))