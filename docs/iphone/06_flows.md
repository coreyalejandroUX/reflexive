# 6. Capture and review flows

These rules apply to every screen below:
- One screen asks for one action.
- No instruction names a place on the screen ("top right", "swipe left"). Choices are named by their words.
- Nothing asks "are you sure?".
- When something is saved, it is done. There are no streaks, counts, or "you missed a day" messages.

## Capture (the Note shortcut)

```
 [press]
    │
 SCREEN 1   "Save:"
            Something happened
            I lost my place
            Moved to the computer
            Rebuilding what was lost
            Just a marker ──────────┐
    │                               │
 SCREEN 2   (listening)             │
            speak; a pause ends it  │
    │                               │
  saved ◀──────────────────────────┘
  done.
```

| Screen | You do | The phone does |
|---|---|---|
| 1 | choose one phrase | sets type and fidelity |
| 2 | speak (skipped for a marker) | turns speech into text, swaps listed names, hashes the text, writes and commits |
| (none) | nothing | the entry is done |

**Context lost.** "I lost my place" records *that* the loss happened, in your words, as `user-supplied`. "Rebuilding what was lost" is for when you deliberately reconstruct the missing content, and it is labeled `reconstruction`. The agent may never do the rebuilding: that is the REFUSE rule. Only you may, and the label says so.

**Moved to the computer.** Say what you could not do on the phone. The desktop session that follows can link back to this capture, so the handoff becomes a pair of linked captures (see the schema proposal in [07_schema.md](07_schema.md)).

**Minimum-viable entry.** "Just a marker" saves a timestamp and nothing else in about 2 seconds. Later, at the desk, you may add a note that points to it. Or never: a marker alone is a complete entry.

## Review on the phone (the Check shortcut)

```
 [open Check]
    │
 SCREEN A   Context (optional)
            Energy low · ok · high
            Skip
    │
 SCREEN B   Setting (optional)
            Moving · Still · Skip
    │
 ┌─▶ SCREEN 1   Evidence
 │              (≤ 60 words)
 │              Next · Stop for now
 │       │
 │   SCREEN 2   Agent proposal
 │              (claim or code)
 │              Approve
 │              Ask for narrower
 │              Hold
 │              Reject
 │              Stop for now
 │       │
 │   saved; next card,
 └── unless the stop rule says rest
         │
 SCREEN END  "Saved. Review is
              closed for now."
```

| Screen | You do | Logged |
|---|---|---|
| A, B | one tap each, or Skip | session context (covariates only) |
| 1 | read the evidence, then Next | `presented_at` |
| 2 | one decision | `decided_at`, `dwell_ms`, `outcome`, `device: phone`, `agent_action_id` |
| End | nothing | session end and its reason |

These are the grant walkthrough's words, plus Reject:

| Choice | Means | Stored as |
|---|---|---|
| Approve | the proposal is supported by the evidence | `approve` |
| Ask for narrower | the idea may hold, but the claim says more than the evidence (the route for over-generalization) | `narrow` |
| Hold | not enough to decide; gather more evidence first | `hold` |
| Reject | the proposal is wrong, for example a wrong code | `reject` |

**Hold is always a safe answer.** The card goes to the desk and does not count as approved.

**After narrow or reject**, the desk is where you may say *why*. The phone never asks why.

## The stop rule

The session ends itself on the first of these:
- 10 cards;
- 8 minutes;
- 3 "Hold" in a row;
- the same card opened twice in one day.

The last two are the rumination signals: circling, re-checking, unable to settle. The end screen is the same no matter which rule ended the session. It never says which one, because naming it would make it a judgment. The reason is logged for the study.

- The stop rule IS: a wall that protects attention and wellbeing, and a data point.
- It IS NOT: a scold. It cannot be turned off mid-session. It can be changed only between sessions, at the desk, and that change is logged.

## The state check-in

- **Asked:** only at the start of a review session, never during capture.
- **Words used:** energy low / ok / high, and moving / still. No clinical words, no symptom lists, no mood scales.
- **Where it goes:** the session record, as a covariate. Never into a capture, never into an export.
- **Skip** is always the last choice and is never counted against anything.

## Pause and bad days

A third shortcut, **Pause**, has one screen: `Pause study` or `Resume study`.
- Pausing stops new seeded cards and hides Check's queue.
- Note (capture) keeps working.
- No message is shown when you come back.
