"""
White-box tests for the validation module.

I wrote these with validation.py open. Each test goes after one specific check
inside clean_responses() or one of the helper functions, so every rule gets
tested by itself.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoring import validation  # noqa: E402

ITEMS = [
    {"item_id": "K1", "indicator": "suspicious_sender", "kind": "knowledge", "is_phishing": True},
    {"item_id": "S6", "indicator": "none", "kind": "scenario", "is_phishing": False},
]


def row(pid="P01", item_id="K1", classified=True, action="report"):
    return {"participant_id": pid, "item_id": item_id,
            "classified_as_phishing": classified, "action": action}


def test_valid_row_passes_with_no_problems():
    clean, problems = validation.clean_responses([row()], ITEMS)
    assert len(clean) == 1
    assert problems == []


def test_participant_id_is_trimmed_and_upper_cased():
    clean, _ = validation.clean_responses([row(pid="  p07 ")], ITEMS)
    assert clean[0]["participant_id"] == "P07"


def test_name_in_participant_id_box_is_skipped():
    clean, problems = validation.clean_responses([row(pid="John Smith")], ITEMS)
    assert clean == []
    assert "is invalid" in problems[0]


def test_unknown_item_is_skipped_and_reported():
    clean, problems = validation.clean_responses([row(item_id="K11")], ITEMS)
    assert clean == []
    assert "was not found" in problems[0]


def test_unknown_action_is_skipped_and_reported():
    clean, problems = validation.clean_responses([row(action="forward")], ITEMS)
    assert clean == []
    assert "is not valid" in problems[0]


def test_action_is_case_insensitive():
    clean, problems = validation.clean_responses([row(action=" Report ")], ITEMS)
    assert clean[0]["action"] == "report"
    assert problems == []


def test_duplicate_answer_keeps_the_last_one():
    first = row(classified=False, action="open")
    second = row(classified=True, action="report")
    clean, problems = validation.clean_responses([first, second], ITEMS)
    assert len(clean) == 1
    assert clean[0]["action"] == "report"
    assert "duplicate answer" in problems[0]


def test_one_bad_row_does_not_remove_the_good_rows():
    rows = [row(pid="P01"), row(pid="bad id"), row(pid="P02")]
    clean, problems = validation.clean_responses(rows, ITEMS)
    assert {r["participant_id"] for r in clean} == {"P01", "P02"}
    assert len(problems) == 1


def test_missing_answers_lists_the_blank_items():
    missing = validation.missing_answers([row(item_id="K1")], ITEMS)
    assert missing == {"P01": ["S6"]}


def test_missing_answers_is_empty_when_everything_is_answered():
    rows = [row(item_id="K1"), row(item_id="S6", classified=False, action="open")]
    assert validation.missing_answers(rows, ITEMS) == {}


def test_matched_participants_only_includes_people_in_both_tests():
    pre = [row(pid="P01"), row(pid="P02")]
    post = [row(pid="p01")]
    assert validation.matched_participants(pre, post) == {"P01"}


def test_keep_only_filters_by_participant():
    rows = [row(pid="P01"), row(pid="P02")]
    assert validation.keep_only(rows, {"P02"}) == [rows[1]]
