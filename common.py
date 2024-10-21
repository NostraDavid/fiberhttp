import os
from threading import Lock


class Counting:
    def __init__(self) -> None:
        self.ok = 0
        self.error = 0
        self.sent = 0
        self.lock = Lock()

    def increment_ok(self) -> None:
        with self.lock:
            self.ok += 1
            self.sent += 1

    def increment_error(self) -> None:
        with self.lock:
            self.error += 1
            self.sent += 1

    def can_send(self, number: int) -> bool:
        with self.lock:
            return self.sent < number


def get_number():
    return int(os.environ.get("NUMBER", 100))


def get_threads():
    return int(os.environ.get("THREADS", 100))


def debug_info(threads: int, number: int):
    print("Number of threads: " + str(threads))
    print("Number of requests: " + str(number))
