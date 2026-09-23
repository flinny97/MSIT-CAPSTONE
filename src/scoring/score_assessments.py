#!/usr/bin/env python3
"""
Score paired pre-training and post-training assessments and write a results summary.

Usage:
    python3 src/scoring/score_assessments.py \
        --pre   data/sample/pre_assessment_sample.csv \
        --post  data/sample/post_assessment_sample.csv \
        --items assessments/item_mapping.csv \
        --out   data/sample/results_summary.json

Input CSV columns
-----------------
item_mapping.csv    item_id, indicator, kind, is_phishing
response files      participant_id, item_id, classified_as_phishing, action

The response files must contain participant IDs, never names. The loader rejects a
file containing a column that looks like a name so that a mistake during export
cannot quietly put identifying data into the analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring import metrics  # noqa: E402

FORBIDDEN_COLUMNS = {"name", "full_name", "first_name", "last_name", "email", "employee_id"}
TRUE_VALUES = {"1", "true", "yes", "y", "phishing", "t"}


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in TRUE_VALUES


def _check_columns(path: Path, fieldnames: List[str]) -> None:
    found = FORBIDDEN_COLUMNS.intersection({f.strip().lower() for f in fieldnames})
    if found:
        raise SystemExit(
            f"Refusing to read {path}: identifying column(s) {sorted(found)} present. "
            "Export the responses keyed by participant ID only."
        )


def load_items(path: Path) -> List[Dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append({
                "item_id": row["item_id"].strip(),
                "indicator": row["indicator"].strip(),
                "kind": row["kind"].strip(),
                "is_phishing": _to_bool(row["is_phishing"]),
            })
    if not rows:
        raise SystemExit(f"No items found in {path}")
    return rows


def load_responses(path: Path) -> List[Dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _check_columns(path, reader.fieldnames or [])
        rows = []
        for row in reader:
            rows.append({
                "participant_id": row["participant_id"].strip(),
                "item_id": row["item_id"].strip(),
                "classified_as_phishing": _to_bool(row["classified_as_phishing"]),
                "action": row["action"].strip().lower(),
            })
    if not rows:
        raise SystemExit(f"No responses found in {path}")
    return rows


def check_matched(pre: List[Dict], post: List[Dict]) -> List[str]:
    """Warn about participants who did not complete both assessments."""
    pre_ids = {r["participant_id"] for r in pre}
    post_ids = {r["participant_id"] for r in post}
    warnings = []
    for pid in sorted(pre_ids - post_ids):
        warnings.append(f"participant {pid} completed the pre-test but not the post-test")
    for pid in sorted(post_ids - pre_ids):
        warnings.append(f"participant {pid} completed the post-test but not the pre-test")
    return warnings


def format_report(summary: Dict) -> str:
    avg = summary["average_score"]
    crr = summary["correct_response_rate"]
    far = summary["false_alarm_rate"]

    lines = [
        "=" * 62,
        "  PHISHING AWARENESS TRAINING - RESULTS SUMMARY",
        "=" * 62,
        f"  Participants with complete records : {summary['participants']}",
        "",
        "  RQ1  Recognition",
        f"    Average score pre-training       : {avg['pre']:.2f}%",
        f"    Average score post-training      : {avg['post']:.2f}%",
        f"    Improvement                      : {avg['improvement']:+.2f} pp",
        f"    Scoring 80% or higher after      : {summary['mastery_rate_post']:.2f}%",
        "",
        "  RQ2  Response",
        f"    Correct response rate pre        : {crr['pre']:.2f}%",
        f"    Correct response rate post       : {crr['post']:.2f}%",
        f"    Improvement                      : {crr['improvement']:+.2f} pp",
        "",
        "  RQ3  Accuracy by indicator (phishing items, post-training)",
    ]

    post_ind = summary["per_indicator_accuracy"]["post"]
    pre_ind = summary["per_indicator_accuracy"]["pre"]
    for indicator in sorted(post_ind):
        before = pre_ind.get(indicator, 0.0)
        after = post_ind[indicator]
        label = indicator.replace("_", " ")
        lines.append(f"    {label:<26}: {after:6.2f}%  ({after - before:+.2f} pp)")

    lines += [
        "",
        "  Control measure",
        f"    False alarm rate pre             : {far['pre']:.2f}%",
        f"    False alarm rate post            : {far['post']:.2f}%",
        "",
        "  Success criteria",
    ]
    labels = {
        "goal_3_score_improvement_20pp": "Goal 3  score improvement >= 20 pp",
        "goal_4_mastery_80pct_at_80": "Goal 4  80% of participants at 80%+",
        "response_rate_improvement_20pp": "Response rate improvement >= 20 pp",
    }
    for key, met in summary["success_criteria"].items():
        lines.append(f"    {labels[key]:<40}: {'MET' if met else 'NOT MET'}")
    lines.append("=" * 62)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pre", required=True, type=Path, help="pre-training response CSV")
    parser.add_argument("--post", required=True, type=Path, help="post-training response CSV")
    parser.add_argument("--items", required=True, type=Path, help="item mapping CSV")
    parser.add_argument("--out", type=Path, help="optional JSON output path")
    args = parser.parse_args()

    for path in (args.pre, args.post, args.items):
        if not path.exists():
            raise SystemExit(f"File not found: {path}")

    items = load_items(args.items)
    pre = load_responses(args.pre)
    post = load_responses(args.post)

    for warning in check_matched(pre, post):
        print(f"  warning: {warning}", file=sys.stderr)

    summary = metrics.summarise(pre, post, items)
    print(format_report(summary))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\n  Summary written to {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
