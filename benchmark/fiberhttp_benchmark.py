import sys
from threading import Thread
from time import sleep, time

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from structlog.stdlib import get_logger

from fiberhttp import client, request

logger = get_logger()
counter = Counting()
NUMBER = get_number()
THREADS = get_threads()
debug_info(NUMBER, THREADS)


def count():
    while counter.can_send(NUMBER):
        # logger.debug("stats", ok=counter.ok, error=counter.error)
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
    BUILD = request("GET", "http://localhost:8080/")
    _client: client = client(timeout=1)
    while counter.can_send(NUMBER):
        try:
            if _client.send(BUILD).text().__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()
    _client.close()


Thread(target=count).start()
start = time()
for _ in range(THREADS):
    Thread(target=test).start()
