# Scoring bridge (M4)
# The Unit 5 scoring code expects each answer as "phishing or not" plus an action.
# The new tests use multiple choice, so each answer is changed into the format the
# Unit 5 code already understands. This way all the results still come from the
# same tested code in src/scoring/metrics.py.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from scoring import metrics  # noqa: E402

# Recognition and legitimate questions are knowledge items.
# Response questions are scenario items, which are used for the correct response rate.
KIND = {"Recognition": "knowledge", "Response": "scenario", "Legitimate": "knowledge"}


def to_scoring_items(questions):
    # Make one scoring item for each question. Q1 on both tests is the same item.
    items = {}
    for q in questions:
        items[q["item_id"]] = {
            "item_id": q["item_id"],
            "indicator": q["indicator"],
            "kind": KIND[q["type"]],
            "is_phishing": q["indicator"] != "none",
        }
    return list(items.values())


def to_scoring_response(row, item):
    # Change one multiple choice answer into the format metrics.py expects
    correct = bool(row["is_correct"])

    if item["is_phishing"]:
        # Phishing email: a correct answer means the participant spotted it and reported it
        classified = correct
        action = "report" if correct else "open"
    else:
        # Real email: a wrong answer means the participant thought it was phishing (false alarm)
        classified = not correct
        action = "open" if correct else "report"

    return {
        "participant_id": row["participant_id"],
        "item_id": row["item_id"],
        "classified_as_phishing": classified,
        "action": action,
    }


def summarise_from_rows(questions, pre_rows, post_rows):
    # Get the scoring items and look them up by question ID
    items = to_scoring_items(questions)
    by_id = {}
    for item in items:
        by_id[item["item_id"]] = item

    # Change every saved answer and send them to the Unit 5 summarise function
    pre = []
    for r in pre_rows:
        pre.append(to_scoring_response(r, by_id[r["item_id"]]))
    post = []
    for r in post_rows:
        post.append(to_scoring_response(r, by_id[r["item_id"]]))
    return metrics.summarise(pre, post, items)
