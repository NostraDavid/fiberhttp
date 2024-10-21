import sys
from asyncio import gather, new_event_loop, sleep
from time import time

from aiohttp import ClientSession, TCPConnector
from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from structlog.stdlib import get_logger

logger = get_logger()
counter = Counting()
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)


async def count():
    while counter.can_send(NUMBER):
        # Use synchronous logging without await
        # logger.debug("stats", ok=counter.ok, error=counter.error)
        await sleep(SLEEP_TIME)

    logger.info("stats", ok=counter.ok, error=counter.error)
    logger.info(
        "end-stats",
        file=sys.argv[0],
        requests=NUMBER,
        request_time=int(time() - start),
        threads=THREADS,
    )


async def test(_client: ClientSession):
    while counter.can_send(NUMBER):
        try:
            async with _client.get("http://localhost:8080/") as req:
                res = await req.text()
                if "random" in res:
                    counter.increment_ok()
                else:
                    counter.increment_error()
        except Exception as e:
            logger.error("Request failed", error=str(e))
            counter.increment_error()


async def main():
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as aiohttp_cn:
        tasks = [count()] + [test(aiohttp_cn) for _ in range(THREADS)]
        await gather(*tasks)


start = time()
# It's recommended to use asyncio.run for simplicity and better loop management
import asyncio

asyncio.run(main())
