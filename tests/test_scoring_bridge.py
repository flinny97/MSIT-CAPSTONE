"""
Tests for scoring_bridge.py, the part that turns multiple choice answers into
the format the Unit 5 scoring module expects.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp import scoring_bridge  # noqa: E402

QUESTIONS = [
    {"item_id": "Q1", "indicator": "suspicious_sender", "type": "Recognition"},
    {"item_id": "Q4", "indicator": "unexpected_attachment", "type": "Response"},
    {"item_id": "Q7", "indicator": "none", "type": "Legitimate"},
]


def row(pid, item, correct):
    return {"participant_id": pid, "item_id": item, "is_correct": int(correct)}


def test_items_get_the_right_kind_and_phishing_flag():
    items = {i["item_id"]: i for i in scoring_bridge.to_scoring_items(QUESTIONS)}
    assert items["Q1"]["kind"] == "knowledge" and items["Q1"]["is_phishing"]
    assert items["Q4"]["kind"] == "scenario"
    assert items["Q7"]["is_phishing"] is False


def test_wrong_answer_on_legitimate_email_is_a_false_alarm():
    item = {"item_id": "Q7", "is_phishing": False}
    assert scoring_bridge.to_scoring_response(row("P01", "Q7", False), item)["classified_as_phishing"] is True
    assert scoring_bridge.to_scoring_response(row("P01", "Q7", True), item)["classified_as_phishing"] is False


def test_summary_matches_hand_count():
    # P01: 1 of 3 right before, 3 of 3 after. Scores are out of all 3 questions.
    pre = [row("P01", "Q1", True), row("P01", "Q4", False), row("P01", "Q7", False)]
    post = [row("P01", "Q1", True), row("P01", "Q4", True), row("P01", "Q7", True)]
    summary = scoring_bridge.summarise_from_rows(QUESTIONS, pre, post)
    assert summary["average_score"] == {"pre": 33.33, "post": 100.0, "improvement": 66.67}
    assert summary["false_alarm_rate"] == {"pre": 100.0, "post": 0.0}
    assert summary["correct_response_rate"] == {"pre": 0.0, "post": 100.0, "improvement": 100.0}
