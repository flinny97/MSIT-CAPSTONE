# Source code

`scoring/metrics.py` computes the six evaluation metrics defined in the project
proposal. `scoring/score_assessments.py` is the command line entry point that reads
the exported assessment CSV files and writes a results summary.

The loader refuses any response file containing a name or email column. Responses
must be keyed by participant ID only.
