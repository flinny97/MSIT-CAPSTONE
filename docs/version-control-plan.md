# Version Control Plan

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | Submitted, working versions only. Protected. Updated by reviewed merge. |
| `development` | All working commits. Drafts, revisions, and code changes land here first. |

## Commit message convention

    type: short summary in the imperative

Types used in this project:

| Type | Used for |
| --- | --- |
| `docs:` | Written deliverables and documentation |
| `design:` | Diagrams and design artifacts |
| `content:` | Training material and mock email set |
| `assessment:` | Assessment items and item mapping |
| `analysis:` | Scoring code and results |
| `test:` | Tests |
| `chore:` | Repository setup and maintenance |

## Merge rules

1. Work is committed to `development` in small, related changes.
2. At a unit milestone, a pull request is opened from `development` to `main`.
3. The pull request description lists the deliverables included in that milestone.
4. After review, the branch is merged and the merge commit is tagged with the unit.

## Why this matters for a single-author project

The repository is the audit trail. Because `main` only ever receives reviewed merges,
the commit history on `main` is a list of what was submitted and when. If a change
breaks something, `git diff` shows exactly what changed between two submitted versions
and the change can be reverted without rebuilding the document from memory.
