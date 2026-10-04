"""
Black-box tests for the scoring rules.

These tests only look at the inputs and outputs. Each one sets up a few answers,
runs the function, and checks the result against the answer I worked out by hand.
They do not depend on how the code is written inside the functions.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoring import metrics  # noqa: E402

# Five phishing questions, one for each indicator, so each wrong answer is 20 points.
FIVE_ITEMS = [
    {"item_id": "K1", "indicator": "suspicious_sender", "kind": "knowledge", "is_phishing": True},
    {"item_id": "K2", "indicator": "misleading_link", "kind": "knowledge", "is_phishing": True},
    {"item_id": "K3", "indicator": "urgent_language", "kind": "knowledge", "is_phishing": True},
    {"item_id": "K4", "indicator": "credential_request", "kind": "knowledge", "is_phishing": True},
    {"item_id": "K5", "indicator": "unexpected_attachment", "kind": "knowledge", "is_phishing": True},
]


def answers(pid, number_correct):
    """Participant gets the first `number_correct` questions right and the rest wrong."""
    rows = []
    for position, item in enumerate(FIVE_ITEMS):
        rows.append({
            "participant_id": pid,
            "item_id": item["item_id"],
            "classified_as_phishing": position < number_correct,
            "action": "report",
        })
    return rows


@pytest.mark.parametrize("correct_answers, expected_score", [
    (0, 0.0),      # no correct answers
    (1, 20.0),
    (2, 40.0),
    (3, 60.0),
    (4, 80.0),     # meets the 80% goal
    (5, 100.0),    # all answers correct
])
def test_average_score(correct_answers, expected_score):
    result = metrics.average_score(
        answers("P01", correct_answers),
        FIVE_ITEMS
    )
    assert result == expected_score


def test_score_of_exactly_80_counts_as_mastery():
    assert metrics.mastery_rate(answers("P01", 4), FIVE_ITEMS) == 100.0


def test_score_just_under_80_does_not_count_as_mastery():
    assert metrics.mastery_rate(answers("P01", 3), FIVE_ITEMS) == 0.0


def test_negative_improvement_is_reported_not_hidden():
    pre = answers("P01", 4)    # 80%
    post = answers("P01", 2)   # 40%
    assert metrics.score_improvement(pre, post, FIVE_ITEMS) == -40.0


def test_no_change_gives_zero_improvement():
    pre = answers("P01", 3)
    post = answers("P01", 3)
    assert metrics.score_improvement(pre, post, FIVE_ITEMS) == 0.0


def test_average_is_taken_across_participants():
    responses = answers("P01", 5) + answers("P02", 3)   # 100% and 60%
    assert metrics.average_score(responses, FIVE_ITEMS) == 80.0


def test_participant_who_skipped_the_post_test_does_not_change_improvement():
    # P01 and P02 complete both tests and each improve by 40 points.
    # P03 only completes the pre-test with a very low score.
    pre = answers("P01", 2) + answers("P02", 2) + answers("P03", 0)
    post = answers("P01", 4) + answers("P02", 4)
    summary = metrics.summarise(pre, post, FIVE_ITEMS)
    assert summary["average_score"]["improvement"] == 40.0


def test_duplicate_submission_is_not_counted_twice():
    # Someone submits the form twice. Only one answer per question should count.
    responses = answers("P01", 5) + answers("P01", 0)
    assert metrics.average_score(responses, FIVE_ITEMS) in (0.0, 100.0)


def test_participant_id_case_and_spaces_do_not_split_one_person_into_two():
    pre = answers("P01", 2)
    post = answers(" p01 ", 4)
    summary = metrics.summarise(pre, post, FIVE_ITEMS)
    assert summary["participants"] == 1
    assert summary["average_score"]["improvement"] == 40.0


def test_blank_answer_counts_as_incorrect():
    # P01 gets four questions right and leaves K5 blank.
    # The score is out of all five, so leaving one blank should not help.
    responses = [r for r in answers("P01", 5) if r["item_id"] != "K5"]
    assert metrics.average_score(responses, FIVE_ITEMS) == 80.0
