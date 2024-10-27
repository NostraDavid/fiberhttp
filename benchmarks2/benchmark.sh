#!/usr/bin/env bash

set -euo pipefail

# use `uv` and `jq` to run the benchmark and colorize the output; you'll need to `uv run server.py` in a separate terminal
# this command helps you to nicely visualize the output
uv run benchmark.py 2>&1 | jq -R -c 'fromjson?' --compact-output
