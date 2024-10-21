from threading import Thread
from time import sleep, time

from urllib3 import PoolManager

from common import Counting, debug_info, get_number, get_threads

counter = Counting()
CN_URLLIB3: PoolManager = PoolManager()
NUMBER = get_number()
THREADS = get_threads()
debug_info(NUMBER, THREADS)


def count():
    while counter.can_send(NUMBER):
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f'urllib3 Sent {NUMBER} HTTP Requests in {str(time() - start).split('.')[0]} Second With {THREADS} Threads'
    )


def test():
    while counter.can_send(NUMBER):
        try:
            RES = CN_URLLIB3.request("GET", "http://localhost:8080/")
            if RES.data.decode("utf-8").__contains__("random"):
                counter.increment_ok()
            else:
                counter.increment_error()
        except Exception:
            counter.increment_error()


Thread(target=count).start()

start = time()
for _ in range(THREADS):
    Thread(target=test).start()
