# Unit 7 test summary report

## Objectives

- Confirm that the integrated system meets the Unit 3 requirements (FR1 to FR8) before the pilot.
- Find defects that only show up when the modules work together or when the input is unusual.
- Check that the app stays stable when many participants use it at the same time.

## Scope

| In scope | Out of scope |
| --- | --- |
| All four modules (lesson, assessments, database, scoring), the JSON API, and every page | Real participants (only synthetic IDs were used) |
| The full participant journey in Chromium | Other browsers and phones |
| Bad input, restarts, and concurrent use | The hosted site on PythonAnywhere (not deployed yet) |

## Procedure

Every automated test uses its own empty database in a temporary folder, so no test touches
real data. The tests run on my computer with `pytest` and again in GitHub Actions on every
pull request and every push to `development`. The system tests start the real app and use Playwright to control a
Chromium browser. The stability and load tests run against the app with a fresh database:

    python app.py
    python scripts/stability_test.py
    python scripts/load_test.py

## Test levels and results

The test suite grew from 46 tests in Unit 5 to 69 in Unit 6 and 94 in Unit 7. FR2, FR4, and FR5
are tested in their revised Unit 6 form (see `unit3-requirements-and-design.md`).

| Level | What it checks | Tests | Before fixes | After fixes |
| --- | --- | --- | --- | --- |
| Unit | Scoring rules, validation, metrics, scoring bridge | 49 | 49 passed | 49 passed |
| Integration | API, database, and scoring working together, bad input, restarts, dashboard access | 31 | 24 passed, 7 failed | 31 passed |
| System | Full participant journey in a real browser | 5 | 3 passed, 2 failed | 5 passed |
| Acceptance | Each requirement (FR1 to FR8, NFR4, NFR5) plus the manual checklist | 9 | 9 passed | 9 passed |
| **Total** | | **94** | **85 passed, 9 failed** | **94 passed, 99% coverage** |

Stability: 3 rounds of 20 participants at the same time, 480 requests, 0 server errors. The
database saved exactly 120 finished tests and 1,200 answers, which matched what was sent.
Load: 1,000 question requests and 300 results requests, all answered with no failures.

## Issues found and how they were handled

| ID | Issue | Found by | Resolution |
| --- | --- | --- | --- |
| I1 | Answers sent in the wrong format crashed the submit route (server error 500) | Integration test | Fixed. The API checks the format and returns a clear 400 message |
| I2 | `true` was accepted as a 1 to 5 rating and saved as 1 | Integration test | Fixed. Ratings must be whole numbers from 1 to 5 |
| I3 | No progress counter on the test page | Unit 6 usability review, system test | Fixed. The page shows "X of 10 questions answered" |
| I4 | Missing questions were not highlighted | Unit 6 usability review, system test | Fixed. Missing questions are marked until they are answered |
| I5 | The researcher dashboard opened for anyone with the link | Acceptance review | Fixed. It needs a password on a server and only opens locally without one |
| I6 | A helper script used a fixed folder on one computer | Code review | Fixed. It now runs from its own folder |
| L1 | The results route is the slowest under load | Load test | Documented. Saving the summary is planned as an enhancement |
| L2 | The database file is not encrypted (NFR1) | Acceptance review | Documented. No names or emails are stored, the file will be encrypted before real data is collected, and data is deleted after the report |
| L3 | Answers are lost if the page is refreshed during a test | System testing | Documented as a future enhancement |
| L4 | Only tested in Chromium | Test scope | Documented as a limitation. Other browsers and phones were not tested |
