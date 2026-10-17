"""
Integration tests for Unit 7.

These check that the API, the database, and the scoring module still work
together when the input is unusual or when the app is restarted. Each test uses
its own empty database in a temporary folder.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp import create_app  # noqa: E402
from webapp.db import get_db  # noqa: E402


def make_app(db_path):
    return create_app({"DATABASE": str(db_path), "SCREENSHOT_DIR": str(db_path.parent)})


@pytest.fixture
def client(tmp_path):
    return make_app(tmp_path / "test.db").test_client()


def answer_key(client, test):
    with client.application.app_context():
        return {r["item_id"]: r["answer"] for r in get_db().execute(
            "SELECT item_id, answer FROM questions WHERE test = ?", (test,))}


def full_answers(client, test, confidence=4):
    return {item: {"choice": right, "confidence": confidence} for item, right in answer_key(client, test).items()}


def join_and_start(client, pid="P01", test="pre"):
    client.post("/api/participants", json={"participant_id": pid, "consent": True})
    client.post(f"/api/tests/{test}/start", json={"participant_id": pid})


def submit(client, answers, pid="P01", test="pre"):
    return client.post(f"/api/tests/{test}/submit", json={"participant_id": pid, "answers": answers})


# --- bad input is refused with a clear message instead of crashing ----------

def test_answers_sent_as_a_list_get_a_clear_error_not_a_crash(client):
    join_and_start(client)
    response = submit(client, ["a"] * 10)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_an_answer_sent_as_plain_text_gets_a_clear_error_not_a_crash(client):
    join_and_start(client)
    answers = full_answers(client, "pre")
    answers["Q1"] = "b"
    response = submit(client, answers)
    assert response.status_code == 400
    assert response.get_json()["missing"] == ["Q1"]


def test_true_is_not_saved_as_a_confidence_rating(client):
    join_and_start(client)
    response = submit(client, full_answers(client, "pre", confidence=True))
    assert response.status_code == 400
    with client.application.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM responses").fetchone()[0] == 0


def test_true_is_not_saved_as_an_ease_rating(client):
    join_and_start(client)
    submit(client, full_answers(client, "pre"))
    join_and_start(client, test="post")
    submit(client, full_answers(client, "post"), test="post")
    response = client.post("/api/feedback", json={"participant_id": "P01", "ease_rating": True})
    assert response.status_code == 400


def test_missing_questions_are_sent_back_as_a_list_for_the_page(client):
    join_and_start(client)
    answers = full_answers(client, "pre")
    del answers["Q3"]
    answers["Q10"]["confidence"] = None
    response = submit(client, answers)
    assert response.status_code == 400
    assert response.get_json()["missing"] == ["Q3", "Q10"]


# --- the saved data matches what the participant was shown ------------------

def test_saved_answers_match_the_score_shown_to_the_participant(client):
    join_and_start(client)
    key = answer_key(client, "pre")
    answers = full_answers(client, "pre")
    for item in ("Q2", "Q5", "Q8"):
        answers[item]["choice"] = next(x for x in "abcd" if x != key[item])
    shown = submit(client, answers).get_json()
    with client.application.app_context():
        saved = get_db().execute("SELECT SUM(is_correct), COUNT(*) FROM responses").fetchone()
    assert shown["correct"] == saved[0] == 7
    assert saved[1] == 10


def test_data_is_still_there_after_the_app_restarts(tmp_path):
    db_path = tmp_path / "restart.db"
    first = make_app(db_path).test_client()
    join_and_start(first)
    submit(first, full_answers(first, "pre"))

    # A new app instance on the same file, like restarting the server
    second = make_app(db_path).test_client()
    response = second.post("/api/tests/pre/start", json={"participant_id": "P01"})
    assert response.status_code == 409          # the finished pre-assessment was remembered
    assert second.post("/api/tests/post/start", json={"participant_id": "P01"}).status_code == 200


def test_results_are_the_same_every_time_they_are_requested(client):
    for pid in ("P01", "P02"):
        join_and_start(client, pid)
        submit(client, full_answers(client, "pre"), pid)
        join_and_start(client, pid, "post")
        submit(client, full_answers(client, "post"), pid, "post")
    first = client.get("/api/results/summary").get_json()
    second = client.get("/api/results/summary").get_json()
    assert first == second
