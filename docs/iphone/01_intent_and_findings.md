# 1. Intent, what I found, assumptions, questions

## Your intent, restated

You want one iPhone layer that does two jobs at the same time.

1. **A tool.** You capture and review your autoethnography of Quantic's MS in AI Engineering from the bus, quickly, by voice, offline, without guilt, and without leaking anything sensitive. Captures land in your existing Reflexive corpus with full provenance.
2. **A study.** The phone becomes the test bed for an AI safety question: *when a governed agent proposes and a human approves, is that approval still meaningful on a small screen, with low attention, on the move?* You measure it by planting errors you cannot see and counting how many get through.

The tool must work even on days the study is paused. The study must never contaminate the tool's evidence.

## What I found

```
WHERE I LOOKED          WHAT WAS THERE
--------------------    ----------------------
GitHub                  empty: no commits,
coreyalejandroUX/       no branches
reflexive

Google Drive            Catalyst Grant
                        application, 2 versions
                        (Oct 5–6, 2026)

Google Drive            June 2026 protocol:
reflexive-ai-engineer   docs, templates,
-study.zip              6 scripts, no data
```

**From the application (treated as the source of truth):**
- Seven steps, five layers, four fidelity labels, and four tested refusals, exactly as your prompt states.
- Outcome metrics already named there: attention per capture (target under 2 minutes), context-loss rate, **unsupported-claim escape rate**, and **human review time**. The study operationalizes two metrics you already committed to. It does not add new ones.
- Autonomous: capture, validation, duplicates, sensitivity screening, provisional coding. Human: interpretation, codebook and hypothesis changes, identity disclosure, every external release.
- Pilot: 68 captures (52 platform interactions, 12 AI-workspace consultations, 4 derived artifacts), schema 2.1, 19 passing tests.

**From the June protocol** (an earlier design, still relevant):
- Its ethics plan: anonymize others at source, a faculty mentor, a peer debriefer, a pending IRB determination, and OSF pre-registration before data collection.
- Its data management plan: **no raw recordings to any cloud service, no unencrypted data on cloud storage.**
- Its style, which this kit copies: stdlib Python scripts and an honest "verification and truth" ledger.
- Its event-log schema is a CSV of instructional events. It is **not** schema 2.1.

## Conflicts I am flagging (not silently overriding)

| # | Conflict | What I did |
|---|---|---|
| C1 | You asked me to read the repository. It is empty, so I could not see schema 2.1, the 68 captures, the scripts, or the 19 tests. | Everything that touches schema 2.1 is marked **confirm** in [07_schema.md](07_schema.md). The phone writes its own small envelope (v0.1), and only `ingest.py` touches the corpus. |
| C2 | The June protocol forbids raw recordings in any cloud and unencrypted cloud data. A voice-first phone tool naturally creates audio and syncs it. | Phase 0 keeps **no audio**. Dictation becomes text on the phone, names are swapped before saving, and only de-identified text syncs. A private GitHub repo still needs a one-line amendment to the data management plan. See Question 3. |
| C3 | "Raw is immutable" against "de-identify at capture". If raw keeps the original, it holds names. If it does not, raw is not quite raw. | De-identification happens **before** preservation, so the identifiable version is never stored. Cost: you cannot re-check a dictation against the original words. This matches the June ethics rule (anonymize at source). Your call to keep it. |
| C4 | The application targets under 2 minutes per checkpoint. You asked for Preserve under 10 seconds. | No real conflict. The 10 seconds covers the phone step. Structure, Check and Interpret run later without you, and Review is a separate, bounded session. |
| C5 | In the application, `transcription` means text copied from a screenshot. Dictation is also a kind of transcription. | A spoken account is labeled `user-supplied`, with a separate `text_method: dictation`. `transcription` keeps its original meaning. |
| C6 | The application's Review is "accept, edit or reject". One-action-per-screen on a bus does not fit editing. | Phone Review uses the grant walkthrough's words: approve / ask for narrower / hold, plus reject and stop. Edits and codebook changes are desktop-only. "Hold" sends the item to the desk. |
| C7 | The June plan says IRB determination and OSF pre-registration must come before data collection. Seeding adds a planted-error element to your own pipeline. | Phase 0 (capture only) continues your existing study. **Seeding starts only after** the determination request is updated and the pre-registration is filed. See [05_timeline.md](05_timeline.md). |
| C8 | This GitHub repo is **public**. | It holds code and docs only. `.gitignore` blocks corpus, inbox, sealed and watchlist files. The corpus must live in a private repo. |

## Assumptions

1. An iPhone with an Action Button (15 Pro or later) or Back Tap, running iOS 17 or later, with on-device dictation in English.
2. Your corpus is a private Git repo with a `raw/` layer folder, and you have Python 3 on the desktop.
3. Schema 2.1 already has fields for id, time, app or source context, task, device, fidelity, capture or episode type, evidence hash, and an explicit "unknown" value.
4. The agent's Interpret step can output proposals as claim-plus-evidence pairs, each under 60 words.
5. You can review about 10–20 items on a good day, and fewer on a bad one.
6. One trusted person can hold a key: your faculty mentor or the peer debriefer from the June plan.
7. Phase 0 uses Apple Shortcuts plus the Working Copy Git app, not a custom app. A native app needs weeks, not three days.

## Questions (three)

1. **Where is the schema 2.1 corpus?** A repo name or path. If you add it to this session, I can replace every "confirm" in the schema mapping with the real field names and run your 19 tests against the new ingest step.
2. **Who can hold the sealed key?** Your mentor or peer debriefer? Without a second person, blinding rests on your promise alone. It stays tamper-evident, but it is weaker, and the paper has to say so.
3. **May de-identified text sync through a private GitHub repo?** That needs a one-line amendment to the data management plan. Or must it stay on your own devices? That option uses a home-network Git remote: the same Shortcuts, about an hour more setup.
