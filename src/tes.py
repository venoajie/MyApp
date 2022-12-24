#!/usr/bin/env python3
import asyncio

import aiohttp


async def fetch(session: aiohttp.ClientSession) -> None:
    print("Query http://httpbin.org/basic-auth/andrew/password")
    async with session.get("https://test.deribit.com/api/v2/'") as resp:
        print(resp.status)
        body = await resp.text()
        print(body)


async def go() -> None:
    async with aiohttp.ClientSession(
        auth=aiohttp.BasicAuth("7aDpbWD0", "M5xtKo6i-maY0y1MaO6a4uV1S6SKhGaraCQ_vY_D_pE")
    ) as session:
        await fetch(session)


loop = asyncio.get_event_loop()
loop.run_until_complete(go())