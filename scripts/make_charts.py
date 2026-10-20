"""
Make the two charts used in the Unit 6 report from the running app.

Start the app first (python app.py), run the load test, then run:

    python scripts/make_charts.py

The charts are saved in the charts/ folder:
    chart-latency.png     average and 95th percentile response time for each API route
    chart-indicators.png  accuracy for each warning sign before and after training

matplotlib is only needed for this script, so it is not in requirements.txt.
Install it with: python -m pip install matplotlib
"""

import json
import os
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
OUT = Path(__file__).resolve().parent.parent / "charts"
PRE_COLOR, POST_COLOR = "#2a78d6", "#eb6834"

ROUTES = {
    "GET /api/results/summary": "Results summary (GET)",
    "GET /api/tests/<test>/questions": "Load questions (GET)",
    "POST /api/tests/<test>/submit": "Submit test (POST)",
    "POST /api/tests/<test>/start": "Start test (POST)",
    "POST /api/participants": "Register participant (POST)",
    "POST /api/feedback": "Send feedback (POST)",
}
SIGNS = {
    "suspicious_sender": "Suspicious\nsender",
    "urgent_language": "Urgent\nlanguage",
    "misleading_link": "Misleading\nlink",
    "unexpected_attachment": "Unexpected\nattachment",
    "credential_request": "Credential\nrequest",
}


def get(path):
    with urllib.request.urlopen(BASE + path) as response:
        return json.load(response)


def clean_axes(ax, grid_axis):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color="#ecebe7")
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def latency_chart(performance):
    rows = {r["route"]: r for r in performance}
    routes = [r for r in ROUTES if r in rows][::-1]
    average = [rows[r]["average_ms"] for r in routes]
    p95 = [rows[r]["p95_ms"] for r in routes]
    y = range(len(routes))

    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=200)
    bars1 = ax.barh([i + 0.2 for i in y], average, height=0.36, color=PRE_COLOR, label="Average")
    bars2 = ax.barh([i - 0.2 for i in y], p95, height=0.36, color=POST_COLOR, label="95th percentile")
    for bars, values in ((bars1, average), (bars2, p95)):
        for bar, value in zip(bars, values):
            ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2, f"{value:g} ms",
                    va="center", fontsize=9, color="#52514e")
    ax.set_yticks(list(y))
    ax.set_yticklabels([ROUTES[r] for r in routes])
    ax.set_xlabel("Response time (milliseconds)")
    ax.set_xlim(0, max(p95) * 1.18)
    ax.set_title("API response time per route", loc="left", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, loc="lower right")
    clean_axes(ax, "x")
    fig.tight_layout()
    fig.savefig(OUT / "chart-latency.png")
    plt.close(fig)


def indicator_chart(summary):
    pre = [summary["per_indicator_accuracy"]["pre"][s] for s in SIGNS]
    post = [summary["per_indicator_accuracy"]["post"][s] for s in SIGNS]
    x = range(len(SIGNS))

    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=200)
    bars1 = ax.bar([i - 0.2 for i in x], pre, width=0.36, color=PRE_COLOR, label="Pre-assessment")
    bars2 = ax.bar([i + 0.2 for i in x], post, width=0.36, color=POST_COLOR, label="Post-assessment")
    for bars, values in ((bars1, pre), (bars2, post)):
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value:.0f}%",
                    ha="center", fontsize=9, color="#52514e")
    ax.set_xticks(list(x))
    ax.set_xticklabels(list(SIGNS.values()), fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Questions answered correctly (%)")
    title = f"Accuracy by warning sign (n = {summary['participants']})"
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, loc="upper left", ncol=2)
    clean_axes(ax, "y")
    fig.tight_layout()
    fig.savefig(OUT / "chart-indicators.png")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    latency_chart(get("/api/metrics/performance"))
    indicator_chart(get("/api/results/summary"))
    print(f"Charts saved in {OUT}")
