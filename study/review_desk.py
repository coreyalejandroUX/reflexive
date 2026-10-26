#!/usr/bin/env python3
"""
review_desk.py: the desktop side of Review (step 5), logged for the study.

Shows one review item at a time, in the same two steps as the phone:
  1. the evidence, then Enter
  2. the agent's claim, then one key: s supported, n not supported, u unsure, q stop
and appends one decision per item to decisions.jsonl, in the same format the
phone writes (see study/measures.py). Only items whose queue is "desktop" are
shown, so device is the only thing that differs between the two paths.

Stop rule (the same as on the phone): the session ends after 10 items,
after 8 minutes, or after 3 "unsure" in a row. Ending is never an error.

Usage:
  python3 study/review_desk.py QUEUE.jsonl DECISIONS.jsonl
Queue items: {"item_id", "queue", "evidence", "claim"}. Stdlib only.
"""
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

MAX_ITEMS, MAX_SECONDS, MAX_UNSURE_RUN = 10, 8 * 60, 3
KEYS = {"s": "supported", "n": "not_supported", "u": "unsure", "q": "stopped"}


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
    return [i for i in items if i.get("queue") == "desktop" and i["item_id"] not in done]


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
    started, unsure_run, count = time.monotonic(), 0, 0

    for item in pending(queue_path, decisions_path):
        if count >= MAX_ITEMS or time.monotonic() - started > MAX_SECONDS or unsure_run >= MAX_UNSURE_RUN:
            break
        presented_at, t0 = now_iso(), time.monotonic()
        print("\nEvidence:\n" + item["evidence"])
        input("\n[Enter] to see the claim ")
        print("\nClaim:\n" + item["claim"])
        key = ask("\nSupported by the evidence?  s / n / u   (q to stop): ", KEYS)
        outcome = KEYS[key]
        row = {"decision_id": uuid.uuid4().hex, "session_id": session, "item_id": item["item_id"],
               "device": "desktop", "presented_at": presented_at, "decided_at": now_iso(),
               "dwell_ms": int((time.monotonic() - t0) * 1000), "outcome": outcome,
               "item_words": len((item["evidence"] + " " + item["claim"]).split()),
               "interrupted": False}
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        if outcome == "stopped":
            break
        count += 1
        unsure_run = unsure_run + 1 if outcome == "unsure" else 0

    print("\nSaved. Review is closed for now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
