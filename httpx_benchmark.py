from httpx import Client, Request
from threading import Thread
from time import sleep, time
import os


class counting:
    def __init__(self) -> None:
        self.ok = 0
        self.error = 0


counter = counting()
NUMBER = os.environ.get("NUMBER", 100)
THREADS = os.environ.get("THREADS", 100)

BUILD = Request("GET", "http://localhost:8080/")


def count():
    while counter.ok <= NUMBER:
        print(f"\rOK = {counter.ok}; ERR = {counter.error}", end=" ")
        sleep(0.1)
    print(f"\rOK = {counter.ok}; ERR = {counter.error}")
    print(
        f'httpx Sent {NUMBER} HTTP Requests in {str(time() - start).split('.')[0]} Second With {THREADS} Threads'
    )


def test():
    CN_HTTPX: Client = Client()
    while counter.ok <= NUMBER:
        try:
            if CN_HTTPX.send(BUILD).text.__contains__("random"):
                counter.ok += 1
            else:
                counter.error += 1
        except:
            counter.error += 1


Thread(target=count).start()

start = time()
for _ in range(THREADS):
    Thread(target=test).start()
