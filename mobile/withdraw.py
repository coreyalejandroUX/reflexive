#!/usr/bin/env python3
"""
withdraw.py: remove a capture from the raw layer on purpose, and keep proof
that it was removed.

"Raw is immutable" means no silent edits. It does not mean a participant can
never take something back. Withdrawal is the one sanctioned way out:

  1. the raw file (and its inbox copy, if given) is deleted
  2. one line goes into WITHDRAWN.jsonl: capture_id, the file's hash, the time
     and a reason code. Never the content and never free text.
  3. ingest.py refuses that capture_id from then on, so an offline replay from
     the phone cannot bring it back

What this does NOT do: erase the file from Git history. Every earlier commit in
the corpus repo (and the phone's clone) still holds it. For full erasure, run
the history step this script prints, then re-clone on the phone.

Usage:
  python3 mobile/withdraw.py --raw PATH --capture-id ID --reason CODE [--inbox PATH]
Reason codes: participant_choice, consent_change, identity_risk, other.
Stdlib only.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "schema"))
from reflexive_schema import definition, validate  # noqa: E402

REASONS = definition("withdrawal")["properties"]["reason"]["enum"]


def withdraw(raw_dir: Path, capture_id: str, reason: str, inbox: Path = None):
    """Return (ok, message)."""
    if reason not in REASONS:
        return False, f"reason must be one of {REASONS}"
    if Path(capture_id).name != capture_id:
        return False, "capture_id must be a bare id"
    target = raw_dir / f"{capture_id}.json"
    if not target.is_file():
        return False, f"{target.name} is not in raw"

    row = {"capture_id": capture_id,
           "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
           "withdrawn_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "reason": reason}
    problems = validate(row, "withdrawal")
    if problems:
        return False, f"withdrawal record invalid: {problems}"

    # Record first, then delete: if deletion fails, the block on re-ingest still holds.
    with open(raw_dir / "WITHDRAWN.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    target.unlink()
    if inbox is not None:
        copy = inbox / f"{capture_id}.json"
        if copy.is_file():
            copy.unlink()
    return True, (f"withdrawn: {capture_id}. Still in Git history; to erase it there, run:\n"
                  f"  git filter-repo --invert-paths --path <path-to>/{capture_id}.json\n"
                  "then force-push the corpus and re-clone it on the phone.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--capture-id", required=True)
    ap.add_argument("--reason", required=True)
    ap.add_argument("--inbox", type=Path)
    args = ap.parse_args(argv)
    ok, message = withdraw(args.raw, args.capture_id, args.reason, args.inbox)
    print(message, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
