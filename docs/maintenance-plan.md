# Maintenance plan

## Types of maintenance for this project

| Type | What it means here | Example |
| --- | --- | --- |
| Corrective | Fix defects found by participants, the tests, or the dashboard | The two input bugs fixed in Unit 7 |
| Adaptive | Keep the app working when Python, Flask, the browser, or the host changes | Updating Flask when a new version is released, renewing the free hosting each month |
| Perfective | Improve the training and the app based on feedback and new threats | Replacing a question when a new phishing method appears, saving answers if the page is refreshed |
| Preventive | Lower the chance of future problems | Monthly dependency updates, tests on every change, database backups |

## Schedule

| When | Task |
| --- | --- |
| Every pilot session | Check the dashboard for unfinished tests and errors. Copy the database file to a backup |
| Every week of the pilot | Review response times in the dashboard and read the feedback comments |
| Every month | Renew the hosted site. Review and merge Dependabot pull requests. Run the full test suite and the stability test |
| Every year, or when a major report is released | Review the questions and lesson against new phishing reports and replace outdated examples |
| After the final report | Delete all participant data, as promised in the consent form |

## Version updates, bug fixes, and enhancement requests

1. Every change starts as a GitHub issue (bug, enhancement, or content update template).
2. Issues are ranked: privacy or data problems first, then wrong scores, then anything that blocks a participant, then cosmetic issues.
3. The work is done on a `fix/` or `feature/` branch with a test that shows the problem.
4. A pull request into `development` runs every test in GitHub Actions. Only passing changes are merged.
5. `development` is merged into `main` between pilot sessions, never during one.
6. Each release gets a tag and a CHANGELOG entry: `v1.0` at the pilot launch, `v1.0.1` for a bug fix, `v1.1` for an enhancement.
7. If a release causes a problem, the previous tag is deployed again.

## Risks and mitigation

| Risk | Mitigation |
| --- | --- |
| A security problem in Flask or another library | Dependabot updates every month, debug mode off, secret key set on the server |
| The dashboard password is weak or shared | A long password set only on the server in `CAPSTONE_ADMIN_PASSWORD`, changed after the pilot |
| Participant data is exposed or the file is lost | No names or emails stored, the database file encrypted before real data is collected, backups after each session, data deleted after the report |
| Data inconsistency, such as partial or duplicate tests | Server-side validation, only completed tests are scored, stability test after each update |
| Usability problems for participants | Ease ratings and comments reviewed weekly, small fixes released between sessions |
| The free hosted site expires or goes down | Monthly reminder to renew, the app can run locally from the last tag |
| The training becomes outdated | Yearly content review using the content update template |
