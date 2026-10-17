# Changelog

## v0.5-unit7-testing

- Added integration tests (`tests/test_integration_flow.py`), system tests that run the
  full participant journey in a real browser (`tests/system/`), and acceptance tests for
  each Unit 3 requirement (`tests/acceptance/`). 91 tests pass with 99 percent coverage.
- Fixed: answers sent in the wrong format crashed the submit route. They now get a clear
  400 message.
- Fixed: `true` was accepted as a 1 to 5 rating and saved as 1.
- The test page now shows a progress counter, and missing questions are highlighted
  until they are answered (from the Unit 6 usability review).
- Added `scripts/stability_test.py` (20 participants at the same time, 3 rounds).
- `run_synthetic_test.bat` now runs from its own folder.
- The workflow installs Chromium and runs the system tests.
- Added Dependabot (monthly dependency updates), issue templates for bugs,
  enhancements, and content updates, the test summary report, the acceptance checklist,
  and the maintenance plan.

## v0.4-unit6-integration

- Added a Flask web app (`webapp/`) that connects the four modules: training lesson (M1),
  pre and post assessments (M2), SQLite data store (M3), and the Unit 5 scoring code (M4).
- Added a JSON API. The pages only talk to the database through the API, and the
  correct answers are never sent to the browser.
- A test is only saved when every question has an answer and a confidence rating. Tests
  that were started but not finished are left out of the results and listed separately.
- The post-assessment cannot start until the pre-assessment is finished, and a test
  cannot be submitted twice.
- Added `webapp/scoring_bridge.py` so the multiple choice answers are scored by the same
  tested code in `src/scoring/metrics.py`.
- Added a researcher dashboard, a feedback form, and response time logging for each API
  route.
- Settings now come from environment variables. See `.env.example`.
- Added `scripts/seed_demo.py` (synthetic participants), `scripts/load_test.py`, and
  `scripts/make_charts.py`.
- 69 tests pass with 98 percent line coverage. The workflow now measures coverage for
  `webapp/` as well.

## v0.3-unit5-testing

- Added `src/scoring/validation.py`. Responses are checked before scoring for participant
  ID format, unknown items, unknown actions, and duplicate answers.
- Fixed: participants who completed only one test are no longer included in the
  improvement calculation.
- Fixed: a form submitted twice is no longer counted twice.
- Fixed: a blank answer now counts as incorrect.
- The results report now shows each participant's change and ranks the five indicators
  from most to least improved.
- Added black-box, white-box, and command line tests. 46 tests pass with 99 percent
  line coverage.
- The GitHub Actions workflow now prints a coverage report.

## v0.2-unit4-cicd

- Added a GitHub Actions workflow that runs the tests on every push to `development`
  and on every pull request into `main`.
- Added the Unit 4 CI/CD reflection.

## v0.1-unit3-submission

- Literature review, project proposal, requirements and design specification.
- System architecture, data flow, and branching model diagrams.
- Training content, assessment item bank, and the first version of the scoring code
  with 12 tests.
