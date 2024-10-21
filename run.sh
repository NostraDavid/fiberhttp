#!/usr/bin/env bash

uv run aiohttp_benchmark.py
uv run fiberhttp_benchmark.py  
uv run http-client_benchmark.py 
uv run httpx_benchmark.py 
uv run httpx-async_benchmark.py 
