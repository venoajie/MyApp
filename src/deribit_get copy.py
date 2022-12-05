"""
Description:
    Deribit RESToverHTTP [POST] Asyncio Example.
    - Authenticated request.
Usage:
    python3.9 dbt-post-authenticated-example.py
Requirements:
    - aiohttp >= 3.8.1
"""

# built ins
import asyncio
import logging
from typing import Dict
import os
# installed
import aiohttp
from aiohttp.helpers import BasicAuth
from dotenv import load_dotenv
from os.path import join, dirname
from dataclassy import dataclass
from utils import system_tools, pickling
from loguru import logger as log

import websockets
import asyncio
import orjson, json
# user defined formula
from configuration import id_numbering

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

    print ('LLLLLLLLLLLLLLLLLLLLLLLL')

