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
| `src/` | Source code for scoring assessments and computing the six evaluation metrics |
| `content/` | Training material, mock email set, phishing indicator checklist, response and reporting guide |
| `assessments/` | Matched pre-training and post-training item banks and the item-to-indicator mapping |
| `data/` | Result files. No real participant data is ever committed here. See `data/README.md` |

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

Run the tests with:

```bash
python3 -m pytest tests/ -v
```

The files under `data/sample/` are synthetic records generated for testing. They contain no
real participant data.

## Branching model

Two permanent branches:

- **`main`**, submitted, working versions only. Every commit on `main` corresponds to a
  deliverable that was handed in. Changes arrive only through a reviewed merge.
- **`development`**, all working commits. Drafts, diagram revisions, and code changes land
  here first.

Commit messages follow a `type: summary` convention (`docs:`, `design:`, `content:`,
`assessment:`, `analysis:`, `chore:`, `test:`) so the log reads as a record of project
progress rather than a list of file saves.

See `docs/version-control-plan.md` for the full rationale.

## Ethics and safety

- Participants give informed consent before any assessment.
- Records are keyed by participant ID. No names are stored with scores.
- All mock phishing content uses fictional names and disabled links. No live malware,
  no working credential forms, no real phishing emails are ever sent.
- Result files are encrypted and access follows least privilege, per NIST SP 800-53.
- All participant data is deleted after the final report is submitted.

## Status

| Milestone | Unit | Status |
| --- | --- | --- |
| Project purpose, scope, literature review | 1 | Complete |
| Proposal, SMART goals, feasibility, Gantt chart | 2 | Complete |
| System architecture, requirements, version control | 3 | Complete |
| Training module and assessment build | 4–5 | In progress |
| Participant recruitment and data collection | 5–6 | Not started |
| Analysis and final report | 7–8 | Not started |
