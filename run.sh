#!/usr/bin/env bash

# order reflects the table in README.md
uv run benchmark/fiberhttp_benchmark.py
uv run benchmark/http-client_benchmark.py
uv run benchmark/aiohttp_benchmark.py
uv run benchmark/urllib3_benchmark.py
uv run benchmark/httpx_benchmark.py
uv run benchmark/httpx-async_benchmark.py
uv run benchmark/requests_benchmark.py
