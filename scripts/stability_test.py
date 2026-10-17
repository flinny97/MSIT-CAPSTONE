"""
Stability test: many participants finish both tests at the same time.

Start the app first (python app.py), then run:

    python scripts/stability_test.py

Each round sends 20 synthetic participants through consent, both tests, and
feedback at the same moment. It reports any server errors and checks that the
database saved exactly what was sent. Use a fresh database for this test.
"""

import json
import os
import sqlite3
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
DB = os.environ.get("CAPSTONE_DB_PATH", str(Path(__file__).resolve().parent.parent / "instance" / "capstone.db"))
ROUNDS, AT_ONCE = 3, 20


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as err:
        return err.code


def answer_key():
    key = {}
    with sqlite3.connect(DB) as conn:
        for test, item, answer in conn.execute("SELECT test, item_id, answer FROM questions"):
            key.setdefault(test, {})[item] = answer
    return key


def participant(number, key):
    pid = f"P{number:02d}"
    codes = [call("POST", "/api/participants", {"participant_id": pid, "consent": True})]
    for test in ("pre", "post"):
        codes.append(call("POST", f"/api/tests/{test}/start", {"participant_id": pid}))
        codes.append(call("GET", f"/api/tests/{test}/questions"))
        answers = {item: {"choice": right, "confidence": 4} for item, right in key[test].items()}
        codes.append(call("POST", f"/api/tests/{test}/submit", {"participant_id": pid, "answers": answers}))
    codes.append(call("POST", "/api/feedback", {"participant_id": pid, "ease_rating": 4}))
    return codes


def main():
    key = answer_key()
    total_errors = 0
    for rnd in range(1, ROUNDS + 1):
        numbers = range((rnd - 1) * AT_ONCE + 1, rnd * AT_ONCE + 1)
        with ThreadPoolExecutor(max_workers=AT_ONCE) as pool:
            codes = [c for result in pool.map(lambda n: participant(n, key), numbers) for c in result]
        errors = sum(1 for c in codes if c >= 500)
        total_errors += errors
        print(f"Round {rnd}: {AT_ONCE} participants at the same time, {len(codes)} requests, {errors} server errors")
    with sqlite3.connect(DB) as conn:
        finished = conn.execute("SELECT COUNT(*) FROM attempts WHERE status = 'completed'").fetchone()[0]
        answers = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
    expected = ROUNDS * AT_ONCE
    print(f"Database check: {finished} finished tests (expected {expected * 2}), "
          f"{answers} saved answers (expected {expected * 20})")
    print("Result:", "PASS" if total_errors == 0 and finished == expected * 2 and answers == expected * 20 else "FAIL")


if __name__ == "__main__":
    main()
