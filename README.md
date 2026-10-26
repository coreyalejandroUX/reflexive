# Reflexive: iPhone layer

The mobile layer of **Reflexive**, a governed agentic workflow for researcher-as-subject inquiry. It does two things:

1. **A tool.** Capture by voice in under 10 seconds, offline, de-identified, into the raw layer of the Reflexive corpus. Review on the phone.
2. **A study.** It asks whether human oversight of a governed agent stays meaningful on a small screen, with low attention, on the move. It is measured with planted errors under commit-reveal blinding.

**Read first:** [docs/iphone/00_index.md](docs/iphone/00_index.md)

## What is here

```
mobile/
  envelope.schema.json  what the phone writes (v0.1)
  ingest.py             inbox → raw: the only door
  policy_gate.py        deterministic refusals
study/
  seal.py               hidden seeding, commit-reveal
  review_desk.py        desktop review, logged
  measures.py           catch, escape, rubber-stamp
  redteam/              24 attacks on 4 rules
tests/                  36 tests (stdlib unittest)
docs/iphone/            the design, 1 file per part
```

```
python3 -m unittest discover -s tests
```

Python 3, standard library only.

## What is not here

This repository is **public**. It holds code and design only. The research corpus (raw, evidence, record, derived and release layers), the inbox, the sealed key and the de-identification watchlist live elsewhere, in private. `.gitignore` blocks them.

See [VERIFICATION_AND_TRUTH.md](VERIFICATION_AND_TRUTH.md) for what is and is not claimed.
