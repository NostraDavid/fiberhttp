# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fiberhttp",
# ]
# ///

from fiberhttp import Client, Request
from time import time
from threading import Thread
from benchmark_helper import Counting, count, test_factory, Settings

counter = Counting()
start = time()
request_template = Request("GET", Settings.target_url)  # Prepare the request template once

def fiberhttp_request(url: str, client: Client) -> bool:
    try:
        response = client.send(request_template)
        result = 'random' in response.text()
        
        if not result:
            print("Unexpected response, retrying...")
            # Retry once if the first attempt fails
            response = client.send(request_template)
            result = 'random' in response.text()
        
        return result
    except Exception as e:
        print(f"Request failed: {e}")
        return False

# Wrapping the test function to reuse a client instance within each thread
def wrapped_test():
    client = Client(timeout=0.4)  # Create a single client instance per thread
    try:
        test_factory(lambda url: fiberhttp_request(url, client), counter, Settings.NUMBER, Settings.target_url)()
    finally:
        client.close()  # Close the client after all requests are complete in this thread

# Start the counting thread
count_thread = Thread(target=count, args=(counter, Settings.NUMBER, Settings.THREADS, "FiberHTTP", start))
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
