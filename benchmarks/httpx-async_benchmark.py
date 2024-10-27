# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
# ]
# ///

import asyncio
from httpx import AsyncClient
from asyncio import gather
from time import time
from benchmark_helper import Counting, async_count, Settings

counter = Counting()
start = time()

async def httpx_async_request(client: AsyncClient, url: str) -> bool:
    try:
        response = await client.get(url)
        return 'random' in response.text
    except Exception as e:
        print(f"Request failed: {e}")
        return False

async def test(client: AsyncClient):
    while counter.ok <= Settings.NUMBER:
        if await httpx_async_request(client, Settings.target_url):
            counter.ok += 1
        else:
            counter.error += 1

async def main():
    async with AsyncClient() as client:
        # Start the counting task
        tasks = [async_count(counter, Settings.NUMBER, Settings.THREADS, "httpx-async", start)]
        
        # Start the test tasks
        tasks.extend([test(client) for _ in range(Settings.THREADS)])
        
        # Run all tasks concurrently
        await gather(*tasks)

# Run the async event loop
asyncio.run(main())
