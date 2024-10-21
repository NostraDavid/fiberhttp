import sys
from threading import Thread
from time import sleep, time

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from httpx import Client, Request
from structlog.stdlib import get_logger

logger = get_logger()
counter = Counting()
BUILD = Request("GET", "http://localhost:8080/")
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)

# Initialize the start time before starting any threads
start = time()


def count():
    while counter.can_send(NUMBER):
        # Uncomment the following line if you need debug logs
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
    with Client() as _client:
        while counter.can_send(NUMBER):
            try:
                response = _client.send(BUILD)
                if "random" in response.text:
                    counter.increment_ok()
                else:
                    counter.increment_error()
            except Exception as e:
                logger.error("Request failed", error=str(e))
                counter.increment_error()


# Start the count thread
count_thread = Thread(target=count, name="CountThread", daemon=True)
count_thread.start()

# Start the test threads
test_threads = []
for i in range(THREADS):
    thread = Thread(target=test, name=f"TestThread-{i+1}", daemon=True)
    thread.start()
    test_threads.append(thread)

# Optionally, wait for all test threads to complete
for thread in test_threads:
    thread.join()

# Wait for the count thread to finish
count_thread.join()
