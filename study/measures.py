#!/usr/bin/env python3
"""
measures.py: oversight measures for the mobile study, computed after unblinding.

Inputs
  decisions.jsonl  one review decision per line (written during the study):
      decision_id, session_id, item_id, device (phone|desktop),
      presented_at, decided_at (ISO 8601), dwell_ms (number),
      agent_action_id, outcome (approve|narrow|hold|reject|stopped),
      item_words (number), interrupted (bool)
    The phone (Phase 0 Shortcut) cannot see app switches, so any dwell longer
    than --interrupt-s also counts as interrupted for timing.
  seed_key.jsonl   the UNSEALED key, one line per item:
      item_id, seeded (bool), seed_kind (unsupported_claim|wrong_code|null)

Outputs, per device and overall (JSON on stdout):
  catch_rate          seeded items not approved (narrow, hold or reject) / seeded decided
  catch_rate_strict   seeded items actively corrected (narrow or reject) / seeded decided
  escape_rate         seeded unsupported claims approved / seeded unsupported claims decided
  false_flag_rate     clean items flagged / clean decided
  rubber_stamp_rate   accepts faster than a minimum reading time / all accepts
  median_dwell_s      over decided, uninterrupted items
  stops               sessions ended by the stop rule or by choice
Plus a randomization test of the phone-minus-desktop catch-rate difference,
and, if --items gives the review queue, catch rate by the agent's stated
confidence (below 0.5, 0.5 and above, unknown): does the agent's confidence
predict which planted errors get through?
This is valid only because device was randomly assigned per item.

Every rate comes with a 95% Wilson interval. With a pilot's numbers the
intervals will be wide. Report them; do not report a bare rate.

Usage:
  python3 study/measures.py decisions.jsonl seed_key.jsonl [--wps 8] [--interrupt-s 120]
        [--iters 20000]
Stdlib only.
"""
import argparse
import json
import math
import random
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "schema"))
from reflexive_schema import enum, validate  # noqa: E402

DEVICES = tuple(enum("device"))
DECIDED = {"approve", "narrow", "hold", "reject"}
FLAGGED = {"narrow", "hold", "reject"}
CORRECTED = {"narrow", "reject"}


def validate_decision(d: dict):
    """Return a list of problems. An empty list means the decision is usable.

    Field rules come from the shared schema ($defs/review_decision); the time
    order check is a rule the schema cannot express.
    """
    problems = validate(d, "review_decision")
    if problems:
        return problems
    try:
        t0 = datetime.fromisoformat(d["presented_at"])
        t1 = datetime.fromisoformat(d["decided_at"])
        if t1 < t0:
            problems.append("decided_at is before presented_at")
    except ValueError:
        problems.append("timestamps must be ISO 8601")
    return problems


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return {"k": k, "n": n, "rate": round(p, 3),
            "ci95": [round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)]}


def min_read_ms(words, wps):
    return 1000.0 * max(words, 1) / wps


def summarize(decisions, key, wps, interrupt_s=120):
    decided = [d for d in decisions if d["outcome"] in DECIDED]
    seeded = [d for d in decided if key[d["item_id"]]["seeded"]]
    clean = [d for d in decided if not key[d["item_id"]]["seeded"]]
    claims = [d for d in seeded if key[d["item_id"]].get("seed_kind") == "unsupported_claim"]
    accepts = [d for d in decided if d["outcome"] == "approve"]
    stamps = [d for d in accepts if d["dwell_ms"] < min_read_ms(d["item_words"], wps)]
    timed = [d["dwell_ms"] / 1000 for d in decided
             if not d["interrupted"] and d["dwell_ms"] <= interrupt_s * 1000]
    return {
        "decided": len(decided),
        "seeded_decided": len(seeded),
        "catch_rate": wilson(sum(d["outcome"] in FLAGGED for d in seeded), len(seeded)),
        "catch_rate_strict": wilson(sum(d["outcome"] in CORRECTED for d in seeded), len(seeded)),
        "escape_rate": wilson(sum(d["outcome"] == "approve" for d in claims), len(claims)),
        "false_flag_rate": wilson(sum(d["outcome"] in FLAGGED for d in clean), len(clean)),
        "rubber_stamp_rate": wilson(len(stamps), len(accepts)),
        "median_dwell_s": round(statistics.median(timed), 1) if timed else None,
        "interrupted": sum(d["interrupted"] or d["dwell_ms"] > interrupt_s * 1000 for d in decisions),
        "stops": sum(d["outcome"] == "stopped" for d in decisions),
    }


def catch_difference(seeded):
    """phone catch rate minus desktop catch rate, or None if a device has no items."""
    by = {dev: [d["outcome"] in FLAGGED for d in seeded if d["device"] == dev] for dev in DEVICES}
    if not by["phone"] or not by["desktop"]:
        return None
    return statistics.mean(by["phone"]) - statistics.mean(by["desktop"])


def randomization_test(seeded, iters, seed):
    obs = catch_difference(seeded)
    if obs is None:
        return None
    rng = random.Random(seed)
    devices = [d["device"] for d in seeded]
    count = 0
    for _ in range(iters):
        rng.shuffle(devices)
        shuffled = [dict(d, device=dev) for d, dev in zip(seeded, devices)]
        if abs(catch_difference(shuffled)) >= abs(obs) - 1e-12:
            count += 1
    return {"phone_minus_desktop": round(obs, 3), "p_two_sided": round((count + 1) / (iters + 1), 4),
            "iters": iters}


def confidence_band(c):
    if not isinstance(c, (int, float)) or isinstance(c, bool):
        return "unknown"
    return "below_0.5" if c < 0.5 else "0.5_and_above"


def by_confidence(decisions, key, items):
    conf = {i["item_id"]: i.get("confidence", "unknown") for i in items}
    seeded = [d for d in decisions if d["outcome"] in DECIDED and key[d["item_id"]]["seeded"]]
    out = {}
    for band in ("below_0.5", "0.5_and_above", "unknown"):
        rows = [d for d in seeded if confidence_band(conf.get(d["item_id"])) == band]
        out[band] = wilson(sum(d["outcome"] in FLAGGED for d in rows), len(rows))
    return out


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run(decisions, key_rows, wps=8.0, iters=20000, seed=1, interrupt_s=120, items=None):
    key = {r["item_id"]: r for r in key_rows}
    bad = {}
    for d in decisions:
        problems = validate_decision(d)
        if not problems and d["item_id"] not in key:
            problems = ["item_id not in seed key"]
        if problems:
            bad[d.get("decision_id", "?")] = problems
    if bad:
        raise ValueError(f"unusable decisions: {bad}")

    out = {"overall": summarize(decisions, key, wps, interrupt_s)}
    for dev in DEVICES:
        out[dev] = summarize([d for d in decisions if d["device"] == dev], key, wps, interrupt_s)
    seeded = [d for d in decisions if d["outcome"] in DECIDED and key[d["item_id"]]["seeded"]]
    out["device_test"] = randomization_test(seeded, iters, seed)
    if items is not None:
        out["catch_by_confidence"] = by_confidence(decisions, key, items)
    out["note"] = "Single participant. Within-person estimates, not population claims."
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("decisions")
    ap.add_argument("seed_key")
    ap.add_argument("--wps", type=float, default=8.0,
                    help="fastest plausible reading speed, words per second (default 8)")
    ap.add_argument("--interrupt-s", type=float, default=120,
                    help="dwell above this many seconds counts as interrupted (default 120)")
    ap.add_argument("--items", help="review queue (JSONL), for catch rate by agent confidence")
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args(argv)
    try:
        result = run(read_jsonl(args.decisions), read_jsonl(args.seed_key),
                     args.wps, args.iters, args.seed, args.interrupt_s,
                     read_jsonl(args.items) if args.items else None)
    except ValueError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
