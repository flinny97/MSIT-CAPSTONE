# Source code

`scoring/validation.py` checks every response before it is scored. It skips rows with a
malformed participant ID, an unknown item, or an unknown action, keeps only the last
answer when an item was answered twice, and reports each problem.

`scoring/metrics.py` computes the six evaluation metrics defined in the project
proposal, using only participants who completed both tests.

`scoring/score_assessments.py` is the command line entry point that reads the exported
assessment CSV files and writes a results summary.

The loader refuses any response file containing a name or email column. Responses
must be keyed by participant ID only.
