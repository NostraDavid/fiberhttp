import sys
from http.client import HTTPConnection
from threading import Thread
from time import sleep, time

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from structlog.stdlib import get_logger

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
    _client: HTTPConnection = HTTPConnection("localhost", timeout=1)
    while counter.can_send(NUMBER):
        try:
            _client.request("GET", "/")
            res = _client.getresponse()
            if res.read().decode("utf-8").__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


Thread(target=count).start()
start = time()
for _ in range(THREADS):
    Thread(target=test).start()
