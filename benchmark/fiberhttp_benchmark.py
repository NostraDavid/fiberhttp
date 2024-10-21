import sys
from threading import Thread
from time import sleep, time
from typing import Any

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from structlog.stdlib import get_logger

import fiberhttp


class counting:
    def __init__(self) -> None:
        self.ok = 0
        self.error = 0


logger = get_logger()
counter = counting()
NUMBER = get_number()
THREADS = get_threads()
debug_info(NUMBER, THREADS)


def count():
    while counter.ok <= NUMBER:
        logger.debug("stats", ok=counter.ok, error=counter.error)
        sleep(SLEEP_TIME)
    logger.info("stats", ok=counter.ok, error=counter.error)
    logger.info(
        "end-stats",
        file=sys.argv[0],
        requests=NUMBER,
        request_time=int(time() - start),
        threads=THREADS,
    )


def test():
    req = fiberhttp.request("GET", "http://localhost:8082/")
    client = fiberhttp.client(timeout=0.4)
    while counter.ok <= NUMBER:
        try:
            if client.send(req).text().__contains__("random"):
                counter.ok += 1
            else:
                counter.error += 1
        except Exception:
            counter.error += 1
    client.close()


Thread(target=count).start()
start = time()
for _ in range(THREADS):
    Thread(target=test).start()
