# Changelog

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
