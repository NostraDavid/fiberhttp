# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

from http.client import HTTPConnection
from time import time
from threading import Thread
from benchmark_helper import Counting, count, test_factory, Settings

counter = Counting()
start = time()

def http_client_request(url: str) -> bool:
    # Create a new connection instance for each thread
    connection = HTTPConnection("localhost", 8080, timeout=1)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        result = 'random' in response.read().decode("utf-8")
        
        if not result:
            print("Unexpected response, retrying...")
            # Retry once if the first attempt fails
            connection.request("GET", "/")
            response = connection.getresponse()
            result = 'random' in response.read().decode("utf-8")
        
        return result
    except Exception as e:
        print(f"Request failed: {e}")
        return False
    finally:
        # Ensure the connection is closed after each request
        connection.close()

# Wrapping the test function without reusing a shared connection
def wrapped_test():
    test_factory(http_client_request, counter, Settings.NUMBER, Settings.target_url)()

# Start the counting thread
count_thread = Thread(target=count, args=(counter, Settings.NUMBER, Settings.THREADS, "http.client", start))
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
