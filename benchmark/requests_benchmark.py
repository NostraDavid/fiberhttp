import sys
from threading import Thread
from time import sleep, time

from common import SLEEP_TIME, Counting, debug_info, get_number, get_threads
from requests import PreparedRequest, Session
from structlog.stdlib import get_logger

logger = get_logger()
counter = Counting()
NUMBER = get_number()
THREADS = get_threads()
debug_info(NUMBER, THREADS)

start = time()  # Initialize start before starting threads


def count():
    while counter.can_send(NUMBER):
        # Uncomment the next line for detailed debug logs
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
    _client: Session = Session()  # Correct instantiation of Session
    while counter.can_send(NUMBER):
        try:
            # Create a new PreparedRequest for each request to ensure thread safety
            build = PreparedRequest()
            build.url = "http://localhost:8080/"
            build.method = "GET"
            response = _client.send(build.prepare())
            if "random" in response.text:
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception as e:
            logger.error("Request failed", error=str(e))
            counter.increment_error()


# Start the count thread
count_thread = Thread(target=count, name="CountThread")
count_thread.start()

# Start the test threads
test_threads = []
for i in range(THREADS):
    thread = Thread(target=test, name=f"TestThread-{i+1}")
    thread.start()
    test_threads.append(thread)

# Optionally, wait for all threads to complete
count_thread.join()
for thread in test_threads:
    thread.join()

logger.info("All threads have completed execution.")
