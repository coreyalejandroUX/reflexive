# 7. Schema mapping and versioned proposals

Three namespaces. Keeping them apart is how seeding stays out of the corpus.

All three are defined in **one file**, `schema/reflexive.schema.json`. That file is the single source of truth. The Python kit reads it through `schema/reflexive_schema.py`, and the TypeScript workspace reads it through `schema/typescript/validate.ts` (Ajv). Both must give the same verdict on every case in `schema/fixtures.json`. Each side has a test for that.

```
 ENVELOPE 0.2      phone → inbox
 (0.1 frozen,      still accepted)
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

## Envelope 0.2 (current)

Shared schema 1.1.0 adds two required fields to what the phone writes. Envelope 0.1 stays valid and frozen (`$defs/mobile_envelope_0_1`), so nothing already captured is lost.

| New field | Values | Why |
|---|---|---|
| `boundary` | `private_research_only` or `unclear` from the phone; the desk may widen to `deidentified_study_record` or `public_release_requested` | Who may use the record. This is the companion checkpoint's use boundary. Narrowest by default, widened only with attention. |
| `capture_seconds` | number | Time from pressing the button to saving. It measures the 10-second target and the grant's attention-per-capture metric. |

## Envelope → schema 2.1 (companion checkpoint field names)

The companion checkpoint builds a record named `reflexive-checkpoint/2.1`. Its field names are the best evidence of schema 2.1 I can reach. They are still a demo, so each needs confirming against the corpus.

| Envelope field | Checkpoint 2.1 field | Confirm |
|---|---|---|
| `capture_id` | `id` (format `RF-YYYYMMDD-NNNN`) | whether the corpus uses the RF format; mobile ids keep their own `m-` form and link to it |
| `captured_at` | `captured_at` | timezone convention |
| `minutes_since_event` | `event_time` ("Not established by this capture" when unknown) | how unknown is written |
| `text` | `event` | |
| (Structure proposes) | `impact` (Friction / Breakdown / Breakthrough / Neutral observation) | the phone does not ask; see "Sampling balance" below |
| `attachment_file` | `evidence` (list of source kinds) | |
| `fidelity` | `fidelity` | **conflict:** the checkpoint stores support strength here (proposal P7) |
| `boundary` | `boundary` | display text vs stored value (`x-display` in the shared schema) |
| (absent) app, URL, task | `context` | stays "Context not recorded" from the phone |
| `text_sha256` | `sha256` | the checkpoint hashes event plus context, not text alone |
| (gate result) | `route`, `route_reason` | same words now: SAVE / ASK / HOLD / REFUSE / ESCALATE |
| (policy version) | `rule_set` | |

**Sampling balance.** Phone captures lean toward friction (context loss, handoff). The phone does not ask for an impact label, because that would break the 10-second budget. Structure proposes `impact`, and Check reports the balance of smooth, friction, breakthrough and baseline episodes **separately for each capture surface**, so a phone-heavy week shows up as skew rather than as a finding.

## Envelope 0.1 → schema 2.1 (earlier mapping)

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
- **Decided (October 26):** the stored value is `no_source`, displayed as "Reconstruction only". A user-supplied account with nothing attached is not a reconstruction, so storage keeps the two apart. The display mapping lives in the shared schema (`x-display`), so both the Python kit and the TypeScript workspace show the same text.

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
agent_action_id  the agent action that
                 proposed it (PROV join)
model            which model proposed it
policy_version   which rule set applied
confidence       0–1, or "unknown"
```

The last four come from the application's provenance promise: every action logs its input, policy version, model, output, confidence and the human's decision. They also let the study ask whether the agent's stated confidence predicts which errors escape.

**Decision** (`study/decisions/...`, validated by `measures.validate_decision`):

```
decision_id   session_id    item_id
agent_action_id               device
presented_at  decided_at    dwell_ms
outcome       item_words    interrupted
```

`outcome` is one of `approve`, `narrow`, `hold`, `reject`, `stopped`.

**Withdrawal** (`raw/mobile/WITHDRAWN.jsonl`, `$defs/withdrawal`): `capture_id`, `sha256`, `withdrawn_at`, and a `reason` code (`participant_choice`, `consent_change`, `identity_risk`, `other`). It holds no content and no free text.

**Session** (one per review session):

```
session_id  device   started_at  ended_at
end_reason  energy   setting     paused
```

`end_reason` is one of: items, time, hold_run, reopen, chosen. Energy and setting may be `skip`.

**Sealed key row** (encrypted, escrow only): `item_id`, `seeded`, `seed_kind`, `device`.

**Red-team result** (`study/redteam/results.jsonl`): `at`, `id`, `rule`, `channel`, `gate`, `expected`, `actual`, `outcome`, `agent`.

Only the decision, item and key formats are fixed in code. Session rows are specified here and logged by the Check shortcut; `review_desk.py` does not write them yet.
