from httpx import AsyncClient, Request
from asyncio import sleep, gather, new_event_loop
import os
from time import time

class counting:
    def __init__(self) -> None:
        self.ok = 0
        self.error = 0

counter = counting()
NUMBER = os.environ.get("NUMBER", 100)
THREADS = os.environ.get("THREADS", 100)

BUILD = Request('GET', 'http://localhost:8080/')

async def count():
    while counter.ok <= NUMBER:
        print(f'\rOK = {counter.ok}; ERR = {counter.error}', end=' ')
        await sleep(0.1)
    print(f'\rOK = {counter.ok}; ERR = {counter.error}')
    print(f'httpx-async Sent {NUMBER} HTTP Requests in {int(time() - start)} Seconds With {THREADS} Threads')

async def test():
    CN_HTTPX : AsyncClient = AsyncClient()
    while counter.ok <= NUMBER:
        try:
            REQ = await CN_HTTPX.send(BUILD)
            if REQ.text.__contains__('random'):
                counter.ok += 1
            else:
                counter.error += 1
        except:
            counter.error += 1

async def main():
    tasks = []
    tasks.append(count())
    for _ in range(THREADS):
        tasks.append(test())
    await gather(*tasks)

start = time()
loop = new_event_loop()
loop.run_until_complete(main())
loop.close()
