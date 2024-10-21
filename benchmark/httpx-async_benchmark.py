import sys
from asyncio import gather, new_event_loop, sleep
from time import time

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from httpx import AsyncClient, Request
from structlog.stdlib import get_logger

logger = get_logger()
counter = Counting()
BUILD = Request("GET", "http://localhost:8080/")
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)


async def count():
    while counter.can_send(NUMBER):
        # await logger.adebug("stats", ok=counter.ok, error=counter.error)
        await sleep(SLEEP_TIME)
    await logger.ainfo("stats", ok=counter.ok, error=counter.error)
    await logger.ainfo(
        "end-stats",
        file=sys.argv[0],
        requests=NUMBER,
        request_time=int(time() - start),
        threads=THREADS,
    )


async def test():
    _client: AsyncClient = AsyncClient()
    while counter.can_send(NUMBER):
        try:
            REQ = await _client.send(BUILD)
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
