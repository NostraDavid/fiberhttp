# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp",
#     "fiberhttp",
#     "httpx",
#     "requests",
#     "structlog",
#     "urllib3",
# ]
# ///

import structlog
from collections import OrderedDict
import logging
import warnings
import time
import requests
import http.client
from urllib3 import PoolManager
import asyncio
import httpx
import aiohttp
import fiberhttp
from typing import Callable, Tuple
from settings import settings

logging.basicConfig(level=logging.INFO, format="%(message)s")
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        lambda logger, method_name, event_dict: OrderedDict(
            [
                ("ts", event_dict.pop("timestamp", None)),
                ("lvl", event_dict.pop("level", None)),
                ("msg", event_dict.pop("event", None)),
            ]
            + sorted(event_dict.items())
        ),
        structlog.processors.JSONRenderer(sort_keys=False),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Silence third-party library loggers
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
warnings.filterwarnings('ignore')

benchmark_duration = 1  # Time to run each benchmark in seconds


# Using requests library
def benchmark_requests() -> tuple[int, float]:
    start_time = time.perf_counter()
    count = 0
    while time.perf_counter() - start_time < benchmark_duration:
        response = requests.get(settings.test_url)
        response.raise_for_status()  # Ensure no failures
        count += 1
    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Using urllib3 library
def benchmark_urllib3() -> tuple[int, float]:
    http = PoolManager()
    start_time = time.perf_counter()
    count = 0
    while time.perf_counter() - start_time < benchmark_duration:
        response = http.request("GET", settings.test_url)
        if response.status != 200:
            raise ValueError("Request failed")
        count += 1
    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Using http.client with proper resource cleanup and error handling
def benchmark_http_client() -> tuple[int, float]:
    start_time = time.perf_counter()
    count = 0
    while time.perf_counter() - start_time < benchmark_duration:
        conn = http.client.HTTPConnection(settings.host, settings.port)
        try:
            conn.request("GET", "/")
            response = conn.getresponse()
            if response.status != 200:
                raise ValueError(f"Request failed with status code: {response.status}")
            count += 1
        except Exception as e:
            logger.error("Request failed with error", error=str(e))
        finally:
            # Ensure the connection is closed properly
            conn.close()
    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Using aiohttp (asynchronous)
async def benchmark_aiohttp() -> tuple[int, float]:
    async with aiohttp.ClientSession() as session:
        start_time = time.perf_counter()
        count = 0
        while time.perf_counter() - start_time < benchmark_duration:
            async with session.get(settings.test_url) as response:
                if response.status != 200:
                    raise ValueError("Request failed")
                count += 1
        elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Using httpx (asynchronous)
async def benchmark_httpx_async() -> tuple[int, float]:
    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        count = 0
        while time.perf_counter() - start_time < benchmark_duration:
            response = await client.get(settings.test_url)
            if response.status_code != 200:
                raise ValueError("Request failed")
            count += 1
        elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Using httpx (synchronous)
def benchmark_httpx_sync() -> tuple[int, float]:
    client = httpx.Client()
    start_time = time.perf_counter()
    count = 0
    while time.perf_counter() - start_time < benchmark_duration:
        response = client.get(settings.test_url)
        if response.status_code != 200:
            raise ValueError("Request failed")
        count += 1
    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


def benchmark_fiberhttp() -> tuple[int, float]:
    client = fiberhttp.Client(timeout=2)  # Increased timeout
    request = fiberhttp.Request("GET", settings.test_url)  # Reuse the request object
    start_time = time.perf_counter()
    count = 0

    try:
        while time.perf_counter() - start_time < benchmark_duration:
            try:
                response = client.send(request)
                if response.status_code() == 200:
                    count += 1
                else:
                    logger.error(
                        "Request failed with status code",
                        status_code=response.status_code(),
                    )
            except Exception as e:
                logger.error("Request failed with error", error=str(e))
    except Exception as e:
        logger.error("Error during benchmarking", error=str(e))
    finally:
        try:
            client.close()
        except Exception as close_error:
            logger.error("Error closing client", error=str(close_error))
    elapsed_time = time.perf_counter() - start_time
    return count, elapsed_time


# Helper function to run benchmark and print results
def run_benchmark(
    name: str,
    benchmark_function: Callable[[], Tuple[int, float]],
    is_async: bool = False,
):
    logger.info(
        event="start-benchmark",
        library=name,
        is_async=is_async,
    )
    if is_async:
        count, elapsed_time = asyncio.run(benchmark_function())
    else:
        count, elapsed_time = benchmark_function()

    logger.info(
        event="end-benchmark",
        library=name,
        count=count,
        elapsed_time=elapsed_time,
    )


if __name__ == "__main__":
    # Run benchmarks with reduced code duplication
    benchmarks = [
        ("fiberhttp", benchmark_fiberhttp, False),
        ("requests", benchmark_requests, False),
        ("urllib3", benchmark_urllib3, False),
        ("http.client", benchmark_http_client, False),
        ("aiohttp", benchmark_aiohttp, True),
        ("httpx (async)", benchmark_httpx_async, True),
        ("httpx (sync)", benchmark_httpx_sync, False),
    ]

    for name, benchmark_function, is_async in benchmarks:
        run_benchmark(name, benchmark_function, is_async)