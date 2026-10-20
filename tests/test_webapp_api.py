"""
Tests for the integrated web app: pages -> API -> database -> scoring.

Each test gets its own empty database in a temporary folder, so the tests never
touch the real data file.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp import create_app  # noqa: E402
from webapp.db import get_db  # noqa: E402


@pytest.fixture
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "SCREENSHOT_DIR": str(tmp_path)})
    return app.test_client()


def answer_key(client, test):
    with client.application.app_context():
        return {r["item_id"]: r["answer"] for r in get_db().execute(
            "SELECT item_id, answer FROM questions WHERE test = ?", (test,))}


def all_answers(client, test, number_right=10):
    """Answers for every question. The first 'number_right' are correct."""
    key = answer_key(client, test)
    answers = {}
    for i in range(1, 11):
        item = f"Q{i}"
        wrong = next(x for x in "abcd" if x != key[item])
        answers[item] = {"choice": key[item] if i <= number_right else wrong, "confidence": 3}
    return answers


def join(client, pid="P01"):
    return client.post("/api/participants", json={"participant_id": pid, "consent": True})


def finish(client, test, pid="P01", number_right=10):
    client.post(f"/api/tests/{test}/start", json={"participant_id": pid})
    return client.post(f"/api/tests/{test}/submit",
                       json={"participant_id": pid, "answers": all_answers(client, test, number_right)})


# --- consent and privacy ---------------------------------------------------

def test_valid_participant_is_registered(client):
    response = join(client, " p01 ")
    assert response.status_code == 201
    assert response.get_json()["participant_id"] == "P01"


def test_email_in_id_box_is_refused(client):
    response = client.post("/api/participants", json={"participant_id": "jane@company.com", "consent": True})
    assert response.status_code == 400
    assert "Invalid participant ID" in response.get_json()["error"]


def test_no_consent_no_registration(client):
    response = client.post("/api/participants", json={"participant_id": "P01", "consent": False})
    assert response.status_code == 400


# --- questions -------------------------------------------------------------

def test_question_bank_loaded_from_packet(client):
    for test in ("pre", "post"):
        questions = client.get(f"/api/tests/{test}/questions").get_json()
        assert [q["number"] for q in questions] == list(range(1, 11))
        assert sum(1 for q in questions if q["image"]) == 3


def test_correct_answers_are_never_sent_to_the_browser(client):
    questions = client.get("/api/tests/pre/questions").get_json()
    assert all("answer" not in q for q in questions)


# --- test flow and the incomplete-assessment rule --------------------------

def test_full_test_is_scored(client):
    join(client)
    result = finish(client, "pre", number_right=7).get_json()
    assert result["correct"] == 7 and result["score"] == 70.0


def test_missing_answer_is_rejected_and_nothing_is_saved(client):
    join(client)
    client.post("/api/tests/pre/start", json={"participant_id": "P01"})
    answers = all_answers(client, "pre")
    del answers["Q4"]
    answers["Q9"]["confidence"] = None
    response = client.post("/api/tests/pre/submit", json={"participant_id": "P01", "answers": answers})
    assert response.status_code == 400
    assert "Q4, Q9" in response.get_json()["error"]
    with client.application.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM responses").fetchone()[0] == 0


def test_post_test_needs_finished_pre_test(client):
    join(client)
    response = client.post("/api/tests/post/start", json={"participant_id": "P01"})
    assert response.status_code == 409


def test_test_cannot_be_submitted_twice(client):
    join(client)
    finish(client, "pre")
    response = client.post("/api/tests/pre/submit", json={"participant_id": "P01", "answers": all_answers(client, "pre")})
    assert response.status_code == 409


def test_unregistered_participant_cannot_start(client):
    response = client.post("/api/tests/pre/start", json={"participant_id": "P99"})
    assert response.status_code == 403


# --- results: database -> scoring module -----------------------------------

def test_summary_uses_scoring_module_and_leaves_out_incomplete(client):
    for pid, pre_right, post_right in (("P01", 4, 9), ("P02", 6, 10)):
        join(client, pid)
        finish(client, "pre", pid, pre_right)
        finish(client, "post", pid, post_right)
    join(client, "P03")
    finish(client, "pre", "P03", 2)                                   # never took the post test
    client.post("/api/tests/post/start", json={"participant_id": "P03"})   # started but did not submit

    summary = client.get("/api/results/summary").get_json()
    assert summary["participants"] == 2
    assert summary["excluded_unmatched"] == ["P03"]
    assert summary["average_score"] == {"pre": 50.0, "post": 95.0, "improvement": 45.0}
    assert summary["mastery_rate_post"] == 100.0
    assert {"participant_id": "P03", "test": "post"} in [
        {k: a[k] for k in ("participant_id", "test")} for a in summary["incomplete_attempts"]]


def test_feedback_only_after_post_test(client):
    join(client)
    finish(client, "pre")
    assert client.post("/api/feedback", json={"participant_id": "P01", "ease_rating": 4}).status_code == 409
    finish(client, "post")
    assert client.post("/api/feedback", json={"participant_id": "P01", "ease_rating": 4}).status_code == 201
    assert client.get("/api/results/summary").get_json()["usability"]["average_ease_rating"] == 4


def test_api_response_times_are_logged(client):
    client.get("/api/tests/pre/questions")
    client.get("/api/tests/post/questions")
    report = client.get("/api/metrics/performance").get_json()
    row = next(r for r in report if r["route"] == "GET /api/tests/<test>/questions")
    assert row["requests"] == 2 and row["average_ms"] >= 0


# --- pages -----------------------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/test/pre", "/test/post", "/training", "/feedback", "/admin"])
def test_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_training_page_shows_the_lesson(client):
    page = client.get("/training").get_data(as_text=True)
    assert "Part 1: Check Who Really Sent It" in page
    assert "Stop, Verify, Report" in page
