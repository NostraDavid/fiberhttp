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

# Define 'start' before starting the count thread
start = time()


def count():
    while counter.can_send(NUMBER):
        # Uncomment the next line if you want to log debug stats periodically
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
    _client = HTTPConnection("localhost", timeout=1)
    while counter.can_send(NUMBER):
        try:
            _client.request("GET", "/")
            res = _client.getresponse()
            response_body = res.read().decode("utf-8")
            if "random" in response_body:
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception as e:
            logger.error("Request failed", error=str(e))
            counter.increment_error()


# Create and start the count thread
count_thread = Thread(target=count)
count_thread.start()

# Create and start test threads
test_threads = []
for _ in range(THREADS):
    t = Thread(target=test)
    t.start()
    test_threads.append(t)

# Optionally, wait for all threads to complete
for t in test_threads:
    t.join()

# Wait for the count thread to finish
count_thread.join()
