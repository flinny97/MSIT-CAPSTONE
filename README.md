# Improving Employee Phishing Awareness and Response

Capstone project repository, MSIT 5910, University of the People
Author: Frank Lin · Supervisor: Dr. Stella Tonye Whyte · AY2027-T1

---

## About this project

Organizations spend heavily on email filtering, but a single employee decision can still
undo those controls. Most awareness programs record that an employee *completed* training
without ever testing whether that employee can now recognize a phishing message or knows
what to do with one. This project closes that gap. It builds a short, practical phishing
awareness training package and measures recognition and response with matched pre-training
and post-training assessments.

The system is not a production security product. It is a self-contained training and
measurement instrument built from free, widely available tools, designed to run safely with
10 to 20 volunteer participants over an eight-week schedule.

## Repository structure

| Folder | Contents |
| --- | --- |
| `docs/` | Written deliverables, literature review, project proposal, requirements and design specification, version control plan |
| `design/` | System architecture diagram, data flow diagram, branching model, and the scripts that generate them |
| `src/` | Source code for validating responses, scoring assessments, and computing the six evaluation metrics |
| `tests/` | Unit tests for the scoring rules, the validation module, and the command line loader |
| `content/` | Training material, mock email set, phishing indicator checklist, response and reporting guide |
| `assessments/` | Matched pre-training and post-training item banks and the item-to-indicator mapping |
| `data/` | Result files. No real participant data is ever committed here. See `data/README.md` |
| `webapp/` | Flask web app that connects the training, assessments, database, and scoring |
| `scripts/` | Synthetic demo data, load test, and chart scripts |

## The five phishing indicators

All training content and every assessment item maps to one of five indicators:

1. Suspicious sender address
2. Misleading or mismatched link
3. Urgent or threatening language
4. Request for credentials or sensitive information
5. Unexpected attachment

## Evaluation metrics

`src/scoring/` computes six metrics from paired pre-test and post-test records:

| Metric | Definition |
| --- | --- |
| Average score | Mean percentage score across participants, pre and post |
| Percentage-point improvement | Post-test average minus pre-test average |
| Mastery rate | Share of participants scoring 80% or higher post-training |
| Correct response rate | Share of scenario items where the correct action was chosen |
| Per-indicator accuracy | Accuracy broken out by each of the five indicators |
| False alarm rate | Share of legitimate emails incorrectly flagged as phishing |

The false alarm rate matters as much as the others. Training that simply makes everyone
suspicious of every message is not a success, because it shifts the cost onto the help desk
instead of reducing risk.

## Running the scoring code

```bash
python3 -m pip install -r requirements.txt
python3 src/scoring/score_assessments.py \
    --pre  data/sample/pre_assessment_sample.csv \
    --post data/sample/post_assessment_sample.csv \
    --items assessments/item_mapping.csv \
    --out  data/sample/results_summary.json
```

Before any score is calculated, every response passes through `src/scoring/validation.py`.
Rows with a malformed participant ID, an unknown item, or an unknown action are skipped
and reported. If a participant submits the same item twice, only the last answer is kept.
Only participants who completed both the pre-test and the post-test are compared, and a
blank answer counts as incorrect.

Run the tests with a coverage report:

```bash
python3 -m pytest tests/ -v --cov=src --cov=webapp --cov-report=term-missing
```

The tests cover four levels:

| Level | Files | What they check |
| --- | --- | --- |
| Unit | `test_metrics.py`, `test_scoring_rules.py`, `test_validation.py`, `test_command_line.py`, `test_scoring_bridge.py` | Scoring rules and validation on their own |
| Integration | `test_webapp_api.py`, `test_integration_flow.py` | API, database, and scoring working together |
| System | `tests/system/` | The full participant journey in a real browser (Playwright and Chromium) |
| Acceptance | `tests/acceptance/` | Each Unit 3 requirement, plus the manual checklist in `docs/unit7-acceptance-checklist.md` |

Each level can be run on its own, for example `pytest -m unit` or `pytest -m system`.
The system tests need a browser the first time: `python -m playwright install chromium`.
If it is not installed, those tests are skipped and the rest still run. With the app
running, `python scripts/stability_test.py` sends 60 participants through both tests,
20 at a time, and checks that the database saved exactly what was sent.

The files under `data/sample/` are synthetic records generated for testing. They contain no
real participant data.

## Running the web app

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 for the participant pages and http://127.0.0.1:5000/admin for
the researcher dashboard. Settings come from environment variables, listed in
`.env.example`. The dashboard opens without a password on your own computer. On a server,
set `CAPSTONE_ADMIN_PASSWORD` and the browser will ask for it. The database is created in `instance/` the first time the app starts.

The question screenshots are not in the repository. Copy them into
`instance/screenshots/` before running the assessments.

To fill the dashboard with made-up participants for testing:

```bash
python scripts/seed_demo.py
```

Delete `instance/capstone.db` before real data collection so the synthetic records are
removed. With the app running, `python scripts/load_test.py` measures throughput and
`python scripts/make_charts.py` saves the charts in `charts/`.

## Branching model

Two permanent branches, plus short-lived feature branches:

- **`main`**, submitted, working versions only. Every commit on `main` corresponds to a
  deliverable that was handed in. Changes arrive only through a reviewed merge.
- **`development`**, all working commits. Drafts, diagram revisions, and code changes land
  here first.
- **`feature/...`**, one branch per piece of work, such as
  `feature/unit5-validation-testing`. It is merged into `development` through a pull
  request once the tests pass, and then deleted.

## Tags and releases

Each submitted milestone on `main` is tagged and published as a GitHub release.

| Tag | Milestone |
| --- | --- |
| `v0.1-unit3-submission` | Initial development. Requirements, design, item bank, and first scoring code |
| `v0.2-unit4-cicd` | GitHub Actions workflow runs the tests automatically |
| `v0.3-unit5-testing` | Response validation, scoring fixes, and 46 unit tests with coverage |
| `v0.4-unit6-integration` | Web app connecting all four modules, evaluation, and deployment plan |
| `v0.5-unit7-testing` | Integration, system, and acceptance testing, bug and usability fixes, dashboard password, maintenance plan |
| `v1.0-final` | Planned. Final report and analysis of real participant results |

See `CHANGELOG.md` for what changed in each release.

Commit messages follow a `type: summary` convention (`docs:`, `design:`, `content:`,
`assessment:`, `analysis:`, `chore:`, `test:`) so the log reads as a record of project
progress rather than a list of file saves.

See `docs/version-control-plan.md` for the full rationale and `docs/maintenance-plan.md`
for how updates, bug fixes, and enhancement requests are handled after deployment.

## Ethics and safety

- Participants give informed consent before any assessment.
- Records are keyed by participant ID. No names are stored with scores.
- Example emails are either screenshots of real phishing emails that universities and
  Microsoft published as public warnings, or use a fictional company. They are images
  only, so nothing in them can be clicked. No live malware, no working credential forms,
  and no phishing emails are ever sent.
- The researcher dashboard needs a password on a server and only opens locally without
  one. The database file will be encrypted before real data collection, per NIST SP 800-53.
  Only participant IDs are stored.
- All participant data is deleted after the final report is submitted.

## Status

| Milestone | Unit | Status |
| --- | --- | --- |
| Project purpose, scope, literature review | 1 | Complete |
| Proposal, SMART goals, feasibility, Gantt chart | 2 | Complete |
| System architecture, requirements, version control | 3 | Complete |
| CI/CD workflow | 4 | Complete |
| Core logic, unit testing, tags and releases | 5 | Complete |
| Training module and assessment build | 5–6 | Complete |
| System integration, evaluation, and deployment plan | 6 | Complete |
| System testing and maintenance plan | 7 | Complete |
| Participant recruitment and data collection | 6 | Not started |
| Initial project report | 7 | In progress |
| Analysis and final report | 8 | Not started |
