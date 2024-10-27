# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp",
# ]
# ///

import asyncio
from aiohttp import ClientSession, TCPConnector
from asyncio import gather
from time import time
from benchmark_helper import Counting, async_count, Settings

counter = Counting()
start = time()

async def aiohttp_request(session: ClientSession, url: str) -> bool:
    try:
        async with session.get(url) as response:
            text = await response.text()
            return 'random' in text
    except Exception as e:
        print(f"Request failed: {e}")
        return False

async def test(session: ClientSession):
    while counter.ok <= Settings.NUMBER:
        if await aiohttp_request(session, Settings.target_url):
            counter.ok += 1
        else:
            counter.error += 1

async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        # Start the counting task
        tasks = [async_count(counter, Settings.NUMBER, Settings.THREADS, "aiohttp", start)]
        
        # Start the test tasks
        tasks.extend([test(session) for _ in range(Settings.THREADS)])
        
        # Run all tasks concurrently
        await gather(*tasks)

# Run the async event loop
asyncio.run(main())
