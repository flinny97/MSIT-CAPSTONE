# Unit 5 testing notes

## Framework

PyTest, with the pytest-cov plugin for coverage. The same command runs locally and in
the GitHub Actions workflow:

    python3 -m pytest tests/ -v --cov=src --cov-report=term-missing

## Test files

| File | Type | What it checks |
| --- | --- | --- |
| `tests/test_scoring_rules.py` | Black-box | Scores at 0, 20, 40, 60, 80, and 100 percent, the 80 percent mastery boundary, negative and zero improvement, unmatched participants, duplicate submissions, ID formatting, blank answers |
| `tests/test_validation.py` | White-box | Each rule inside `clean_responses()` and each helper in `validation.py` |
| `tests/test_metrics.py` | White-box | The six evaluation metrics, written in Unit 3 |
| `tests/test_command_line.py` | Integration-style unit tests | The CSV loader, the privacy rule, and a full run on the sample data |

## Results

46 tests pass. Line coverage is 99 percent. The two uncovered lines are the script's
`if __name__ == "__main__"` entry line and the guard for an empty item bank file.

## Issues the tests found

| Issue | Test that found it | Effect before the fix | Fix |
| --- | --- | --- | --- |
| Participants who only took the pre-test were still included | `test_participant_who_skipped_the_post_test_does_not_change_improvement` | Improvement reported as 53.33 pp instead of 40 pp | Compare matched participants only |
| A form submitted twice was counted twice | `test_duplicate_submission_is_not_counted_twice` | Score of 50 percent from one perfect and one blank submission | Keep the last answer per participant per item |
| A blank answer was ignored instead of counted as wrong | `test_blank_answer_counts_as_incorrect` | Four of five answered scored 100 percent instead of 80 percent | Score out of every item in the item bank |

All three were fixed in `src/scoring/validation.py` and `src/scoring/metrics.py`. The
full synthetic sample gives the same results before and after the fixes, because it has
no gaps or duplicates. The messy sample files in `data/sample/` reproduce each problem
so the warnings can be seen.
