"""Tests for the evaluation metrics."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoring import metrics  # noqa: E402


ITEMS = [
    {"item_id": "K1", "indicator": "suspicious_sender", "kind": "knowledge", "is_phishing": True},
    {"item_id": "K2", "indicator": "misleading_link", "kind": "knowledge", "is_phishing": True},
    {"item_id": "S1", "indicator": "credential_request", "kind": "scenario", "is_phishing": True},
    {"item_id": "S2", "indicator": "none", "kind": "scenario", "is_phishing": False},
]


def response(pid, item_id, classified, action="report"):
    return {"participant_id": pid, "item_id": item_id,
            "classified_as_phishing": classified, "action": action}


def test_perfect_participant_scores_100():
    responses = [
        response("P01", "K1", True), response("P01", "K2", True),
        response("P01", "S1", True, "report"), response("P01", "S2", False, "open"),
    ]
    assert metrics.average_score(responses, ITEMS) == 100.0


def test_all_wrong_scores_zero():
    responses = [
        response("P01", "K1", False), response("P01", "K2", False),
        response("P01", "S1", False, "open"), response("P01", "S2", True, "report"),
    ]
    assert metrics.average_score(responses, ITEMS) == 0.0


def test_score_improvement_is_percentage_points():
    pre = [response("P01", "K1", False), response("P01", "K2", True)]
    post = [response("P01", "K1", True), response("P01", "K2", True)]
    assert metrics.score_improvement(pre, post, ITEMS) == 50.0


def test_mastery_rate_counts_participants_at_threshold():
    responses = [
        # P01 gets 4 of 4
        response("P01", "K1", True), response("P01", "K2", True),
        response("P01", "S1", True), response("P01", "S2", False, "open"),
        # P02 gets 2 of 4
        response("P02", "K1", True), response("P02", "K2", True),
        response("P02", "S1", False, "open"), response("P02", "S2", True),
    ]
    assert metrics.mastery_rate(responses, ITEMS) == 50.0


def test_correct_response_rate_only_counts_scenario_items():
    responses = [
        response("P01", "K1", False, "open"),      # knowledge item, ignored
        response("P01", "S1", True, "report"),     # safe
        response("P01", "S2", False, "open"),      # safe, legitimate mail opened
    ]
    assert metrics.correct_response_rate(responses, ITEMS) == 100.0


def test_recognising_phishing_but_opening_it_is_not_a_safe_action():
    responses = [response("P01", "S1", True, "open")]
    assert metrics.correct_response_rate(responses, ITEMS) == 0.0


def test_reporting_legitimate_mail_is_not_a_safe_action():
    responses = [response("P01", "S2", False, "report")]
    assert metrics.correct_response_rate(responses, ITEMS) == 0.0


def test_false_alarm_rate_uses_legitimate_items_only():
    responses = [
        response("P01", "S2", True),    # false alarm
        response("P02", "S2", False),   # correct
        response("P03", "K1", False),   # phishing item, ignored here
    ]
    assert metrics.false_alarm_rate(responses, ITEMS) == 50.0


def test_per_indicator_accuracy_excludes_legitimate_items():
    responses = [
        response("P01", "K1", True), response("P01", "K2", False),
        response("P01", "S2", True),
    ]
    accuracy = metrics.per_indicator_accuracy(responses, ITEMS)
    assert accuracy["suspicious_sender"] == 100.0
    assert accuracy["misleading_link"] == 0.0
    assert "none" not in accuracy


def test_duplicate_item_ids_are_rejected():
    bad_items = ITEMS + [dict(ITEMS[0])]
    with pytest.raises(ValueError):
        metrics.average_score([], bad_items)


def test_empty_input_does_not_raise():
    assert metrics.average_score([], ITEMS) == 0.0
    assert metrics.mastery_rate([], ITEMS) == 0.0
    assert metrics.false_alarm_rate([], ITEMS) == 0.0


def test_summarise_reports_success_criteria():
    pre = [response(f"P{i:02d}", "K1", False) for i in range(10)]
    post = [response(f"P{i:02d}", "K1", True) for i in range(10)]
    summary = metrics.summarise(pre, post, ITEMS)
    assert summary["average_score"]["improvement"] == 100.0
    assert summary["success_criteria"]["goal_3_score_improvement_20pp"] is True
    assert summary["success_criteria"]["goal_4_mastery_80pct_at_80"] is True
