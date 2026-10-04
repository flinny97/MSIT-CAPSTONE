"""
Checks the assessment responses before anything gets scored.

This is kept separate from metrics.py on purpose:

    validation.py  decides which answers are allowed in
    metrics.py     calculates the results from those answers

Bad rows are skipped and listed as warnings instead of stopping the whole run.
This way one mistake in a survey export does not throw out everyone else's
answers. Files with names or emails are a different case. Those are blocked in
score_assessments.py and the run stops.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

ALLOWED_ACTIONS = {"report", "verify", "delete", "open", "reply"}

# Participant IDs look like P01, P02 ... P120. Anything else is treated as a
# mistake, because a real name typed in the ID box should never get scored.
PARTICIPANT_ID_PATTERN = re.compile(r"^P\d{2,3}$")


def normalize_id(participant_id: str) -> str:
    """Remove extra spaces and use capital letters so ' p01 ' and 'P01' match."""
    return str(participant_id).strip().upper()


def clean_responses(responses: Sequence[Mapping],
                    items: Iterable[Mapping]) -> Tuple[List[Dict], List[str]]:
    """
    Check the responses before scoring them.
    This checks:
      1. The participant ID is in the correct format.
      2. The question exists in the item bank.
      3. The action is allowed.
      4. If the same question was answered more than once,
         the most recent answer is used.
    """

    known_items = {item["item_id"] for item in items}
    problems = []
    clean_data = {}

    for row_number, response in enumerate(responses, start=1):
        participant_id = normalize_id(response["participant_id"])
        item_id = str(response["item_id"]).strip()
        action = str(response["action"]).strip().lower()
        # Check participant ID
        if not PARTICIPANT_ID_PATTERN.match(participant_id):
            problems.append(
                f"row {row_number}: participant ID '{participant_id}' is invalid, row skipped"
            )
            continue
        # Check if the question exists
        if item_id not in known_items:
            problems.append(
                f"row {row_number}: item '{item_id}' was not found, row skipped"
            )
            continue
        # Check if the action is allowed
        if action not in ALLOWED_ACTIONS:
            problems.append(
                f"row {row_number}: action '{action}' is not valid, row skipped"
            )
            continue
        key = (participant_id, item_id)
        # Keep the last answer if there is a duplicate
        if key in clean_data:
            problems.append(
                f"row {row_number}: duplicate answer for {participant_id} and {item_id}, last answer kept"
            )
        clean_data[key] = {
            "participant_id": participant_id,
            "item_id": item_id,
            "classified_as_phishing": bool(response["classified_as_phishing"]),
            "action": action,
        }
    return list(clean_data.values()), problems


def missing_answers(responses: Sequence[Mapping], items: Iterable[Mapping]) -> Dict[str, List[str]]:
    """List the questions each participant left blank. People with no blanks are left out."""
    all_items = [item["item_id"] for item in items]
    answered: Dict[str, Set[str]] = {}
    for response in responses:
        answered.setdefault(normalize_id(response["participant_id"]), set()).add(response["item_id"])
    return {
        pid: [item_id for item_id in all_items if item_id not in done]
        for pid, done in sorted(answered.items())
        if len(done) < len(all_items)
    }


def matched_participants(pre: Sequence[Mapping], post: Sequence[Mapping]) -> Set[str]:
    """Participants who did both the pre-test and the post-test."""
    pre_ids = {normalize_id(r["participant_id"]) for r in pre}
    post_ids = {normalize_id(r["participant_id"]) for r in post}
    return pre_ids & post_ids


def keep_only(responses: Sequence[Mapping], participant_ids: Set[str]) -> List[Mapping]:
    """Return only the responses from the participants given."""
    return [r for r in responses if normalize_id(r["participant_id"]) in participant_ids]
