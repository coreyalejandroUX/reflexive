#!/usr/bin/env python3
"""
review_desk.py: the desktop side of Review (step 5), logged for the study.

Shows one review item at a time, in the same two steps as the phone:
  1. the evidence, then Enter
  2. the agent's proposal, then one key:
       a approve   n ask for a narrower statement   h hold   r reject   q stop
and appends one decision per item to decisions.jsonl, in the shared-schema
format ($defs/review_decision). Only items whose queue is "desktop" are
shown, so device is the only thing that differs between the two paths.
Items that do not match $defs/review_item are skipped and named.

Stop rule (the same as on the phone): the session ends after 10 items,
after 8 minutes, or after 3 "hold" in a row. Ending is never an error.

Usage:
  python3 study/review_desk.py QUEUE.jsonl DECISIONS.jsonl
Stdlib only.
"""
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "schema"))
from reflexive_schema import validate  # noqa: E402

MAX_ITEMS, MAX_SECONDS, MAX_HOLD_RUN = 10, 8 * 60, 3
KEYS = {"a": "approve", "n": "narrow", "h": "hold", "r": "reject", "q": "stopped"}


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def pending(queue_path, decisions_path):
    done = set()
    if Path(decisions_path).exists():
        with open(decisions_path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        # A stopped item was never decided, so it comes back next session.
        done = {r["item_id"] for r in rows if r["outcome"] != "stopped"}
    with open(queue_path, encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]
    ready = []
    for item in items:
        problems = validate(item, "review_item")
        if problems:
            print(f"[skip] {item.get('item_id', '?')}: {problems}", file=sys.stderr)
        elif item["queue"] == "desktop" and item["item_id"] not in done:
            ready.append(item)
    return ready


def ask(prompt, allowed):
    while True:
        answer = input(prompt).strip().lower()
        if answer in allowed:
            return answer


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    queue_path, decisions_path = argv
    session = f"desk-{uuid.uuid4().hex[:8]}"
    started, hold_run, count = time.monotonic(), 0, 0

    for item in pending(queue_path, decisions_path):
        if count >= MAX_ITEMS or time.monotonic() - started > MAX_SECONDS or hold_run >= MAX_HOLD_RUN:
            break
        presented_at, t0 = now_iso(), time.monotonic()
        print("\nEvidence:\n" + item["evidence"])
        input("\n[Enter] to see the agent's proposal ")
        print("\nAgent proposal:\n" + item["claim"])
        key = ask("\na approve · n narrower · h hold · r reject   (q to stop): ", KEYS)
        outcome = KEYS[key]
        row = {"decision_id": uuid.uuid4().hex, "session_id": session, "item_id": item["item_id"],
               "agent_action_id": item["agent_action_id"], "device": "desktop",
               "presented_at": presented_at, "decided_at": now_iso(),
               "dwell_ms": int((time.monotonic() - t0) * 1000), "outcome": outcome,
               "item_words": item["item_words"], "interrupted": False}
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        if outcome == "stopped":
            break
        count += 1
        hold_run = hold_run + 1 if outcome == "hold" else 0

    print("\nSaved. Review is closed for now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
