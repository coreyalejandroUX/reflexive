#!/usr/bin/env python3
"""
fidelity_report.py: count the fidelity labels the corpus actually carries.

Read-only. It opens every file for reading only, writes nothing, and never
normalizes a value: "User-supplied" and "user-supplied" are reported as two
different labels, because that difference is itself a finding.

It looks for a field (default: fidelity) at any depth in .json and .jsonl
files, and in "fidelity: value" lines in .md/.yml/.yaml front matter. Each
value is sorted into a family:
  grant        one of the four labels in the shared schema (capture method)
  checkpoint   Corroborated / Documented / Reconstruction only (support strength)
  other        anything else, listed so a person can decide

Usage:
  python3 tools/fidelity_report.py CORPUS_DIR [--field fidelity] [--expect 68] [--json]
Stdlib only.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "schema"))
from reflexive_schema import enum  # noqa: E402

GRANT = set(enum("fidelity"))
CHECKPOINT = re.compile(r"^(corroborated|documented|reconstruction only)\b", re.IGNORECASE)
RECORD_KEYS = {"id", "capture_id", "record_id", "episode_id"}
TEXT_SUFFIXES = {".md", ".yml", ".yaml"}


def family(value):
    if isinstance(value, str) and value in GRANT:
        return "grant"
    if isinstance(value, str) and CHECKPOINT.match(value.strip()):
        return "checkpoint"
    return "other"


def walk_json(obj, field, found, unlabeled):
    if isinstance(obj, dict):
        if field in obj:
            found.append(obj[field])
        elif RECORD_KEYS & obj.keys():
            unlabeled.append(obj.get("id") or obj.get("capture_id") or "?")
        for v in obj.values():
            walk_json(v, field, found, unlabeled)
    elif isinstance(obj, list):
        for v in obj:
            walk_json(v, field, found, unlabeled)


def scan(corpus: Path, field="fidelity"):
    values, per_file, unlabeled, unreadable = [], Counter(), [], []
    line_re = re.compile(rf"^\s*{re.escape(field)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    for path in sorted(p for p in corpus.rglob("*") if p.is_file() and ".git" not in p.parts):
        suffix = path.suffix.lower()
        if suffix not in {".json", ".jsonl"} | TEXT_SUFFIXES:
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            unreadable.append(str(path.relative_to(corpus)))
            continue
        found = []
        try:
            if suffix == ".json":
                walk_json(json.loads(text), field, found, unlabeled)
            elif suffix == ".jsonl":
                for line in text.splitlines():
                    if line.strip():
                        walk_json(json.loads(line), field, found, unlabeled)
            else:
                found = [v.strip("'\"") for v in line_re.findall(text)]
        except json.JSONDecodeError:
            unreadable.append(str(path.relative_to(corpus)))
            continue
        if found:
            per_file[str(path.relative_to(corpus))] += len(found)
        values.extend(found)

    counts = Counter(json.dumps(v) if not isinstance(v, str) else v for v in values)
    by_family = Counter()
    for v in values:
        by_family[family(v)] += 1
    return {
        "field": field,
        "labelled_values": len(values),
        "counts": dict(counts.most_common()),
        "by_family": dict(by_family),
        "other_values": sorted(k for k in counts if family(k) == "other"),
        "records_without_field": len(unlabeled),
        "files_with_labels": len(per_file),
        "unreadable_files": unreadable,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--field", default="fidelity")
    ap.add_argument("--expect", type=int, help="number of captures you expect, e.g. 68")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.corpus.is_dir():
        print(f"[!] {args.corpus} is not a folder", file=sys.stderr)
        return 2
    r = scan(args.corpus, args.field)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"'{r['field']}' values found: {r['labelled_values']} "
          f"in {r['files_with_labels']} file(s)")
    for label, n in r["counts"].items():
        print(f"  {n:>4}  {label}  [{family(label)}]")
    print(f"by family: {r['by_family']}")
    print(f"records with an id but no '{r['field']}': {r['records_without_field']}")
    if r["unreadable_files"]:
        print(f"unreadable (not counted): {r['unreadable_files']}")
    if args.expect is not None and r["labelled_values"] != args.expect:
        print(f"NOTE: expected {args.expect}, found {r['labelled_values']}. "
              "Derived artifacts or duplicates may explain the gap; check before quoting either number.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
