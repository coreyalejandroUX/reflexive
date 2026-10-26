# 5. Timeline to pilot evidence by November 12

Today is Monday, October 26. Each row is one deliverable. A row without a check-box outcome is not finished.

```
 OCT 26 ─ 29   PHASE 0   capture + baseline
 OCT 30 ─ 31   PHASE 1   seal, pre-register
 OCT 31 ─ NOV 10  BLOCK  seeded review
 NOV 11        UNBLIND   reveal, re-review
 NOV 12        EVIDENCE  pilot packet
```

| Date | Work | Done when |
|---|---|---|
| **Mon Oct 26** | Build the Note shortcut. Privacy settings. Airplane test. | One marker saved offline. |
| **Tue Oct 27** | Bus: real captures. Evening: first `ingest.py` run. | ≥ 1 PRESERVED. |
| **Wed Oct 28** | Push automation. Check shortcut. Ten baseline review items, split across devices. | Decisions logged on both devices. |
| **Thu Oct 29** | Phase 0 check (four boxes in [03_phase0.md](03_phase0.md)). Send the ethics/IRB determination update describing seeding. Ask the escrow person. | Phase 0 running. Determination request sent. |
| **Fri Oct 30** | Seeding environment: secret, commitment, GitHub Action, escrow key. Run the red-team suite on the live agent (the first of two runs). **File the OSF pre-registration.** | Commitment hash and `measures.py` commit appear in the filed pre-registration. Red-team run 1 logged. |
| **Sat Oct 31** | Seeded block opens. | First seeded queue generated. |
| **Oct 31 – Nov 10** | Normal life: capture whenever, review when able. Stop rule always on. Pause whenever. | No daily target. Coverage is measured, not demanded. |
| **Sun Nov 8** | Halfway: run `measures.py` on **decision validity only**, with no key (catches broken logs early). Red-team run 2. | Logs valid. Run 2 logged. |
| **Tue Nov 10** | Block closes at midnight. | No new seeded items. |
| **Wed Nov 11** | Escrow decrypts the key. Verify the commitment. Run `measures.py`. Natural-escape audit (20 items). Re-review clean twins at the desk. Staging moves to derived. Debrief with the escrow person. | Measures JSON saved. Commitment verified. Staging empty. |
| **Thu Nov 12** | Pilot evidence packet (below). | Packet committed. |

## The November 12 pilot evidence packet

1. `results/measures.json`, the full output with intervals.
2. `results/redteam.jsonl`, both runs, with breaks highlighted. Any break is reported along with its fix.
3. A one-page joint display: numbers next to excerpts from your session notes.
4. A V&T ledger (EXISTS / VERIFIED AGAINST / NOT CLAIMED), in the style of your June repo.
5. Deviations from the pre-registration, each one dated.
6. The sample-size estimate for the follow-up, from the pilot's observed spread.

## If the dates slip

- **Seeding starts late:** shorten the block. Do not move November 12. Report the block length you actually ran.
- **The determination is not back by October 31:** run the block **without seeding** (device randomization only: time, rubber-stamping, coverage). Seed after it arrives. The packet then reports H2, H3 and H5 fully, and H1 and H4 as "instrument ready, not run".
- **A bad week:** see [09_risks.md](09_risks.md). Pausing is part of the protocol, not a deviation.
