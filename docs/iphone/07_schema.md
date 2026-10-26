# 7. Schema mapping and versioned proposals

Three namespaces. Keeping them apart is how seeding stays out of the corpus.

All three are defined in **one file**, `schema/reflexive.schema.json`. That file is the single source of truth. The Python kit reads it through `schema/reflexive_schema.py`, and the TypeScript workspace reads it through `schema/typescript/validate.ts` (Ajv). Both must give the same verdict on every case in `schema/fixtures.json`. Each side has a test for that.

```
 ENVELOPE 0.1      phone → inbox
 ($defs/mobile_envelope)
        │ ingest.py
        ▼
 CORPUS 2.1 → 2.2  raw → … → release
 (your schema; proposal below)

 STUDY 1.0         decisions, queue,
 (study/…)         sealed key
                   never inside the corpus
```

- The envelope IS: the phone's transport format, deliberately tiny. It IS NOT: a schema 2.1 record. The Structure step makes records from raw.
- Study 1.0 IS: the oversight experiment's own data. It IS NOT: part of the corpus, so it can never be released by Export.

## Envelope 0.1 → schema 2.1

I could not read schema 2.1 (conflict C1), so every field name on the right must be **confirmed** against your schema file before Structure maps automatically.

| Envelope field | Schema 2.1 concept | Confirm |
|---|---|---|
| `capture_id` | capture or record id | name, and whether ids are reused |
| `captured_at` | capture timestamp | timezone convention |
| `device` = `iphone` | device context | allowed values |
| `capture_type` | capture or episode type | whether `context_loss`, `handoff` and `marker` exist (proposal P1) |
| `fidelity` | fidelity label | same four values (yes, per the application) |
| `text` | user-supplied content | field for researcher-authored text |
| `text_method` | none known | proposal P2 |
| `text_sha256` | evidence hash | algorithm used in the evidence layer |
| `attachment_file`, `attachment_sha256` | source file and hash | path convention |
| `minutes_since_event` | none known | proposal P3 |
| (absent) app, URL, task | context fields | stay `unknown` from the phone |

## Proposal P: schema 2.2 (corpus)

Additive only. Every 2.1 record stays valid as 2.2. Status: **proposed**, not adopted. Adoption needs your approval, which, per the application, a codebook or schema change always does.

| # | Field | Type | Why |
|---|---|---|---|
| P1 | `capture_type` adds `context_loss`, `handoff`, `marker` | enum | the two first-class mobile types, plus the minimum-viable entry |
| P2 | `text_method` | `dictation` / `typed` / `none` / `ocr` | keeps how text was produced separate from the fidelity label (conflict C5) |
| P3 | `minutes_since_event` | number or `unknown` | the gap between event and capture; feeds the context-loss rate |
| P4 | `capture_surface` | `phone` / `desktop` / `browser` | where Preserve ran, distinct from where the event happened |
| P5 | `links` | list of `{rel, target_id}` with `rel` in `handoff_of`, `marker_for`, `correction_of`, `reconstruction_of` | connects a handoff pair, a marker to its later note, and a correction to the capture it corrects, without editing raw |
| P6 | `deid` | `{method, replacements}` | records that de-identification ran at capture and how many swaps it made, not what was swapped |

**Migration:** none needed. Readers of 2.1 ignore the new fields. Structure writes 2.2 for new mobile captures only.

## Proposal P7: two fidelity questions, two fields (status: proposed)

The grant and the companion checkpoint use the word "fidelity" for two different questions:

```
 fidelity (2.1, unchanged)   support (2.2, proposed)
 HOW was it captured?        HOW WELL is it backed?
 ──────────────────────      ──────────────────────
 direct                      corroborated
 user-supplied               documented
 transcription               no_source
 reconstruction              unknown
 set once, at Preserve       recomputed when sources
 lives in raw/record         are attached; derived
```

- `fidelity` IS: a fact about the capture event, fixed at Preserve. It IS NOT: a rating of how trustworthy the content is.
- `support` IS: a revisable judgment of how many independent sources back the record. It IS NOT: stored in raw, and it IS NOT written back into any existing capture.
- `corroborated`: two or more independent source kinds (for example transcript plus screenshot). `documented`: at least one source. `no_source`: nothing attached. `unknown`: not yet checked.
- **Naming decision for you:** the checkpoint shows `no_source` as "Reconstruction only". In storage I propose `no_source`, because a user-supplied account with nothing attached is not a reconstruction. The display text can stay as it is.

**Migration note (P7):**
1. **No existing capture is rewritten or relabeled.** All 68 stay byte-identical, and the raw manifest proves it.
2. First, run `python3 tools/fidelity_report.py <corpus> --expect 68`. It is read-only and reports which values the captures actually carry, exactly as written.
3. If some existing records hold checkpoint-style values ("Corroborated…") in their `fidelity` field, they keep them. A 2.2 reader shows those records with `fidelity: unknown (not recorded as a capture method)`, and reads the stored value as `support` in a derived view only.
4. Any per-record correction is a new derived annotation with your decision logged. It is never an edit.
5. On adoption: shared schema `x-version` goes 1.0.0 → 1.1.0, and the corpus schema goes 2.1 → 2.2. The `x-status: proposed` marker comes off `support_strength`, in one commit that only you approve.

**Not proposed, on purpose:** any state or energy field. The check-in belongs to the study session, not to the evidence.

## Study 1.0 (separate namespace)

**Review item** (`review/queue.jsonl`, written by the seeding environment):

```
item_id     opaque; same shape whether seeded or not
queue       phone | desktop
evidence    ≤ 60 words, from the evidence layer
claim       the agent's proposal (claim or code)
item_words  word count of evidence + claim
record_ref  the 2.1 record it is about
```

**Decision** (`study/decisions/...`, validated by `measures.validate_decision`):

```
decision_id   session_id    item_id
device        presented_at  decided_at
dwell_ms      outcome       item_words
interrupted
```

**Session** (one per review session):

```
session_id  device   started_at  ended_at
end_reason  energy   setting     paused
```

`end_reason` is one of: items, time, unsure_run, reopen, chosen. Energy and setting may be `skip`.

**Sealed key row** (encrypted, escrow only): `item_id`, `seeded`, `seed_kind`, `device`.

**Red-team result** (`study/redteam/results.jsonl`): `at`, `id`, `rule`, `channel`, `gate`, `expected`, `actual`, `outcome`, `agent`.

Only the decision, item and key formats are fixed in code. Session rows are specified here and logged by the Check shortcut; `review_desk.py` does not write them yet.
