#!/usr/bin/env python3
"""
ingest.py: move iPhone capture envelopes from the inbox into the raw layer.

The phone (Phase 0: an Apple Shortcut writing through Working Copy) drops one
JSON envelope per capture into an inbox folder in the private corpus repo.
This script is the only door from that inbox into raw. For each envelope it
returns one decision:

    PRESERVED   written to raw, hash added to the manifest
    DUPLICATE   already in raw with identical bytes (safe offline replay)
    HOLD        not written; a person must look (reason given)
    REFUSE      not written; this must never enter raw (reason given)

Field rules come from the shared schema (schema/reflexive.schema.json,
$defs/mobile_envelope). Rules enforced here (see docs/iphone/08_tests.md):
  - raw is append-only: an existing raw file is never overwritten
  - text_sha256 must match the text (evidence integrity)
  - a referenced attachment must exist and match its hash (missing source -> HOLD)
  - the fidelity label must be allowed for the capture type
  - study or seeding fields may never appear in a raw envelope (-> REFUSE)
  - a watchlist name in the text means de-identification failed (-> HOLD)

Usage:
    python3 mobile/ingest.py --inbox PATH --raw PATH [--watchlist FILE] [--dry-run]

Exit code 0 when everything was PRESERVED or DUPLICATE, 2 if anything was held
or refused. Stdlib only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "schema"))
from reflexive_schema import definition, validate  # noqa: E402

# Which fidelity labels a phone capture may carry, from the shared schema. A
# voice or typed account is user-supplied; rebuilding lost content from memory
# is a reconstruction; "direct" needs an attached source file.
ALLOWED_FIDELITY = {k: set(v) for k, v in definition("mobile_envelope")["x-allowed-fidelity"].items()}

# Any key that smells like the oversight study. Seeding lives in study/, never raw.
FORBIDDEN_KEY = re.compile(r"seed|sealed|planted|study|experiment", re.IGNORECASE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_watchlist(path):
    if not path:
        return []
    names = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("=>")[0].strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


def all_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from all_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from all_keys(v)


def check(env: dict, inbox: Path, watchlist):
    """Return (decision, reason). decision is None when the envelope may be preserved."""
    bad = [k for k in all_keys(env) if FORBIDDEN_KEY.search(k)]
    if bad:
        return "REFUSE", f"study field(s) {sorted(set(bad))} may not enter raw"

    problems = validate(env, "mobile_envelope")
    if problems:
        hint = "; propose a schema change first" if any("unknown field" in p for p in problems) else ""
        return "HOLD", "does not match the shared schema: " + "; ".join(problems) + hint
    if env["fidelity"] not in ALLOWED_FIDELITY[env["capture_type"]]:
        return "HOLD", (f"fidelity {env['fidelity']!r} is not allowed for "
                        f"{env['capture_type']!r} captures")
    if env["capture_type"] == "marker" and env["text"].strip():
        return "HOLD", "a marker carries no text; save it as a moment instead"
    if env["fidelity"] == "direct" and "attachment_file" not in env:
        return "HOLD", "'direct' needs an attached source file"

    if sha256_bytes(env["text"].encode("utf-8")) != env["text_sha256"]:
        return "HOLD", "text_sha256 does not match the text"

    if "attachment_file" in env:
        if Path(env["attachment_file"]).name != env["attachment_file"]:
            return "REFUSE", "attachment_file must be a bare file name in the inbox"
        att = inbox / env["attachment_file"]
        if not att.is_file():
            return "HOLD", f"missing source: {env['attachment_file']} not found"
        if "attachment_sha256" in env and sha256_bytes(att.read_bytes()) != env["attachment_sha256"]:
            return "HOLD", "attachment_sha256 does not match the attachment"

    for name in watchlist:
        if re.search(rf"\b{re.escape(name)}\b", env["text"], re.IGNORECASE):
            return "HOLD", "possible identity in text; de-identify before preserving"

    return None, ""


def preserve(env_path: Path, raw_dir: Path, inbox: Path, watchlist, dry_run=False):
    data = env_path.read_bytes()
    try:
        env = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return "HOLD", f"not valid JSON: {e}"
    if not isinstance(env, dict):
        return "HOLD", "envelope must be a JSON object"

    decision, reason = check(env, inbox, watchlist)
    if decision:
        return decision, reason

    target = raw_dir / f"{env['capture_id']}.json"
    if target.exists():
        if target.read_bytes() == data:
            return "DUPLICATE", "already preserved with identical bytes"
        return "REFUSE", "raw is immutable: a different file with this capture_id exists"

    if dry_run:
        return "PRESERVED", "dry run, nothing written"

    raw_dir.mkdir(parents=True, exist_ok=True)
    # "x" mode fails rather than overwrite, even under a race.
    with open(target, "xb") as f:
        f.write(data)
    with open(raw_dir / "MANIFEST.sha256", "a", encoding="utf-8") as m:
        m.write(f"{sha256_bytes(data)}  {target.name}\n")
    return "PRESERVED", str(target)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--inbox", required=True, type=Path)
    ap.add_argument("--raw", required=True, type=Path,
                    help="raw-layer folder for mobile captures, e.g. corpus/raw/mobile")
    ap.add_argument("--watchlist", type=Path, help="names to keep out of raw, one per line")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    watchlist = load_watchlist(args.watchlist)
    worst = 0
    for env_path in sorted(args.inbox.glob("m-*.json")):
        decision, reason = preserve(env_path, args.raw, args.inbox, watchlist, args.dry_run)
        print(f"{decision:<9} {env_path.name}  {reason}")
        if decision in ("HOLD", "REFUSE"):
            worst = 2
    return worst


if __name__ == "__main__":
    sys.exit(main())
