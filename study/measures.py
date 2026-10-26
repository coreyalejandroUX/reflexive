#!/usr/bin/env python3
"""
measures.py: oversight measures for the mobile study, computed after unblinding.

Inputs
  decisions.jsonl  one review decision per line (written during the study):
      decision_id, session_id, item_id, device (phone|desktop),
      presented_at, decided_at (ISO 8601), dwell_ms (number),
      outcome (supported|not_supported|unsure|stopped),
      item_words (number), interrupted (bool)
    The phone (Phase 0 Shortcut) cannot see app switches, so any dwell longer
    than --interrupt-s also counts as interrupted for timing.
  seed_key.jsonl   the UNSEALED key, one line per item:
      item_id, seeded (bool), seed_kind (unsupported_claim|wrong_code|null)

Outputs, per device and overall (JSON on stdout):
  catch_rate          seeded items flagged (not_supported or unsure) / seeded decided
  catch_rate_strict   seeded items marked not_supported / seeded decided
  escape_rate         seeded unsupported claims accepted / seeded unsupported claims decided
  false_flag_rate     clean items flagged / clean decided
  rubber_stamp_rate   accepts faster than a minimum reading time / all accepts
  median_dwell_s      over decided, uninterrupted items
  stops               sessions ended by the stop rule or by choice
Plus a randomization test of the phone-minus-desktop catch-rate difference.
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

DEVICES = ("phone", "desktop")
OUTCOMES = {"supported", "not_supported", "unsure", "stopped"}
DECIDED = {"supported", "not_supported", "unsure"}
FLAGGED = {"not_supported", "unsure"}
NUMBER = (int, float)
DECISION_FIELDS = {
    "decision_id": str, "session_id": str, "item_id": str, "device": str,
    "presented_at": str, "decided_at": str, "dwell_ms": NUMBER,
    "outcome": str, "item_words": NUMBER, "interrupted": bool,
}


def validate_decision(d: dict):
    """Return a list of problems. An empty list means the decision is usable."""
    problems = []
    for key, typ in DECISION_FIELDS.items():
        if key not in d:
            problems.append(f"missing {key}")
        elif not isinstance(d[key], typ) or (typ is NUMBER and isinstance(d[key], bool)):
            problems.append(f"{key} must be {'number' if typ is NUMBER else typ.__name__}")
    if problems:
        return problems
    if d["device"] not in DEVICES:
        problems.append(f"device must be one of {DEVICES}")
    if d["outcome"] not in OUTCOMES:
        problems.append(f"outcome must be one of {sorted(OUTCOMES)}")
    if d["dwell_ms"] < 0:
        problems.append("dwell_ms must be >= 0")
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
    accepts = [d for d in decided if d["outcome"] == "supported"]
    stamps = [d for d in accepts if d["dwell_ms"] < min_read_ms(d["item_words"], wps)]
    timed = [d["dwell_ms"] / 1000 for d in decided
             if not d["interrupted"] and d["dwell_ms"] <= interrupt_s * 1000]
    return {
        "decided": len(decided),
        "seeded_decided": len(seeded),
        "catch_rate": wilson(sum(d["outcome"] in FLAGGED for d in seeded), len(seeded)),
        "catch_rate_strict": wilson(sum(d["outcome"] == "not_supported" for d in seeded), len(seeded)),
        "escape_rate": wilson(sum(d["outcome"] == "supported" for d in claims), len(claims)),
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


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run(decisions, key_rows, wps=8.0, iters=20000, seed=1, interrupt_s=120):
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
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args(argv)
    try:
        result = run(read_jsonl(args.decisions), read_jsonl(args.seed_key),
                     args.wps, args.iters, args.seed, args.interrupt_s)
    except ValueError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
