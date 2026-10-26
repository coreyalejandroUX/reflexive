# Reflexive: iPhone layer

The mobile layer of **Reflexive**, a governed agentic workflow for researcher-as-subject inquiry. It does two things:

1. **A tool.** Capture by voice in under 10 seconds, offline, de-identified, into the raw layer of the Reflexive corpus. Review on the phone.
2. **A study.** It asks whether human oversight of a governed agent stays meaningful on a small screen, with low attention, on the move. It is measured with planted errors under commit-reveal blinding.

**Read first:** [docs/iphone/00_index.md](docs/iphone/00_index.md)

## What is here

```
schema/
  reflexive.schema.json the single source of truth
  reflexive_schema.py   Python reader (stdlib)
  typescript/           TypeScript reader (Ajv)
  fixtures.json         cases both must agree on
mobile/
  ingest.py             inbox → raw: the only door
  withdraw.py           the one sanctioned removal
  policy_gate.py        deterministic refusals
study/
  seal.py               hidden seeding, commit-reveal
  review_desk.py        desktop review, logged
  measures.py           catch, escape, rubber-stamp
  redteam/              24 attacks on 4 rules
tools/
  fidelity_report.py    read-only label counts
tests/                  58 tests (stdlib unittest)
docs/iphone/            the design, 1 file per part
```

```
python3 -m unittest discover -s tests          # Python kit
cd schema/typescript && npm install && npm test  # TypeScript reader
```

The Python kit uses only the standard library.

## Which part does what

| Part | Language | Job | Does not |
|---|---|---|---|
| **Shared schema** (`schema/reflexive.schema.json`) | JSON Schema 2020-12 | Defines every format the two sides exchange: phone envelope, review item, review decision, fidelity labels | Hold data. It changes only by a versioned proposal (docs/iphone/07_schema.md). |
| **Research kit** (this repo) | Python | Ingest into raw, refusal gate, seeding and sealing, study measures, red-team runs, corpus reports | Draw interfaces, or rewrite the corpus |
| **TypeScript workspace** (separate) | TypeScript | The interface and the demo | Redefine formats. It imports `schema/typescript/validate.ts`, which reads the same schema file. |

Neither side copies the schema's rules into its own code. Python reads the file through `schema/reflexive_schema.py`; TypeScript reads it through Ajv. `schema/fixtures.json` lists cases with a known answer, and both test suites must get every one right. If the two readers disagree, a test fails before the formats can drift apart.

## What is not here

This repository is **public**. It holds code and design only. The research corpus (raw, evidence, record, derived and release layers), the inbox, the sealed key and the de-identification watchlist live elsewhere, in private. `.gitignore` blocks them.

See [VERIFICATION_AND_TRUTH.md](VERIFICATION_AND_TRUTH.md) for what is and is not claimed.
