from asyncio import gather, new_event_loop, sleep
from time import time

from aiohttp import ClientSession, TCPConnector

from common import Counting, debug_info, get_number, get_threads

counter = Counting()
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)


async def count():
    while counter.can_send(NUMBER):
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        await sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f"aiohttp Sent {NUMBER} HTTP Requests in {int(time() - start)} Seconds With {THREADS} Threads"
    )


async def test(aiohttp_cn: ClientSession):
    while counter.can_send(NUMBER):
        try:
            req = await aiohttp_cn.get("http://localhost:8080/")
            res = await req.text()
            if res.__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


async def main():
    connector = TCPConnector(ssl=False)
    aiohttp_cn = ClientSession(connector=connector)

    tasks = []
    tasks.append(count())
    for _ in range(THREADS):
        tasks.append(test(aiohttp_cn))
    await gather(*tasks)
    await aiohttp_cn.close()


start = time()
loop = new_event_loop()
loop.run_until_complete(main())
loop.close()
