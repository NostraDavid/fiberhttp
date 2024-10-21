import fiberhttp
from threading import Thread
from time import sleep, time


class counting:
    def __init__(self) -> None:
        self.ok = 0
        self.error = 0


counter = counting()
NUMBER = 1000000
THREADS = 100


def count():
    while counter.ok <= NUMBER:
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f'FiberHTTP Sent {NUMBER} HTTP Requests in {str(time() - start).split('.')[0]} Second With {THREADS} Threads'
    )


def test():
    req = fiberhttp.request("GET", "http://localhost:8082/")
    client = fiberhttp.client(timeout=0.4)
    while counter.ok <= NUMBER:
        try:
            resp = client.send(req)
            print(resp.status_code())
        except Exception:
            counter.error += 1


Thread(target=count).start()
start = time()
for _ in range(THREADS):
    Thread(target=test).start()
