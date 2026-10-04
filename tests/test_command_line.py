"""
Tests for the command line program and the CSV loader.

These run the program the same way it will run on the real exports. They use
small CSV files saved to a temporary folder and also check the privacy rule.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "scoring"))

import score_assessments  # noqa: E402

ITEM_CSV = "item_id,indicator,kind,is_phishing\nK1,suspicious_sender,knowledge,TRUE\nS6,none,scenario,FALSE\n"


def write(folder, name, text):
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_file_with_email_column_is_refused(tmp_path):
    bad = write(tmp_path, "pre.csv",
                "participant_id,email,item_id,classified_as_phishing,action\n"
                "P01,someone@example.com,K1,TRUE,report\n")
    with pytest.raises(SystemExit) as stopped:
        score_assessments.load_responses(bad)
    assert "identifying column" in str(stopped.value)


def test_file_with_name_column_is_refused(tmp_path):
    bad = write(tmp_path, "pre.csv",
                "Name,participant_id,item_id,classified_as_phishing,action\n"
                "Jane,P01,K1,TRUE,report\n")
    with pytest.raises(SystemExit):
        score_assessments.load_responses(bad)


def test_empty_response_file_is_refused(tmp_path):
    empty = write(tmp_path, "pre.csv", "participant_id,item_id,classified_as_phishing,action\n")
    with pytest.raises(SystemExit):
        score_assessments.load_responses(empty)


def test_true_false_text_is_read_correctly(tmp_path):
    path = write(tmp_path, "pre.csv",
                 "participant_id,item_id,classified_as_phishing,action\n"
                 "P01,K1,Yes,report\nP01,S6,FALSE,open\n")
    rows = score_assessments.load_responses(path)
    assert rows[0]["classified_as_phishing"] is True
    assert rows[1]["classified_as_phishing"] is False


def test_full_run_on_sample_data_writes_summary(tmp_path, capsys):
    out = tmp_path / "summary.json"
    code = score_assessments.main([
        "--pre", str(ROOT / "data/sample/pre_assessment_sample.csv"),
        "--post", str(ROOT / "data/sample/post_assessment_sample.csv"),
        "--items", str(ROOT / "assessments/item_mapping.csv"),
        "--out", str(out),
    ])
    assert code == 0
    summary = json.loads(out.read_text(encoding="utf-8"))
    assert summary["participants"] == 16
    assert summary["average_score"]["improvement"] == 28.12
    assert "RESULTS SUMMARY" in capsys.readouterr().out


def test_messy_export_is_cleaned_and_problems_are_shown(capsys):
    score_assessments.main([
        "--pre", str(ROOT / "data/sample/pre_assessment_messy_sample.csv"),
        "--post", str(ROOT / "data/sample/post_assessment_messy_sample.csv"),
        "--items", str(ROOT / "assessments/item_mapping.csv"),
    ])
    warnings = capsys.readouterr().err
    assert "duplicate answer" in warnings
    assert "is invalid" in warnings
    assert "P04 did not complete both tests" in warnings
    assert "left 1 item(s) blank: K7" in warnings


def test_missing_input_file_stops_the_run(tmp_path):
    items = write(tmp_path, "items.csv", ITEM_CSV)
    with pytest.raises(SystemExit):
        score_assessments.main(["--pre", str(tmp_path / "nope.csv"),
                                "--post", str(tmp_path / "nope.csv"),
                                "--items", str(items)])
