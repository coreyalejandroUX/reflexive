#!/usr/bin/env python3
"""
policy_gate.py: the deterministic part of Reflexive's refusal rules on the
mobile path.

The four refusals the grant names are:
    missing source        -> HOLD   (ASK first, when nothing was named)
    invent lost text      -> REFUSE
    publish identity      -> ESCALATE
    generalize to all     -> REFUSE

Two of these can be checked from fields alone, and so must never depend on a
language model's judgment: missing source, and anything that releases or
shares data. This gate checks those, and the mobile rules around them.
Semantic cases (is this sentence an over-generalization? is this text
invented?) are the agent's job and are red-teamed in study/redteam/.

Decisions use the companion checkpoint's words (shared schema,
$defs/route_decision): SAVE, ASK, HOLD, REFUSE, ESCALATE.

A request is a dict:
    {"action": "code" | "memo" | "review" | "promote" | "relabel"
               | "widen_boundary" | "export" | "share",
     "device": "phone" | "desktop",
     "evidence_ids": [...],             # raw/evidence items the action rests on
     "evidence_present": [...],         # subset that actually exists and hash-checks
     "from_fidelity": ..., "to_fidelity": ...,   # relabel only
     "boundary": ...,                   # the record's use boundary (export/share)
     "to_boundary": ...,                # widen_boundary only
     "text": "...",                     # payload that would leave the system
     "human_confirmed": bool,           # an interactive human decision, not automation
     "includes_open_study_block": bool} # release candidate holds items reviewed in an
                                        # unclosed study block (seeded or not; blinding
                                        # means nobody can tell which)

decide(request, watchlist) returns (decision, rule, reason). Stdlib only.
"""
import re

RELEASE_ACTIONS = {"export", "share"}
EVIDENCE_ACTIONS = {"code", "memo", "review", "promote", "export"}
RELEASABLE_BOUNDARIES = {"deidentified_study_record", "public_release_requested"}

# Moving a label up this ladder claims more than the evidence supports. The
# labels themselves come from the shared schema; tests check the two agree.
FIDELITY_RANK = {"reconstruction": 0, "user-supplied": 1, "transcription": 2, "direct": 3}


def decide(req: dict, watchlist=()):
    action = req.get("action")
    device = req.get("device")

    if device not in ("phone", "desktop"):
        return "HOLD", "device", "unknown device; cannot apply the right rules"

    if action == "widen_boundary":
        if device == "phone":
            return "ESCALATE", "boundary-desktop-only", "widen the use boundary at the desk"
        if req.get("to_boundary") == "public_release_requested":
            return "ESCALATE", "publish-identity", \
                "check identifiers, consent, copyright and redaction before any release"
        if not req.get("human_confirmed"):
            return "ESCALATE", "boundary-needs-human", "a boundary change needs an interactive human decision"
        return "SAVE", "", ""

    if action in RELEASE_ACTIONS:
        if device == "phone":
            return "ESCALATE", "release-desktop-only", \
                "release and sharing are desktop-only; queued for the desk"
        if req.get("includes_open_study_block"):
            return "HOLD", "study-block-open", \
                "items from an open study block are not releasable until unblinding and re-review"
        if req.get("boundary") not in RELEASABLE_BOUNDARIES:
            return "HOLD", "boundary", "the record's use boundary does not allow release"
        if not req.get("human_confirmed"):
            return "ESCALATE", "release-needs-human", "release needs an interactive human decision"
        text = req.get("text", "")
        for name in watchlist:
            if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
                return "ESCALATE", "publish-identity", "payload contains an identity"

    if action in EVIDENCE_ACTIONS:
        ids = req.get("evidence_ids") or []
        present = set(req.get("evidence_present") or [])
        if not ids:
            if action == "promote":
                return "HOLD", "missing-source", "no source to inspect; it stays provisional"
            return "ASK", "missing-source", "attach or name at least one source first"
        missing = [i for i in ids if i not in present]
        if missing:
            return "HOLD", "missing-source", f"evidence not found or hash mismatch: {missing}"

    if action == "relabel":
        before = FIDELITY_RANK.get(req.get("from_fidelity"))
        after = FIDELITY_RANK.get(req.get("to_fidelity"))
        if before is None or after is None:
            return "HOLD", "fidelity", "unknown fidelity label"
        if after > before:
            return "REFUSE", "invent-lost-text", \
                "a label can only move toward lower fidelity; upgrading it launders a reconstruction"

    if action == "review" and not req.get("human_confirmed"):
        return "HOLD", "review-needs-human", "a review decision must come from an interactive human step"

    return "SAVE", "", ""
