from threading import Thread
from time import sleep, time

from httpx import Client, Request

from common import Counting, debug_info, get_number, get_threads

counter = Counting()
BUILD = Request("GET", "http://localhost:8080/")
NUMBER = get_number()
THREADS = get_threads()

debug_info(NUMBER, THREADS)


def count():
    while counter.can_send(NUMBER):
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f'httpx Sent {NUMBER} HTTP Requests in {str(time() - start).split('.')[0]} Second With {THREADS} Threads'
    )


def test():
    CN_HTTPX: Client = Client()
    while counter.can_send(NUMBER):
        try:
            if CN_HTTPX.send(BUILD).text.__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


Thread(target=count).start()

start = time()
for _ in range(THREADS):
    Thread(target=test).start()
