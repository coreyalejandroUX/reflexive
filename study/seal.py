#!/usr/bin/env python3
"""
seal.py: hidden seeding and device assignment for the oversight study.

Everything here is driven by one secret that the participant does not hold.
Commit-reveal keeps it honest:

  1. Before the study, the seeding environment generates a secret and publishes
     only its commitment, sha256(secret), in the OSF pre-registration.
  2. During the study, for each review item, the environment computes
       rate     the hidden seed rate, drawn once from [RATE_LOW, RATE_HIGH]
       seeded   whether this item gets a planted error
       kind     unsupported_claim or wrong_code
       device   phone or desktop queue (not secret; it is visible by design)
     and writes the key to the sealed log, encrypted to the escrow holder.
  3. At unblinding, the secret is revealed. Anyone can check it against the
     commitment and recompute every decision. A changed key cannot pass.

The participant knows the rate range, never the realized rate or which items.

Usage:
  python3 study/seal.py commit SECRET_FILE
  python3 study/seal.py key SECRET_FILE ITEMS_FILE     # one item_id per line; prints JSONL
  python3 study/seal.py verify SECRET_FILE COMMITMENT
Pipe "key" output straight into an encryption tool (for example `age -r <escrow key>`)
so the plaintext key never sits on disk. Stdlib only.
"""
import hashlib
import hmac
import json
import sys

RATE_LOW, RATE_HIGH = 0.10, 0.25
SEED_KINDS = ("unsupported_claim", "wrong_code")


def commitment(secret: bytes) -> str:
    return hashlib.sha256(secret).hexdigest()


def _uniform(secret: bytes, label: str) -> float:
    """A reproducible number in [0, 1) from the secret and a label."""
    digest = hmac.new(secret, label.encode("utf-8"), hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64


def seed_rate(secret: bytes) -> float:
    return RATE_LOW + (RATE_HIGH - RATE_LOW) * _uniform(secret, "rate")


def decide(secret: bytes, item_id: str) -> dict:
    seeded = _uniform(secret, f"seed:{item_id}") < seed_rate(secret)
    kind = SEED_KINDS[int(_uniform(secret, f"kind:{item_id}") * len(SEED_KINDS))] if seeded else None
    device = "phone" if _uniform(secret, f"device:{item_id}") < 0.5 else "desktop"
    return {"item_id": item_id, "seeded": seeded, "seed_kind": kind, "device": device}


def verify(secret: bytes, published: str) -> bool:
    return hmac.compare_digest(commitment(secret), published.strip().lower())


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2 or argv[0] not in ("commit", "key", "verify"):
        print(__doc__)
        return 2
    with open(argv[1], "rb") as f:
        secret = f.read().strip()
    if len(secret) < 32:
        print("[!] secret must be at least 32 bytes", file=sys.stderr)
        return 2
    if argv[0] == "commit":
        print(commitment(secret))
    elif argv[0] == "key":
        with open(argv[2], encoding="utf-8") as f:
            for item_id in (line.strip() for line in f):
                if item_id:
                    print(json.dumps(decide(secret, item_id)))
    else:
        ok = verify(secret, argv[2])
        print("commitment matches" if ok else "COMMITMENT DOES NOT MATCH")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
