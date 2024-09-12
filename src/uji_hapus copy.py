#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

from strategies.config_strategies import (hedging_spot_attributes,preferred_spot_currencies,paramaters_to_balancing_transactions,strategies)

active_strategies=''

log.warning (not active_strategies.strip())
log.warning (active_strategies=="")
