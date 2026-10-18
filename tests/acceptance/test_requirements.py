"""
Acceptance tests for Unit 7.

Each test checks one requirement from the Unit 3 design (FR = functional,
NFR = non-functional). FR2, FR4, and FR5 are checked in their revised Unit 6
form (see "Requirement revisions" in docs/unit3-requirements-and-design.md). Together with the manual walkthrough in
docs/unit7-acceptance-checklist.md, they show whether the system is ready for
the pilot. Only synthetic participant IDs are used.
"""

import re
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from webapp import create_app  # noqa: E402
from webapp.db import get_db  # noqa: E402

FIVE_INDICATORS = {"suspicious_sender", "misleading_link", "urgent_language",
                   "credential_request", "unexpected_attachment"}


@pytest.fixture
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "acceptance.db"), "SCREENSHOT_DIR": str(tmp_path)})
    return app.test_client()


def key(client, test):
    with client.application.app_context():
        return {r["item_id"]: r["answer"] for r in get_db().execute(
            "SELECT item_id, answer FROM questions WHERE test = ?", (test,))}


def complete(client, pid, test, number_right):
    answers = {}
    for n, (item, right) in enumerate(sorted(key(client, test).items(), key=lambda x: int(x[0][1:])), start=1):
        wrong = next(x for x in "abcd" if x != right)
        answers[item] = {"choice": right if n <= number_right else wrong, "confidence": 3}
    client.post(f"/api/tests/{test}/start", json={"participant_id": pid})
    return client.post(f"/api/tests/{test}/submit", json={"participant_id": pid, "answers": answers})


def test_FR1_consent_is_recorded_before_any_test_can_start(client):
    assert client.post("/api/tests/pre/start", json={"participant_id": "P01"}).status_code == 403
    assert client.post("/api/participants", json={"participant_id": "P01", "consent": False}).status_code == 400
    assert client.post("/api/participants", json={"participant_id": "P01", "consent": True}).status_code == 201
    with client.application.app_context():
        row = get_db().execute("SELECT consented_at FROM participants WHERE participant_id = 'P01'").fetchone()
    assert row["consented_at"]
    assert client.post("/api/tests/pre/start", json={"participant_id": "P01"}).status_code == 200


def test_FR2_and_FR4_matched_pre_and_post_assessments(client):
    pre = client.get("/api/tests/pre/questions").get_json()
    post = client.get("/api/tests/post/questions").get_json()
    assert len(pre) == len(post) == 10
    assert [q["item_id"] for q in pre] == [q["item_id"] for q in post]
    assert all(len(q["options"]) == 4 for q in pre + post)


def test_FR3_training_lesson_covers_the_five_warning_signs_and_reporting(client):
    page = client.get("/training").get_data(as_text=True)
    for heading in ("Part 1: Check Who Really Sent It", "Part 2:", "URGENCY",
                    "Part 3: Check the Link", "Part 4: Never Share Passwords",
                    "Part 5: Be Careful With Unexpected Attachments", "Stop, Verify, Report"):
        assert heading in page


def test_FR5_every_answer_and_confidence_rating_is_recorded(client):
    client.post("/api/participants", json={"participant_id": "P01", "consent": True})
    complete(client, "P01", "pre", 6)
    with client.application.app_context():
        rows = get_db().execute("SELECT choice, confidence FROM responses WHERE participant_id = 'P01'").fetchall()
    assert len(rows) == 10
    assert all(r["choice"] in "abcd" and 1 <= r["confidence"] <= 5 for r in rows)


def test_FR6_responses_are_keyed_by_id_and_names_or_emails_are_refused(client, tmp_path):
    for bad in ("jane.doe@company.com", "Jane Doe", "12345"):
        assert client.post("/api/participants", json={"participant_id": bad, "consent": True}).status_code == 400
    client.post("/api/participants", json={"participant_id": "P01", "consent": True})
    columns = set()
    with sqlite3.connect(tmp_path / "acceptance.db") as conn:
        for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            columns |= {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    assert not columns & {"name", "full_name", "first_name", "last_name", "email"}


def test_FR7_metrics_are_calculated_and_compared_to_the_success_criteria(client):
    for pid, pre, post in (("P01", 4, 9), ("P02", 5, 10), ("P03", 6, 8)):
        client.post("/api/participants", json={"participant_id": pid, "consent": True})
        complete(client, pid, "pre", pre)
        complete(client, pid, "post", post)
    s = client.get("/api/results/summary").get_json()
    assert s["average_score"] == {"pre": 50.0, "post": 90.0, "improvement": 40.0}
    for metric in ("mastery_rate_post", "correct_response_rate", "per_indicator_accuracy", "false_alarm_rate"):
        assert metric in s
    assert s["success_criteria"]["goal_3_score_improvement_20pp"] is True
    assert s["success_criteria"]["goal_4_mastery_80pct_at_80"] is True


def test_FR8_results_are_reported_for_each_warning_sign(client):
    client.post("/api/participants", json={"participant_id": "P01", "consent": True})
    complete(client, "P01", "pre", 5)
    complete(client, "P01", "post", 10)
    s = client.get("/api/results/summary").get_json()
    assert set(s["per_indicator_accuracy"]["post"]) == FIVE_INDICATORS
    assert client.get("/admin").status_code == 200


def test_NFR4_the_same_answers_always_give_the_same_results(tmp_path):
    results = []
    for run in (1, 2):
        app = create_app({"DATABASE": str(tmp_path / f"run{run}.db"), "SCREENSHOT_DIR": str(tmp_path)})
        client = app.test_client()
        client.post("/api/participants", json={"participant_id": "P01", "consent": True})
        complete(client, "P01", "pre", 3)
        complete(client, "P01", "post", 9)
        summary = client.get("/api/results/summary").get_json()
        summary.pop("incomplete_attempts", None)
        results.append(summary)
    assert results[0] == results[1]


def test_NFR5_no_question_contains_a_working_link(client):
    for test in ("pre", "post"):
        for q in client.get(f"/api/tests/{test}/questions").get_json():
            text = q["prompt"] + " ".join(q["options"].values()) + (q["caption"] or "")
            assert not re.search(r"<a\s|href=", text, re.IGNORECASE)
