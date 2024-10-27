# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "urllib3",
# ]
# ///

from urllib3 import PoolManager
from time import time
from threading import Thread
from benchmark_helper import Counting, count, test_factory, Settings

counter = Counting()
start = time()
client = PoolManager()

def urllib3_request(url: str) -> bool:
    response = client.request('GET', url)
    return 'random' in response.data.decode('utf-8')

# Start counting thread
Thread(target=count, args=(counter, Settings.NUMBER, Settings.THREADS, 'urllib3', start)).start()

# Start test threads
for _ in range(Settings.THREADS):
    Thread(target=test_factory(urllib3_request, counter, Settings.NUMBER, Settings.target_url)).start()
