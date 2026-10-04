"""
Evaluation metrics for the phishing awareness training study.

Each function here answers one part of the three research questions defined in the
project proposal:

    RQ1 - recognition:  average_score, score_improvement, mastery_rate
    RQ2 - response:     correct_response_rate
    RQ3 - indicators:   per_indicator_accuracy, false_alarm_rate

All functions take plain Python data structures so they can be tested without a
spreadsheet or survey tool present.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence

from . import validation

# An item record describes one assessment question.
#   item_id    - matches between the pre-test and post-test
#   indicator  - one of the five phishing indicators, or "none" for legitimate mail
#   kind       - "knowledge" or "scenario"
#   is_phishing- True if the mock message is a phishing message
ITEM_KEYS = ("item_id", "indicator", "kind", "is_phishing")

# A response record describes one participant's answer to one item.
#   participant_id - pseudonymous ID, never a name
#   item_id        - the item answered
#   classified_as_phishing - what the participant decided
#   action         - "report", "verify", "delete", "open", or "reply"
RESPONSE_KEYS = ("participant_id", "item_id", "classified_as_phishing", "action")

SAFE_ACTIONS = {"report", "verify"}
FIVE_INDICATORS = (
    "suspicious_sender",
    "misleading_link",
    "urgent_language",
    "credential_request",
    "unexpected_attachment",
)


def _index_items(items: Iterable[Mapping]) -> Dict[str, Mapping]:
    """Build an item_id -> item lookup, rejecting duplicates."""
    indexed: Dict[str, Mapping] = {}
    for item in items:
        item_id = item["item_id"]
        if item_id in indexed:
            raise ValueError(f"duplicate item_id in item bank: {item_id}")
        indexed[item_id] = item
    return indexed


def _usable(responses: Sequence[Mapping], indexed: Mapping[str, Mapping]) -> List[Dict]:
    """Responses that passed validation, with one answer per person per question."""
    clean, _problems = validation.clean_responses(responses, indexed.values())
    return clean


def is_correct(response: Mapping, item: Mapping) -> bool:
    """A response is correct when the participant classified the message correctly."""
    return bool(response["classified_as_phishing"]) == bool(item["is_phishing"])


def is_safe_action(response: Mapping, item: Mapping) -> bool:
    """
    A scenario response is safe when the participant chose an action that does not
    expose them. Reporting or verifying a phishing message is safe. Opening or
    replying to one is not. For a legitimate message, any action except reporting
    it as phishing is acceptable, because over-reporting has its own cost.
    """
    action = response["action"]
    if item["is_phishing"]:
        return action in SAFE_ACTIONS
    return action != "report"


def average_score(responses: Sequence[Mapping], items: Iterable[Mapping]) -> float:
    """Mean percentage score across all participants."""
    indexed = _index_items(items)
    per_participant = participant_scores(responses, indexed.values())
    if not per_participant:
        return 0.0
    return round(sum(per_participant.values()) / len(per_participant), 2)


def participant_scores(responses: Sequence[Mapping],
                       items: Iterable[Mapping]) -> Dict[str, float]:
    """
    Percentage score for each participant.

    The score is out of every question in the item bank, not just the ones the
    participant answered. A blank answer counts as wrong. Otherwise someone could
    skip a hard question and end up with a higher percentage.
    """
    indexed = _index_items(items)
    total_items = len(indexed)
    correct: Dict[str, int] = defaultdict(int)
    seen = set()

    for response in _usable(responses, indexed):
        item = indexed[response["item_id"]]
        seen.add(response["participant_id"])
        if is_correct(response, item):
            correct[response["participant_id"]] += 1

    return {pid: round(100.0 * correct[pid] / total_items, 2) for pid in sorted(seen)}


def score_improvement(pre_responses: Sequence[Mapping],
                      post_responses: Sequence[Mapping],
                      items: Iterable[Mapping]) -> float:
    """
    Percentage-point improvement from pre-test to post-test.

    Goal 3 of the proposal sets a target of at least 20 percentage points.
    """
    items = list(items)
    return round(average_score(post_responses, items) - average_score(pre_responses, items), 2)


def mastery_rate(responses: Sequence[Mapping], items: Iterable[Mapping],
                 threshold: float = 80.0) -> float:
    """
    Share of participants scoring at or above the threshold.

    Goal 4 of the proposal sets a target of 80% of participants at 80% or higher.
    """
    scores = participant_scores(responses, items)
    if not scores:
        return 0.0
    reached = sum(1 for score in scores.values() if score >= threshold)
    return round(100.0 * reached / len(scores), 2)


def correct_response_rate(responses: Sequence[Mapping],
                          items: Iterable[Mapping]) -> float:
    """
    Share of scenario items where the participant chose a safe action.

    This is the RQ2 measure. It is tracked separately from recognition because a
    participant can correctly identify a phishing message and still take an unsafe
    action with it.
    """
    indexed = _index_items(items)
    considered = 0
    safe = 0

    for response in _usable(responses, indexed):
        item = indexed[response["item_id"]]
        if item["kind"] != "scenario":
            continue
        considered += 1
        if is_safe_action(response, item):
            safe += 1

    if not considered:
        return 0.0
    return round(100.0 * safe / considered, 2)


def per_indicator_accuracy(responses: Sequence[Mapping],
                           items: Iterable[Mapping]) -> Dict[str, float]:
    """
    Recognition accuracy broken out by phishing indicator.

    This is the RQ3 measure. It shows which indicators improved and which stayed
    difficult, which is what drives the training recommendations.
    """
    indexed = _index_items(items)
    correct: Dict[str, int] = defaultdict(int)
    answered: Dict[str, int] = defaultdict(int)

    for response in _usable(responses, indexed):
        item = indexed[response["item_id"]]
        if not item["is_phishing"]:
            continue
        indicator = item["indicator"]
        answered[indicator] += 1
        if is_correct(response, item):
            correct[indicator] += 1

    return {
        indicator: round(100.0 * correct[indicator] / answered[indicator], 2)
        for indicator in sorted(answered) if answered[indicator]
    }


def false_alarm_rate(responses: Sequence[Mapping],
                     items: Iterable[Mapping]) -> float:
    """
    Share of legitimate messages incorrectly flagged as phishing.

    Training that raises recognition by making participants suspicious of every
    message has not succeeded. It has moved the cost to the help desk instead. A
    rising false alarm rate alongside a rising average score is a warning sign,
    not a result.
    """
    indexed = _index_items(items)
    legitimate = 0
    flagged = 0

    for response in _usable(responses, indexed):
        item = indexed[response["item_id"]]
        if item["is_phishing"]:
            continue
        legitimate += 1
        if response["classified_as_phishing"]:
            flagged += 1

    if not legitimate:
        return 0.0
    return round(100.0 * flagged / legitimate, 2)


def participant_improvement(pre_responses: Sequence[Mapping],
                            post_responses: Sequence[Mapping],
                            items: Iterable[Mapping]) -> Dict[str, Dict[str, float]]:
    """
    Pre-test score, post-test score, and change for each participant.

    Only people who did both tests are included, because you cannot measure a
    change for someone who only has one score.
    """
    items = list(items)
    pre_scores = participant_scores(pre_responses, items)
    post_scores = participant_scores(post_responses, items)
    return {
        pid: {
            "pre": pre_scores[pid],
            "post": post_scores[pid],
            "change": round(post_scores[pid] - pre_scores[pid], 2),
        }
        for pid in sorted(set(pre_scores) & set(post_scores))
    }


def rank_indicator_changes(pre_accuracy: Mapping[str, float],
                           post_accuracy: Mapping[str, float]) -> List[Dict[str, float]]:
    """
    Indicators sorted from most improved to least improved.

    This is for RQ3. The top of the list shows what the training taught well and
    the bottom shows what still needs more work.
    """
    ranked = [
        {"indicator": name,
         "pre": pre_accuracy.get(name, 0.0),
         "post": post_accuracy[name],
         "change": round(post_accuracy[name] - pre_accuracy.get(name, 0.0), 2)}
        for name in post_accuracy
    ]
    return sorted(ranked, key=lambda row: (-row["change"], row["indicator"]))


def summarise(pre_responses: Sequence[Mapping],
              post_responses: Sequence[Mapping],
              items: Iterable[Mapping]) -> Dict[str, object]:
    """
    Calculate the results and check if the success criteria were met.

    The responses are cleaned first. Only participants who completed
    both the pre-assessment and post-assessment are compared.
    """

    items = list(items)

    # Clean the pre-assessment and post-assessment responses
    pre_clean, pre_problems = validation.clean_responses(pre_responses, items)
    post_clean, post_problems = validation.clean_responses(post_responses, items)

    # Find participants who completed both assessments
    matched = validation.matched_participants(pre_clean, post_clean)

    # Find participants who did not complete both assessments
    everyone = {response["participant_id"] for response in pre_clean + post_clean}
    unmatched = sorted(everyone - matched)

    # Only keep participants who completed both assessments
    pre = validation.keep_only(pre_clean, matched)
    post = validation.keep_only(post_clean, matched)

    pre_avg = average_score(pre, items)
    post_avg = average_score(post, items)
    improvement = round(post_avg - pre_avg, 2)
    post_mastery = mastery_rate(post, items)
    pre_response = correct_response_rate(pre, items)
    post_response = correct_response_rate(post, items)
    response_gain = round(post_response - pre_response, 2)
    pre_indicators = per_indicator_accuracy(pre, items)
    post_indicators = per_indicator_accuracy(post, items)

    return {
        "participants": len(matched),
        "excluded_unmatched": unmatched,
        "data_problems": {"pre": pre_problems, "post": post_problems},
        "average_score": {"pre": pre_avg, "post": post_avg, "improvement": improvement},
        "participant_improvement": participant_improvement(pre, post, items),
        "mastery_rate_post": post_mastery,
        "correct_response_rate": {
            "pre": pre_response, "post": post_response, "improvement": response_gain,
        },
        "per_indicator_accuracy": {"pre": pre_indicators, "post": post_indicators},
        "indicator_ranking": rank_indicator_changes(pre_indicators, post_indicators),
        "false_alarm_rate": {
            "pre": false_alarm_rate(pre, items),
            "post": false_alarm_rate(post, items),
        },
        "success_criteria": {
            "goal_3_score_improvement_20pp": improvement >= 20.0,
            "goal_4_mastery_80pct_at_80": post_mastery >= 80.0,
            "response_rate_improvement_20pp": response_gain >= 20.0,
        },
    }
