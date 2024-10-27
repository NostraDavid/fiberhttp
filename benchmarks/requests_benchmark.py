# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

from requests import Session, PreparedRequest, session
from time import time
from threading import Thread
from benchmark_helper import Counting, count, test_factory, Settings

counter = Counting()
start = time()
CN_REQUESTS: Session = session()

# Prepare the request
BUILD = PreparedRequest()
BUILD.prepare(method="GET", url=Settings.target_url)

def requests_request(url: str) -> bool:
    response = CN_REQUESTS.send(BUILD)
    return 'random' in response.text

# Start counting thread
Thread(target=count, args=(counter, Settings.NUMBER, Settings.THREADS, 'requests', start)).start()

# Start test threads
for _ in range(Settings.THREADS):
    Thread(target=test_factory(requests_request, counter, Settings.NUMBER, Settings.target_url)).start()
