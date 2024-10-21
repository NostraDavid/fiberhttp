from threading import Thread
from time import sleep, time

from common import Counting, debug_info, get_number, get_threads
from fiberhttp import client, request

counter = Counting()
BUILD = request("GET", "http://localhost:8080/")
NUMBER = get_number()
THREADS = get_threads()
debug_info(NUMBER, THREADS)


def count():
    while counter.can_send(NUMBER):
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f'FiberHTTP Sent {NUMBER} HTTP Requests in {str(time() - start).split('.')[0]} Second With {THREADS} Threads'
    )


def test():
    cn_fiberhttp: client = client(timeout=1)
    while counter.can_send(NUMBER):
        try:
            if cn_fiberhttp.send(BUILD).text().__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


Thread(target=count).start()

start = time()
for _ in range(THREADS):
    Thread(target=test).start()
