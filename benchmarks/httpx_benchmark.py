# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
# ]
# ///

from httpx import Client
from time import time
from threading import Thread
from benchmark_helper import Counting, count, test_factory, Settings

counter = Counting()
start = time()
client = Client()  # Single instance of Client

def httpx_request(url: str, client: Client) -> bool:
    response = client.get(url)
    return 'random' in response.text

# Wrapping the test function to include the client instance
def wrapped_test():
    test_factory(lambda url: httpx_request(url, client), counter, Settings.NUMBER, Settings.target_url)()

# Start the counting thread
count_thread = Thread(target=count, args=(counter, Settings.NUMBER, Settings.THREADS, 'httpx', start))
count_thread.start()

# Start test threads and collect them in a list
test_threads = [Thread(target=wrapped_test) for _ in range(Settings.THREADS)]
for thread in test_threads:
    thread.start()

# Wait for all test threads to finish
for thread in test_threads:
    thread.join()

# Wait for the counting thread to finish
count_thread.join()

# Close the client after all threads are done
client.close()
