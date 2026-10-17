"""
Load synthetic (made-up) participants into the app so the dashboard has data
to show before real participants take part.

    python scripts/seed_demo.py

It uses the real API, the same way the pages do, so it also exercises the
whole system: consent -> start test -> submit -> scoring. The answers are
generated, not collected from people. Clear them before real data collection by
deleting the database file (instance/capstone.db).

Sixteen participants finish both tests, the same size as the Unit 5 synthetic
sample. P17 only finishes the pre-assessment and P18 starts the post-assessment
but never submits, so the dashboard shows how incomplete tests are left out.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp import create_app  # noqa: E402

LETTERS = ["a", "b", "c", "d"]


def answers_for(client, test, skill, rng):
    """Pick each answer: right with probability 'skill', otherwise a wrong letter."""
    from webapp.db import get_db
    with client.application.app_context():
        key = {r["item_id"]: r["answer"] for r in get_db().execute(
            "SELECT item_id, answer FROM questions WHERE test = ?", (test,))}
    answers = {}
    for item, right in key.items():
        if rng.random() < skill:
            choice, conf = right, rng.choice([3, 4, 4, 5])
        else:
            choice, conf = rng.choice([x for x in LETTERS if x != right]), rng.choice([2, 3, 3, 4])
        answers[item] = {"choice": choice, "confidence": conf}
    return answers


def main(seed=5910):
    rng = random.Random(seed)
    app = create_app()
    client = app.test_client()
    for n in range(1, 19):
        pid = f"P{n:02d}"
        client.post("/api/participants", json={"participant_id": pid, "consent": True})
        client.post("/api/tests/pre/start", json={"participant_id": pid})
        pre = client.post("/api/tests/pre/submit",
                          json={"participant_id": pid, "answers": answers_for(client, "pre", rng.uniform(0.40, 0.70), rng)})
        if n == 17:
            continue  # finished the pre-assessment only
        client.post("/api/tests/post/start", json={"participant_id": pid})
        if n == 18:
            continue  # started the post-assessment but never submitted it
        post = client.post("/api/tests/post/submit",
                           json={"participant_id": pid, "answers": answers_for(client, "post", rng.uniform(0.70, 0.95), rng)})
        client.post("/api/feedback", json={"participant_id": pid, "ease_rating": rng.choice([3, 4, 4, 5, 5])})
        print(pid, "pre", pre.get_json()["score"], "post", post.get_json()["score"])
    print("Synthetic data loaded. Open /admin to see the results.")


if __name__ == "__main__":
    main()
