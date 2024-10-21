from asyncio import gather, new_event_loop, sleep
from time import time

from httpx import AsyncClient, Request

from common import Counting, debug_info, get_number, get_threads

counter = Counting()
BUILD = Request("GET", "http://localhost:8080/")
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)


async def count():
    while counter.can_send(NUMBER):
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        await sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f"httpx-async Sent {NUMBER} HTTP Requests in {int(time() - start)} Seconds With {THREADS} Threads"
    )


async def test():
    cn_httpx: AsyncClient = AsyncClient()
    while counter.can_send(NUMBER):
        try:
            REQ = await cn_httpx.send(BUILD)
            if REQ.text.__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


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
