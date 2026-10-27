# Lab 5: Static Code Analysis

Shashank D | SRN: PES1UG24CS433

## Submission contents

- `parking_system.py`: cleaned program.
- `issues.md`: 13 documented issues, including findings from all three tools.
- `reflection.md`: four prepared reflection answers; see missing-question note.
- `reports/before/` and `reports/after/`: Pylint, Bandit and Flake8 reports.
- `original/parking_system.py`: unchanged baseline for line references.
- `test_parking_system.py` and `reports/test_results.txt`: 18 passing tests.
- `Lab5_Report.pdf`: printable summary, issue table and reflections.
- `requirements.txt`: exact installed tool versions and dependencies.
- The ZIP also includes `git_history.bundle` and `commit_history.txt`.

## Verified results

| Check | Before | After |
|---|---:|---:|
| Pylint | 6.32/10 (21 messages) | 10.00/10 |
| Bandit | 2 Low findings; 0 Medium/High | 0 findings |
| Flake8 | 16 violations | 0 violations |
| Regression tests | Not run on original | 18 passed |

The empty final Flake8 report is expected: a successful run emits no violations.
Tool checks target `parking_system.py`, matching the lab scope. No rule
suppression or custom score configuration was used.

## Reproduce the checks (Python 3.12)

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pylint --persistent=n parking_system.py
python -m bandit -r parking_system.py
python -m flake8 parking_system.py
python -m unittest -v test_parking_system.py
python parking_system.py
```

For baseline checks, run the same three analysis commands inside `original/`.
Run the demonstration in a fresh directory or retain a backup of your data.
Reports combine stdout and stderr so diagnostic context is retained.

## Three local commits

1. Fix Bandit findings: secure permit IDs and explicit exceptions.
2. Fix Pylint findings and validate permit data and expiry.
3. Fix Flake8 spacing and add lab deliverables and verification evidence.

This lab is published in the `Lab 5` folder of
https://github.com/shashankd06/PES1UG24CS433_Campus-Academic-Operations
as three corresponding commits. Their hashes differ from the original local
commits because the files now belong to this repository under `Lab 5/`.
`commit_history.txt` lists the original commits preserved in `git_history.bundle`.
The PDF and ZIP are the original prepared submission snapshots from before
publication; their local-only wording describes that preparation stage.
The original assignment README is preserved as `SOURCE_README.md`.

To recover the original standalone history, run from this folder:

```text
git clone git_history.bundle restored_repository
git -C restored_repository log -3 --oneline
```

The bundle includes baseline history plus the three new commits. The ZIP omits
the live `.git` directory, caches and virtual environment. GitHub commit history records the three folder-scoped publication commits.

## Behavior and scope

Valid plates are non-empty strings; this lab does not enforce jurisdiction-specific
plate syntax. Permits remain valid through their expiry date. The demonstration
now uses valid zones and ISO dates. Invalid input examples are covered by tests.
Missing database files start empty; malformed or inaccessible files produce a
visible error and are not silently replaced. The file store remains a simple
single-process lab implementation, without transactional writes or file locking.

## Provenance and reflection note

Repository: https://github.com/SETAPESU26/L5_10_parking_permits
Baseline commit: 127891f607978b73040587cbb73c7a3b6bb6151a
Source handout: Lab_5_Static_Code_Analysis_Student_handout.pdf (3 pages).
Prepared 27 October 2026 for Shashank D, PES1UG24CS433.
The source handout omits the reflection questions referenced by the README.
Four relevant substitute prompts and drafted answers are clearly labeled.
