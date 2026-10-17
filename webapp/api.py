# API layer
# The web pages never connect to the database directly. They send requests to
# these routes, which check the input, read or write the database, and send the
# answer back as JSON. The results route sends the answers to the scoring module.

import json
import statistics
import sys
from pathlib import Path

from flask import Blueprint, jsonify, request

from .db import get_db, now
from .scoring_bridge import summarise_from_rows

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from scoring import validation  # noqa: E402

api = Blueprint("api", __name__, url_prefix="/api")
TESTS = ("pre", "post")


def error(message, status=400, **extra):
    # Send an error message back to the page, plus any extra details (like missing questions)
    return jsonify({"error": message, **extra}), status


def is_rating(value):
    # A rating has to be a whole number from 1 to 5. True and False are refused because
    # Python would otherwise treat True as 1 and save it (found in Unit 7 testing).
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5


def participant_exists(pid):
    # Check if the participant ID is already saved
    row = get_db().execute("SELECT 1 FROM participants WHERE participant_id = ?", (pid,)).fetchone()
    return row is not None


def attempt_status(pid, test):
    # Get the status of one test (started or completed) for a participant
    query = "SELECT status FROM attempts WHERE participant_id = ? AND test = ?"
    row = get_db().execute(query, (pid, test)).fetchone()
    return row["status"] if row else None


@api.post("/participants")
def register_participant():
    # Get the participant ID and check the consent
    data = request.get_json(silent=True) or {}
    pid = validation.normalize_id(data.get("participant_id", ""))

    # Make sure the participant agrees before starting
    if data.get("consent") is not True:
        return error("Consent is required before starting.")

    # Check if the participant ID is valid
    if not validation.PARTICIPANT_ID_PATTERN.fullmatch(pid):
        return error("Invalid participant ID. Please use an ID like P01.")

    # Save the participant ID into the database
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO participants VALUES (?, ?)",
        (pid, now())
    )
    db.commit()
    return jsonify({"participant_id": pid}), 201


@api.get("/tests/<test>/questions")
def get_questions(test):
    # Only the pre and post tests exist
    if test not in TESTS:
        return error("Unknown test.", 404)

    # Get the questions for this test. The correct answers are never sent to the page.
    rows = get_db().execute(
        "SELECT item_id, number, prompt, options, image, caption FROM questions "
        "WHERE test = ? ORDER BY number",
        (test,)
    ).fetchall()

    questions = []
    for r in rows:
        questions.append({
            "item_id": r["item_id"],
            "number": r["number"],
            "prompt": r["prompt"],
            "options": json.loads(r["options"]),
            "image": f"/screenshots/{r['image']}" if r["image"] else None,
            "caption": r["caption"],
        })
    return jsonify(questions)


@api.post("/tests/<test>/start")
def start_test(test):
    # Get the participant ID
    data = request.get_json(silent=True) or {}
    pid = validation.normalize_id(data.get("participant_id", ""))

    # Check the test name and make sure the participant gave consent
    if test not in TESTS:
        return error("Unknown test.", 404)
    if not participant_exists(pid):
        return error("Give consent before starting a test.", 403)

    # The post-assessment can only start after the pre-assessment is finished
    if test == "post" and attempt_status(pid, "pre") != "completed":
        return error("The pre-assessment has to be finished first.", 409)

    # A test can only be taken once
    if attempt_status(pid, test) == "completed":
        return error("This test was already submitted.", 409)

    # Save that the test was started so unfinished tests can be found later
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO attempts VALUES (?, ?, 'started', ?, NULL)",
        (pid, test, now())
    )
    db.commit()
    return jsonify({"participant_id": pid, "test": test, "status": "started"})


@api.post("/tests/<test>/submit")
def submit_test(test):
    # Get the participant ID and the answers from the page
    data = request.get_json(silent=True) or {}
    pid = validation.normalize_id(data.get("participant_id", ""))
    answers = data.get("answers") or {}

    # The test has to be started first and can only be submitted once
    if test not in TESTS:
        return error("Unknown test.", 404)
    if attempt_status(pid, test) != "started":
        return error("Start the test before submitting it, and submit it only once.", 409)

    # The answers have to come in as one entry per question. Anything else is refused
    # with a clear message instead of crashing the server (found in Unit 7 testing).
    if not isinstance(answers, dict):
        return error("The answers were not sent in the right format. Please submit the test again.")

    # Get the correct answer for each question
    db = get_db()
    key = {}
    for r in db.execute("SELECT item_id, answer FROM questions WHERE test = ?", (test,)):
        key[r["item_id"]] = r["answer"]

    # Every question needs an answer (a to d) and a confidence rating (1 to 5).
    # If anything is missing, nothing is saved and the test stays "started".
    missing = []
    for item in key:
        answer = answers.get(item)
        if not isinstance(answer, dict):
            missing.append(item)
            continue
        no_choice = answer.get("choice") not in ("a", "b", "c", "d")
        no_rating = not is_rating(answer.get("confidence"))
        if no_choice or no_rating:
            missing.append(item)
    if missing:
        # The list of missing questions is also sent on its own so the page can highlight them
        missing.sort(key=lambda item: int(item[1:]))
        return error("Answer every question and rate how sure you are. Missing: " + ", ".join(missing),
                     missing=missing)

    # Save every answer and mark the test as completed
    rows = []
    for item in key:
        choice = answers[item]["choice"]
        is_correct = int(choice == key[item])
        rows.append((pid, test, item, choice, answers[item]["confidence"], is_correct))
    db.executemany("INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?)", rows)
    db.execute(
        "UPDATE attempts SET status = 'completed', completed_at = ? WHERE participant_id = ? AND test = ?",
        (now(), pid, test)
    )
    db.commit()

    # Send the score back to the page
    correct = sum(r[5] for r in rows)
    score = round(100.0 * correct / len(rows), 2)
    return jsonify({"participant_id": pid, "test": test, "correct": correct, "total": len(rows), "score": score})


@api.post("/feedback")
def submit_feedback():
    # Get the participant ID, the ease rating, and the comment
    data = request.get_json(silent=True) or {}
    pid = validation.normalize_id(data.get("participant_id", ""))
    rating = data.get("ease_rating")
    comment = (data.get("comment") or "").strip()[:1000]

    # Feedback is only collected after the post-assessment
    if attempt_status(pid, "post") != "completed":
        return error("Feedback is collected after the post-assessment.", 409)
    if not is_rating(rating):
        return error("Choose an ease rating from 1 to 5.")

    # Save the feedback into the database
    db = get_db()
    db.execute(
        "INSERT OR REPLACE INTO feedback VALUES (?, ?, ?, ?)",
        (pid, rating, comment, now())
    )
    db.commit()
    return jsonify({"saved": True}), 201


def average_confidence(rows):
    # Average of the 1 to 5 confidence ratings, or None if there are no answers yet
    if not rows:
        return None
    return round(statistics.mean(r["confidence"] for r in rows), 2)


@api.get("/results/summary")
def results_summary():
    # Researcher view: send every completed test to the scoring module (M4)
    db = get_db()
    questions = [dict(r) for r in db.execute("SELECT * FROM questions")]

    # Only use answers from tests that were completed
    completed_answers = (
        "SELECT r.* FROM responses r JOIN attempts a "
        "ON a.participant_id = r.participant_id AND a.test = r.test "
        "WHERE a.status = 'completed' AND r.test = ?"
    )
    pre_rows = [dict(r) for r in db.execute(completed_answers, ("pre",))]
    post_rows = [dict(r) for r in db.execute(completed_answers, ("post",))]
    summary = summarise_from_rows(questions, pre_rows, post_rows)

    # List the tests that were started but never submitted
    summary["incomplete_attempts"] = [dict(r) for r in db.execute(
        "SELECT participant_id, test, started_at FROM attempts "
        "WHERE status = 'started' ORDER BY participant_id, test"
    )]

    # Average confidence before and after the training
    summary["confidence"] = {"pre": average_confidence(pre_rows), "post": average_confidence(post_rows)}

    # Usability results from the feedback form
    ratings = [r["ease_rating"] for r in db.execute("SELECT ease_rating FROM feedback")]
    comments = [r["comment"] for r in db.execute(
        "SELECT comment FROM feedback WHERE comment <> '' ORDER BY submitted_at"
    )]
    summary["usability"] = {
        "responses": len(ratings),
        "average_ease_rating": round(statistics.mean(ratings), 2) if ratings else None,
        "comments": comments,
    }
    return jsonify(summary)


@api.get("/metrics/performance")
def performance():
    # Response time for each API route, taken from the request log
    rows = get_db().execute("SELECT method, path, duration_ms FROM request_log").fetchall()

    # Group the times by route, for example "POST /api/feedback"
    grouped = {}
    for r in rows:
        route = f"{r['method']} {r['path']}"
        grouped.setdefault(route, []).append(r["duration_ms"])

    # Work out the average and the 95th percentile for each route
    report = []
    for route, times in sorted(grouped.items()):
        times.sort()
        p95 = times[min(len(times) - 1, int(round(0.95 * (len(times) - 1))))]
        report.append({
            "route": route,
            "requests": len(times),
            "average_ms": round(statistics.mean(times), 2),
            "p95_ms": round(p95, 2),
        })
    return jsonify(report)
