# 7. Schema mapping and versioned proposals

Three namespaces. Keeping them apart is how seeding stays out of the corpus.

```
 ENVELOPE 0.1      phone → inbox
 (mobile/envelope.schema.json)
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
