# 2. Where each step runs

Three places:
- **Phone:** you, on the bus, low attention.
- **Agent:** the governed model plus the deterministic scripts, with no human present.
- **Desktop:** you, at a desk, full attention.

| Step | Runs on | Why there |
|---|---|---|
| 1 Preserve | **Phone** (and desktop browser, as today) | The moment happens away from the desk. Capture must not wait for one. Offline, under 10 s. |
| 2 Structure | **Agent** | Segmenting into schema 2.1 episodes needs the corpus and the controlled vocabulary, and no human attention. Unknowns stay `unknown`. |
| 3 Check | **Agent**, with two small checks on the **phone** | The phone does the two checks that must happen before saving: swap known names, and attach a fidelity label. Everything else (duplicates, sampling balance, sensitivity, consent, contradictions) runs in the agent. |
| 4 Interpret | **Agent** (provisional) | Proposals are drafts. The phone never generates interpretations: no model output appears on the phone unless it is queued for review. |
| 5 Review | **Phone or desktop** | Both are allowed. In the study, each item is randomly assigned to one of them. Edits, codebook changes and hypothesis changes are **desktop only**. |
| 6 Synthesize | **Agent** | Reads only the derived layer, never staging, never seeds. |
| 7 Export | **Desktop**, you release | Release is the highest-stakes step, so it gets the highest-attention setting. The phone **cannot** export or share. The gate returns ESCALATE ("queued for the desk"). |

## The rule behind the table

This diagram defines **attention-matched authority**. The more a decision costs if wrong, the more attention its location must have.

```
 COST IF WRONG     WHERE IT MAY HAPPEN
 -------------     -------------------
 low   capture     phone, agent, desk
   |   mark        phone, desk
   |   review      phone, desk
   |   edit/code   desk
   v   release     desk + gate
 high  identity    desk + gate + you,
                   ESCALATE only
```

- It IS: a hard rule in `mobile/policy_gate.py`, tested.
- It IS NOT: a guess that phones are bad. Whether phone review is good enough is the question the study measures. Release stays on the desk even if the answer is "yes", because one escaped identity cannot be undone.

## What crosses between places

```
 PHONE                    AGENT / DESK
 ─────                    ────────────
 envelope ──transit──▶ ingest.py
 (de-identified,          │ PRESERVED
  labeled, hashed)        ▼
                         raw ─▶ evidence
                          ─▶ record (2.1)
                          ─▶ proposals
                               │
 review card ◀─ queue ─────────┘
   (claim + evidence,
    ≤ 60 words)
 decision ──transit──▶ study/decisions
                       derived-staging
                       ─▶ derived
                          (after unblind)
                       ─▶ release (desk)
```

Read the arrows as the only allowed paths. In particular:
- **No arrow** goes from the study (seeds, sealed log) into raw. `ingest.py` refuses any envelope with study fields.
- **No arrow** goes from staging to release. The gate holds any release that includes an open study block.
- **No arrow** goes from phone to release.

## Later: the native app (after November 12)

Phase 0 uses Shortcuts. If the pilot shows phone review is worth keeping, a native SwiftUI app replaces Shortcuts with:
- on-device speech (`requiresOnDeviceRecognition`), so nothing goes to a server;
- on-device name detection (NaturalLanguage `NLTagger`, person and organization names) on top of the watchlist;
- complete data protection, so files are unreadable while the phone is locked;
- real interruption detection (scene phase), so an app switch during review is logged as an interruption, and as a context-loss capture;
- an App Intent for the Action Button, no notifications at all, and no widgets that show content.

That app is **not** needed for the pilot, and nothing in the pilot depends on it.
