# Database layer (M3)
# SQLite stores the participants, their answers, the questions, and a log of how
# long each API request took. Participants are saved by ID only. No names or
# email addresses are saved, which follows the FR6 privacy rule from Unit 3.

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app, g

# Tables for the participant data. Every table uses the participant ID.
# The questions and the request log are separate and have no participant data.
SCHEMA = """
CREATE TABLE IF NOT EXISTS participants (
    participant_id TEXT PRIMARY KEY,
    consented_at   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
    participant_id TEXT NOT NULL,
    test           TEXT NOT NULL,
    status         TEXT NOT NULL,
    started_at     TEXT NOT NULL,
    completed_at   TEXT,
    PRIMARY KEY (participant_id, test)
);
CREATE TABLE IF NOT EXISTS responses (
    participant_id TEXT NOT NULL,
    test           TEXT NOT NULL,
    item_id        TEXT NOT NULL,
    choice         TEXT NOT NULL,
    confidence     INTEGER NOT NULL,
    is_correct     INTEGER NOT NULL,
    PRIMARY KEY (participant_id, test, item_id)
);
CREATE TABLE IF NOT EXISTS feedback (
    participant_id TEXT PRIMARY KEY,
    ease_rating    INTEGER NOT NULL,
    comment        TEXT,
    submitted_at   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions (
    test      TEXT NOT NULL,
    item_id   TEXT NOT NULL,
    number    INTEGER NOT NULL,
    prompt    TEXT NOT NULL,
    options   TEXT NOT NULL,
    answer    TEXT NOT NULL,
    indicator TEXT NOT NULL,
    type      TEXT NOT NULL,
    image     TEXT,
    caption   TEXT,
    PRIMARY KEY (test, item_id)
);
CREATE TABLE IF NOT EXISTS request_log (
    path        TEXT NOT NULL,
    method      TEXT NOT NULL,
    status      INTEGER NOT NULL,
    duration_ms REAL NOT NULL,
    logged_at   TEXT NOT NULL
);
"""


def now():
    # Current time in UTC, for example 2026-10-14T18:30:00+00:00
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    # Open one database connection per request and reuse it for that request
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    # Close the connection when the request is finished
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(database, questions_file):
    # Create the database folder and the tables if they do not exist yet
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database)
    conn.executescript(SCHEMA)

    # Load the questions from questions.json
    with open(questions_file, encoding="utf-8") as f:
        bank = json.load(f)["questions"]

    # Reload the questions every time the app starts so any change shows up.
    # Saved answers are not touched.
    conn.execute("DELETE FROM questions")
    for q in bank:
        conn.execute(
            "INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (q["test"], q["item_id"], q["number"], q["prompt"], json.dumps(q["options"]),
             q["answer"], q["indicator"], q["type"], q["image"], q["caption"])
        )
    conn.commit()
    conn.close()
