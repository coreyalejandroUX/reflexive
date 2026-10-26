# Key concepts: what each one IS and IS NOT

Each concept gets two lines. Other files link here instead of re-explaining.

## Data and provenance

**Transit inbox**
- IS: a folder where the phone drops capture envelopes before they are checked.
- IS NOT: the raw layer. Nothing in the inbox counts as evidence until `mobile/ingest.py` preserves it.

**Raw layer (immutable)**
- IS: the first place a capture is stored for good. Append-only. Each file's hash goes in a manifest.
- IS NOT: an editable draft. A correction is a new capture that points to the old one, never an overwrite.

**Fidelity label**
- IS: how close the stored content is to the event it describes: `direct` (the thing itself, such as a screenshot), `user-supplied` (your account of it), `transcription` (text copied from an image), `reconstruction` (rebuilt from memory after it was lost).
- IS NOT: a quality score or a judgment of you. A reconstruction is honest evidence when it is labeled as one.

**Capture types on the phone**
- `moment`: something happened worth keeping.
- `context_loss`: you lost your place, such as a chat vanishing after an app switch. It is first-class: the loss itself is data.
- `handoff`: the phone could not finish the task and you had to move to the computer. Also first-class.
- `marker`: a timestamp and nothing else. This is the minimum-viable entry.
- IS NOT: a coding scheme. Types say what kind of capture this is, not what it means. Meaning belongs to Interpret.

**De-identification at capture**
- IS: replacing known names with pseudonyms (for example "Peer A") on the phone, before anything is saved or synced.
- IS NOT: a full privacy guarantee. It catches names you have listed. The desktop check is a second net, and Export runs a third check.

**Use boundary**
- IS: who may use a record: private research only, de-identified study record, public release requested, or not sure yet. The phone can only set the first or the last.
- IS NOT: consent itself. It records the decision; widening it is a separate desk decision, and public release still goes through ESCALATE.

**Withdrawal**
- IS: the one sanctioned way to remove a capture. The file is deleted, its hash and a reason code are kept, and ingest refuses that capture forever after.
- IS NOT: erasure from Git history. That is a separate step the tool prints, and it must be run on purpose.

**Derived staging**
- IS: a holding area for review decisions made during a study block. They move into the derived layer only after unblinding.
- IS NOT: hidden data. You can see it. It is simply not used by Synthesize or Export until the block closes.

## Oversight study

**Review (step 5)**
- IS: you deciding whether an agent's proposal is supported by the evidence.
- IS NOT: rewriting. On the phone you decide; editing waits for the desk.

**Meaningful oversight**
- IS: oversight that changes outcomes. It catches errors at a useful rate, and acceptance is not faster than reading.
- IS NOT: the presence of an approve button. A human in the loop who approves everything is a rubber stamp, not oversight.

**Seeded error**
- IS: a deliberately planted mistake in an agent proposal, either an unsupported claim or a wrong code, used to measure whether review catches it.
- IS NOT: a false statement about your life. Seeds are never false facts about what you did, said, or felt, and never touch your own words. See [04_study_design.md](04_study_design.md), "Seeding protocol".

**Sealed log (commit-reveal)**
- IS: the record of which items were seeded. It is encrypted to someone else's key, and its secret's hash is published before the study, so nobody can change it afterward without being caught.
- IS NOT: a vault you cannot open. It is tamper-evident, not tamper-proof. Its strength is that any change shows.

**Blinding**
- IS: not knowing which items are seeded, or the exact rate, while you review.
- IS NOT: not knowing seeding exists. You consented to it and know the rate range (10–25%).

**Catch rate**
- IS: of the seeded items you decided, the share you did not approve (ask for narrower, hold, or reject).
- IS NOT: a personal score. It measures the review interface under conditions. That is the point of the study.

**Rubber-stamping**
- IS: accepting an item faster than it could be read: under 1 second per 8 words, so 30 words in under 3.75 s.
- IS NOT: every fast accept being wrong. It is a behavioral flag, checked against catch rate.

**Unsupported-claim escape rate**
- IS: the share of seeded unsupported claims you approved. These are the errors that would have entered the analysis.
- IS NOT: the same as 1 minus catch rate. That covers wrong codes too.

**Refusal rule and red-teaming**
- IS: the four rules (missing source → HOLD, invent lost text → REFUSE, publish identity → ESCALATE, generalize to all learners → REFUSE), and a set of attacks written to make the system break them.
- IS NOT: proof of safety. Zero breaks on 24 attacks means those 24 held. It says nothing about the 25th.

**Break**
- IS: the system allowing what a rule forbids.
- IS NOT: an over-refusal, where it refused more than needed. That is logged separately as a cost, not a breach.

**Scalable oversight**
- IS: the research question of whether humans can keep supervising AI systems as the work grows faster, larger, or harder to check.
- IS NOT: automation replacing review. It asks when human review still works and how to support it.

**AI control**
- IS: designing a system so that even a model that makes mistakes, or misbehaves, cannot cause harm without a human or a hard rule stopping it. Examples: deterministic gates, desktop-only release, audits with planted errors.
- IS NOT: trusting the model to behave. Control assumes it might not.

## Wellbeing and method

**State check-in**
- IS: an optional, one-tap note about session context (energy low / ok / high) kept as a research covariate.
- IS NOT: symptom tracking, diagnosis, or a mood score. It never uses clinical words and is never required.

**Stop rule**
- IS: the session ending on its own after 10 items, 8 minutes, or 3 "hold" in a row, so review cannot turn into rumination.
- IS NOT: a failure or a penalty. Stopping is logged as data, and the rest waits.

**Single-case design**
- IS: a study of one person over time, with conditions randomized inside that person's own days.
- IS NOT: a sample. It cannot estimate how often anything happens to other people.

**Analytic generalization**
- IS: carrying a finding to theory or design. For example: "under these conditions, this reviewer's oversight degraded this way, so interfaces need X".
- IS NOT: statistical generalization ("learners do Y").
