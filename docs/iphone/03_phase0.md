# 3. Phase 0: capturing from the bus by Thursday

**Goal:** by Thursday, October 29, captures you speak on the bus are preserved into your existing corpus's raw layer, hashed and labeled. Review decisions are also logged with device, time and outcome. **No seeding yet.** Phase 0 is the baseline.

**What you need:** Apple Shortcuts (built in), the Working Copy app (a Git client for iOS; pushing needs its paid unlock), your private corpus repo, and this repo on your desktop.

**Sync stays on your own devices by default.** The phone pushes to a Git copy on your desktop over your home Wi-Fi, so captures never pass through a cloud service. That matches "local-first" and the June data plan. GitHub is the fallback (section A, option 2).

---

## Day 1: Monday evening or Tuesday's bus (about 40 minutes, once)

### A. Make the phone's corpus copy

**Option 1, local (default, about 20 minutes more):**
1. Desktop: turn on SSH (macOS: **System Settings → General → Sharing → Remote Login**). Then make a bare copy the phone can push to: `git clone --bare ~/corpus ~/corpus-phone.git`.
2. Working Copy: **Settings → SSH Keys → generate**. Add the public key to `~/.ssh/authorized_keys` on the desktop.
3. Working Copy: **Clone → `ssh://<you>@<desktop-name>.local/~/corpus-phone.git`**. This works only on your home network, which is the point.
4. Desktop, to collect captures: `git -C ~/corpus pull ~/corpus-phone.git main`. To send new review cards to the phone: `git -C ~/corpus push ~/corpus-phone.git main`. Use your branch name if it is not `main`.

**Option 2, GitHub (only if option 1 fails):** clone your **private** corpus repo from GitHub instead. Add one line to the data management plan first: "de-identified capture text syncs through a private GitHub repository".

Then, either way:
1. In the corpus, create a folder named `mobile_inbox`.
2. Commit with the message `add mobile inbox`.

### B. Build the capture shortcut

Name it something plain, like **Note**. The name shows briefly while it runs, so it must reveal nothing.

Each numbered line is one Shortcuts action, in order.

0. **Current Date** → set variable `Start`. This times the capture, so the 10-second target is measured, not assumed.
1. **Choose from Menu.** Prompt: `Save:`. Options, each setting two variables (`Type`, `Fidelity`) with **Text** plus **Set Variable** actions:
   - `Something happened` → `moment`, `user-supplied`
   - `I lost my place` → `context_loss`, `user-supplied`
   - `Moved to the computer` → `handoff`, `user-supplied`
   - `Rebuilding what was lost` → `context_loss`, `reconstruction`
   - `Just a marker` → `marker`, `user-supplied`
2. **If** `Type` is `marker`: set `Words` to empty text and `Method` to `none`. **Otherwise:** run **Dictate Text** (stop listening: *After Pause*), set `Words` to the result, and set `Method` to `dictation`.
3. **Dictionary** named `Names`. Each real name you might say maps to its pseudonym, for example `Jordan` → `Peer A`. Keep this list **only inside the shortcut**, never in the repo.
4. **Repeat with Each** key in `Names`: **Replace Text**, finding the key and replacing it with its value in `Words`. Set it case-insensitive, with regular expression on, and pattern `\b<name>\b`. Set `Words` to the result.
5. **Generate Hash**, SHA-256, of `Words` → `Hash`. For a marker, use this fixed text instead (it is the SHA-256 of empty text): `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
6. **Current Date** → **Format Date** with custom format `yyyyMMdd'T'HHmmss` → `Stamp`. **Random Number** from 1000 to 9999 → `Rand`. **Text** `m-Stamp-Rand` → `ID`.
7. **Format Date** (ISO 8601, with time) → `When`.
8. **Dictionary** with these keys (the envelope; see [07_schema.md](07_schema.md)):
   `envelope_version` = `0.2`, `capture_id` = `ID`, `captured_at` = `When`, `device` = `iphone`, `capture_type` = `Type`, `fidelity` = `Fidelity`, `text` = `Words`, `text_method` = `Method`, `text_sha256` = `Hash`, `boundary` = `private_research_only`, `capture_seconds` = **Get Time Between Dates** (`Start` → Current Date, in seconds), `minutes_since_event` = `unknown`.

   The use boundary is always the narrowest one from the phone. Widening it (to a de-identified study record or a public release) happens only at the desk, and ingest holds any capture that tries otherwise.
9. **Working Copy: Write Repository File.** Repo: your corpus. Path: `mobile_inbox/ID.json`. Content: the dictionary.
10. **Working Copy: Commit Repository.** Message: `capture`. Never put content in the message.

Stop there: no notification, no "are you sure". The entry is done when step 10 finishes.

**Time budget:** menu 1.5 s, speaking about 5 s, pause detection 1.5 s, write and commit 1 s. That is about 9 s. A marker takes about 2 s.

### C. Put it under your thumb

- **Settings → Action Button → Shortcut → Note** (or **Accessibility → Touch → Back Tap → Double Tap → Note**).

### D. Privacy settings (each one closes a leak)

- **Settings → Notifications → Working Copy → off.** Then nothing about the repo can appear on the lock screen.
- **Settings → Siri → Working Copy** and **→ Shortcuts:** turn off *Show on Lock Screen*, *Suggest App* and *Learn from this App*.
- **Settings → Privacy & Security → Analytics & Improvements → Improve Siri & Dictation → off.**
- No Lock Screen or Home Screen widget for either app.

### E. Test before trusting it

1. Turn on **Airplane Mode**. Run Note and say one sentence. If Dictate Text fails offline, replace step 2 with **Ask for Input** and use the keyboard's microphone key, which uses on-device dictation.
2. Run a marker.
3. Say a name that is in `Names` and check that the saved file shows the pseudonym.
4. **VoiceOver** (**Settings → Accessibility → VoiceOver**, or triple-click the side button if you set that shortcut): run Note once and Check once with VoiceOver on. Every menu choice should be read aloud by its words. Note anything that is not. This is the first screen-reader evidence the grant lists as "still to prove".

## Day 2: Wednesday, at the desktop (about 30 minutes)

### F. Preserve the first captures

```
git -C ~/corpus pull
python3 mobile/ingest.py \
  --inbox ~/corpus/mobile_inbox \
  --raw   ~/corpus/raw/mobile \
  --watchlist ~/deid_watchlist.txt
```

- `deid_watchlist.txt` is one real name per line. It lives **outside** both repos.
- Each line of output reads `PRESERVED`, `DUPLICATE`, `HOLD` (with a reason) or `REFUSE` (with a reason).
- If every capture says `HOLD … text_sha256 does not match`, the hash step is hashing something other than the exact text. Fix step 5 and re-capture.
- Commit `raw/mobile/` in the corpus. Leave the inbox files as they are; replaying them is harmless (`DUPLICATE`).

### G. Sync without thinking about it

In Shortcuts, add an **Automation → When joining Wi-Fi (home) → Working Copy: Push Repository**, set to *Run Immediately* with *Notify when run* off. The bus capture never waits for the network. With option 1, home Wi-Fi is also the only place a push can reach.

**Taking something back:** `python3 mobile/withdraw.py --raw ~/corpus/raw/mobile --inbox ~/corpus/mobile_inbox --capture-id <id> --reason participant_choice`. This deletes the file and records only its hash, and ingest refuses that capture from then on, even if the phone replays it. It also prints the step that erases the file from Git history.

### H. Start logging review on both devices (baseline, no seeds)

1. Have the agent write ten proposals, each a claim plus an evidence excerpt of **60 words or fewer**. Write them as review items to `review/queue.jsonl` in the corpus: `{"item_id", "queue", "evidence", "claim", "item_words", "agent_action_id", "model", "policy_version", "confidence"}`. The last four join each card to the agent action that proposed it; use `"unknown"` for confidence if the agent gives none. Set `queue` to `phone` or `desktop` at random. A coin flip is fine for now; from Phase 1, `study/seal.py` assigns it. Cards that do not match the shared schema are skipped and named.
2. **Desktop:** `python3 study/review_desk.py ~/corpus/review/queue.jsonl ~/corpus/study/decisions/desktop.jsonl`
3. **Phone:** build a second shortcut, **Check**, using the flow in [06_flows.md](06_flows.md), "Review on the phone". Each decision is written as `study/decisions/phone/<id>.json` and committed.

## Day 3: Thursday. Is it running?

Phase 0 is **running** when all four are true:

- [ ] At least 3 bus captures are `PRESERVED` in `raw/mobile/`, with manifest lines.
- [ ] At least 1 is a `context_loss` and at least 1 is a `handoff`.
- [ ] At least 1 review session is logged on each device, and the rows pass `measures.validate_decision`.
- [ ] Airplane-mode capture worked, or the fallback in E.1 is in place.

Also worth ticking, but not required: the VoiceOver run (E.4), and `capture_seconds` under 10 on the first three captures.

If one box will not tick by Thursday, Phase 0 is **still running** as long as the first box is ticked. Capture is the tool; the rest is the study.
