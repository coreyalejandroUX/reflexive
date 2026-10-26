# VERIFICATION_AND_TRUTH: Reflexive iPhone layer

**truth_status:** `draft` · **evaluated:** 2026-10-26

## EXISTS (present in this repository)
- Design: docs/iphone/ (10 deliverables + concepts).
- Code: envelope schema 0.1, `ingest.py`, `policy_gate.py`, `seal.py`, `review_desk.py`, `measures.py`, `run_redteam.py`, 24 red-team prompts.
- 36 unit tests.

## VERIFIED AGAINST
- All 36 tests pass on Python 3.13 (stdlib only).
- `ingest.py` was run from the command line on a synthetic envelope: PRESERVED, then DUPLICATE on replay.
- `review_desk.py` was run with scripted input; its rows pass `measures.validate_decision`.
- `run_redteam.py` was run without an agent: 9 of 9 structural attacks held, and 15 agent attacks were reported as not run.

## NOT CLAIMED
- Not tested against schema 2.1, the 68-capture corpus, or the existing 19 tests. None of them was reachable: the GitHub repo was empty, and they were not in Drive.
- The Shortcuts recipes (Note, Check, Pause) are specified, not built or tested on a device. Offline dictation inside Shortcuts is unverified (a fallback is given).
- No seeding environment exists yet. `seal.py` is its tested core.
- No live-agent red-team run. No study data. No effect estimated.
- Nothing here has had ethics or IRB review or OSF registration.

## FUNCTIONAL STATUS
**PARTIAL.** Phase 0 can run once the Shortcuts are built and the ingest raw path is pointed at the real corpus.
