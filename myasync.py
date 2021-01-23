import asyncio
import aiohttp
from asyncio_throttle import Throttler

URL = 'https://enogxgpck423p.x.pipedream.net'

async def fetch(session, url, throttler, counter):
    async with throttler:
        async with session.post(url, data = "'{'something': 'somethinglese'}") as response:
            json_response = response
            print(str(counter) + ' ----- ' + str(json_response))


async def main():
    tasks = []
    throttler = Throttler(rate_limit=20, period=1)
    conn = aiohttp.TCPConnector(limit=30)
    async with aiohttp.ClientSession(connector=conn) as session:
        for _ in range(100):
            tasks.append(fetch(session, URL, throttler, _))
        
        await asyncio.gather(*tasks)


asyncio.run(main())