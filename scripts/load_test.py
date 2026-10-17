"""
Load test: send many requests to the running app at the same time and report
how many it answers per second (throughput).

Start the app first (python app.py), then run:

    python scripts/load_test.py

Set BASE_URL to test another address, for example the hosted site.
"""

import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:5000")


def get(path):
    with urllib.request.urlopen(BASE + path) as response:
        return response.status


def run(path, total, workers=10):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        codes = list(pool.map(lambda _: get(path), range(total)))
    seconds = time.perf_counter() - start
    ok = sum(1 for code in codes if code == 200)
    print(f"{path}: {total} requests, {workers} at a time, {seconds:.2f} s, "
          f"{ok / seconds:.0f} requests per second, {ok}/{total} OK")


if __name__ == "__main__":
    run("/api/tests/pre/questions", 1000)
    run("/api/results/summary", 300)
