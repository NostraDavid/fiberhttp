from dataclasses import dataclass
from time import time, sleep
from asyncio import sleep as async_sleep
from typing import Callable

@dataclass
class Settings:
    target_url = 'http://localhost:8080/'
    # NUMBER = 1_000_000
    NUMBER = 10_000
    THREADS = 10

@dataclass
class Counting:
    ok = 0
    error = 0

# sync code

def count(counter: Counting, number: int, threads: int, client_name: str, start: float):
    """Monitors the request count progress and outputs final stats."""
    while counter.ok <= number:
        print(f'\rOK = {counter.ok}; ERR = {counter.error}', end=' ')
        sleep(0.1)
    print(f'\rOK = {counter.ok}; ERR = {counter.error}')
    print(f'{client_name} Sent {number} HTTP Requests in {int(time() - start)} Seconds With {threads} Threads')

def test_factory(request_func: Callable[[str], bool], counter: Counting, number: int, url: str) -> Callable[[], None]:
    """Generates a test function tailored to a specific HTTP client."""
    def test():
        while counter.ok <= number:
            try:
                if request_func(url):
                    counter.ok += 1
                else:
                    counter.error += 1
            except Exception:
                counter.error += 1
    return test

# async code

async def async_count(counter: Counting, number: int, threads: int, client_name: str, start: float):
    """Asynchronous variant of count for async clients."""
    while counter.ok <= number:
        print(f'\rOK = {counter.ok}; ERR = {counter.error}', end=' ')
        await async_sleep(0.1)
    print(f'\rOK = {counter.ok}; ERR = {counter.error}')
    print(f'{client_name} Sent {number} HTTP Requests in {int(time() - start)} Seconds With {threads} Threads')

async def async_test_factory(request_func: Callable[[str], bool], counter: Counting, number: int, url: str):
    """Asynchronous variant of the test factory."""
    async def test():
        while counter.ok <= number:
            try:
                if await request_func(url):
                    counter.ok += 1
                else:
                    counter.error += 1
            except Exception:
                counter.error += 1
    return test
