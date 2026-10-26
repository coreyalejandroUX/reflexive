# 12. Corrected grant-facing wording

Use these sentences in every application from now on, starting with the Generator Residency (due November 1). Each replaces a sentence that said more than the repository shows. **Confirm** marks a fact only you can check. Keep those words out of an application until you have.

## A. Refusals: demonstrated, then tested

**Decision:** change the wording now, and run the real tests on schedule.

| Option | Time | What it proves |
|---|---|---|
| Change the wording to "demonstration" | minutes (done here) | honesty about what exists today |
| Run the 15 agent attacks against ChatGPT/Codex | about 2–4 hours of your time: an adapter around your real Reflexive instructions, an API key, a run, a review | whether the **agent** holds the rules (already scheduled for October 30 and November 8) |
| Rewire the companion page's buttons to evaluate the record | about 1–2 hours | only that the page runs rules, not the agent. Low value |

**Replace** "Tested refusals (working checkpoint on the companion site)" **with:**

> Refusal rules: missing source → HOLD; invent lost text → REFUSE; publish identity → ESCALATE; generalize to all learners → REFUSE. The companion page demonstrates each rule with a fixed example response. In the research kit, the rules that can be checked from data fields alone run as automated tests: 11 attacks covering missing sources, fidelity relabeling, phone-side release and boundary widening, all held. The 15 attacks that need the agent's judgment are written and scheduled to run against the live agent before November 12.

**Short form (one line):**

> Four refusal rules, demonstrated on the companion page; the rule-based checks run as 11 passing automated tests, and live-agent tests are scheduled.

**After the October 30 run**, change the last clause to the real result, breaks included. For example: "15 live-agent attacks: N held, N over-refused, N broke (each fixed and re-run)". Use the numbers from `study/redteam/results.jsonl`, never estimates.

**Companion page.** It is linked from an application that has already been submitted, so I have not changed it. If you want it to match, replace the break-test note "Runs on this device. Explicit rules, no AI model." with:

> Demonstration: each button shows the decision and reason Reflexive's rule gives for that request. These are fixed examples, not a live test of the agent. Automated tests of the rules live in the research kit.

## B. Local-first: what stays on your devices, and what goes to ChatGPT/Codex

```
 STAYS ON YOUR DEVICES        SENT TO A CLOUD SERVICE
 ─────────────────────        ───────────────────────
 phone capture (Note)         Structure   ┐ de-identified
 ingest, hashing, raw         Interpret   │ text to
 de-identification            Synthesize  │ ChatGPT/Codex
 rule checks (policy gate)    model-assisted Check ┘
 review (phone + desk)
 the corpus (local Git)       Export → Figshare, only
 study measures, sealing        after a human release
                              study: seeding + live
                                red-team runs (model API)
```

| Step | Runs where | What leaves your devices |
|---|---|---|
| 1 Preserve, phone | iPhone (Shortcuts, Working Copy) | Nothing, with home-network sync. **Confirm:** dictation works in Airplane Mode (Phase 0, E.1); if it does, speech-to-text ran on the phone. |
| 1 Preserve, browser | the AI workspace where the work happens | The activity already takes place in ChatGPT/Codex, so its content is already there. Preserving it adds a local copy and a hash. |
| Ingest, hash, fidelity label, de-identification check | your desktop (Python kit) | Nothing |
| 2 Structure | the agent in ChatGPT/Codex | De-identified record text. **Confirm:** that Structure runs in the agent today, not only in your local scripts. |
| 3 Check | local scripts for duplicates, hashes and sensitivity scans; the agent for model-assisted checks | De-identified text, for the model-assisted checks only |
| 4 Interpret | the agent in ChatGPT/Codex | De-identified evidence excerpts and context |
| 5 Review | phone and desktop | Nothing |
| 6 Synthesize | the agent in ChatGPT/Codex | Approved, de-identified derived records |
| 7 Export | packaged on your desktop | Deposited to Figshare **only** after your release decision |
| Study: seeding, live red-team | a model API | De-identified review cards and test prompts |

**Replace** "Reflexive is a local-first agent" **with:**

> Reflexive keeps the research record on the researcher's own devices: capture, hashing, de-identification, rule checks, review and the corpus itself never leave them. The steps that need a language model (structuring, interpreting and synthesizing) send de-identified text to ChatGPT/Codex. Nothing is released, for example to Figshare, without a separate human decision.

**Short form:**

> Local-first record, cloud-assisted analysis: the evidence stays on the researcher's devices, and only de-identified text goes to the language model.

**Do not say** "nothing is sent to a server" about Reflexive as a whole. That is true of the companion demo page, not of the agent.

**Training (confirm before claiming "not used for training"):**
- ChatGPT: in **Settings → Data controls**, turn off *Improve the model for everyone*.
- API (seeding, red-team): OpenAI states that API data is not used for training by default. Check the current terms on the day you write the claim.

Then the application may say: "Private evidence is not used for model training: ChatGPT's training setting is off, and API calls are excluded by the provider's terms." Until you have checked both, say only "configured not to be used for training".

## Where this changes earlier text

- [11_grant_vs_repository.md](11_grant_vs_repository.md), rows G4 and G7: fixed by sections A and B.
- [10_framing.md](10_framing.md): both paragraphs now use this wording.
