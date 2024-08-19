
import asyncio
import random

class Demo:
    def __init__(self):
        self.queue = asyncio.Queue(1)

    async def one(self):
        ltp = 0
        while True:
            ltp += random.uniform(-1, 1)
            await self.queue.put(ltp)

    async def two(self):
        while True:
            ltp = await self.queue.get()
            print(ltp)
            await asyncio.sleep(0)

loop = asyncio.get_event_loop()
d = Demo()
loop.create_task(d.one())
loop.create_task(d.two())
loop.run_forever()