import sys
import asyncio
from asyncio import gather, sleep
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

start = time()  # Moved before function definitions to ensure accessibility


async def count(start_time: float):
    while counter.can_send(NUMBER):
        # logger.adebug("stats", ok=counter.ok, error=counter.error)  # Removed await
        # logger.debug("stats", ok=counter.ok, error=counter.error)
        await sleep(SLEEP_TIME)
    logger.info("stats", ok=counter.ok, error=counter.error)
    logger.info(
        "end-stats",
        file=sys.argv[0],
        requests=NUMBER,
        request_time=int(time() - start_time),
        threads=THREADS,
    )


async def test(client: AsyncClient):
    while counter.can_send(NUMBER):
        try:
            REQ = await client.send(BUILD)
            if "random" in REQ.text:
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception as e:
            counter.increment_error()
            logger.error("request_failed", error=str(e))


async def main():
    async with AsyncClient() as client:
        tasks = []
        tasks.append(count(start))
        for _ in range(THREADS):
            tasks.append(test(client))
        await gather(*tasks)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Program interrupted by user")
