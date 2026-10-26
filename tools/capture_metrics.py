#!/usr/bin/env python3
"""
capture_metrics.py: the grant's capture metrics, computed from the raw layer.

Read-only. Reads the phone envelopes in a raw folder and reports:
  attention per capture   median capture_seconds, and the share at or under
                          the 10-second Preserve target (envelope 0.2 only)
  context-loss rate       context_loss captures / all captures
  handoff rate            handoff captures / all captures
  marker rate             minimum-viable entries / all captures
  boundary mix            share of captures at each use boundary
Envelope 0.1 captures count toward the rates but have no timing.
Withdrawn captures are gone from raw and are not counted.

Usage:
  python3 tools/capture_metrics.py RAW_DIR [--target-s 10]
Stdlib only.
"""
import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path


def load(raw_dir: Path):
    rows = []
    for path in sorted(raw_dir.glob("m-*.json")):
        rows.append(json.loads(path.read_bytes().decode("utf-8")))
    return rows


def share(k, n):
    return round(k / n, 3) if n else None


def metrics(rows, target_s=10.0):
    n = len(rows)
    types = Counter(r.get("capture_type") for r in rows)
    timed = [r["capture_seconds"] for r in rows if "capture_seconds" in r]
    boundaries = Counter(r.get("boundary", "not recorded (envelope 0.1)") for r in rows)
    return {
        "captures": n,
        "timed_captures": len(timed),
        "median_capture_seconds": round(statistics.median(timed), 1) if timed else None,
        "share_within_target": share(sum(t <= target_s for t in timed), len(timed)),
        "target_seconds": target_s,
        "context_loss_rate": share(types["context_loss"], n),
        "handoff_rate": share(types["handoff"], n),
        "marker_rate": share(types["marker"], n),
        "boundary_mix": {b: share(k, n) for b, k in boundaries.most_common()},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("raw", type=Path)
    ap.add_argument("--target-s", type=float, default=10.0)
    args = ap.parse_args(argv)
    if not args.raw.is_dir():
        print(f"[!] {args.raw} is not a folder", file=sys.stderr)
        return 2
    print(json.dumps(metrics(load(args.raw), args.target_s), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
