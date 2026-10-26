#!/usr/bin/env python3
"""
agreement.py: inter-reviewer agreement on a shared sample of review items.

The grant lists inter-reviewer agreement as an outcome metric. With one
participant, it comes from a second reviewer (the independent coder in the
budget) deciding the same items: for example, the 20-item audit sample at
unblinding. Each reviewer's decisions are a decisions.jsonl file in the
shared-schema format. Only items both decided (not "stopped") are compared.

Reports, each with the number of items compared:
  percent agreement and Cohen's kappa on the four outcomes
    (approve, narrow, hold, reject)
  the same for the binary question that matters for escapes:
    approve vs not approve

Kappa on a 20-item sample is unstable. Report it with the item count, never alone.

Usage:
  python3 study/agreement.py REVIEWER_A.jsonl REVIEWER_B.jsonl
Stdlib only.
"""
import json
import sys
from collections import Counter

DECIDED = ("approve", "narrow", "hold", "reject")


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def paired(rows_a, rows_b):
    last_a = {r["item_id"]: r["outcome"] for r in rows_a if r["outcome"] in DECIDED}
    last_b = {r["item_id"]: r["outcome"] for r in rows_b if r["outcome"] in DECIDED}
    shared = sorted(set(last_a) & set(last_b))
    return [last_a[i] for i in shared], [last_b[i] for i in shared]


def summary(a, b):
    def block(x, y):
        k = cohen_kappa(x, y)
        return {"items": len(x),
                "percent_agreement": round(sum(p == q for p, q in zip(x, y)) / len(x), 3) if x else None,
                "kappa": round(k, 3) if k is not None else None}
    return {"four_outcomes": block(a, b),
            "approve_vs_not": block([o == "approve" for o in a], [o == "approve" for o in b])}


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    a, b = paired(read_jsonl(argv[0]), read_jsonl(argv[1]))
    print(json.dumps(summary(a, b), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
