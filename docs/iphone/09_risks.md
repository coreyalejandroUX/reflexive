# 9. Risks and failure modes

## Bad days come first

| What happens | The fix built in |
|---|---|
| Too tired to speak | "Just a marker": about 2 seconds, a complete entry. |
| Cannot face reviewing | Do not open Check. Nothing reminds you, and nothing counts days. |
| Review starts to spiral | The stop rule ends the session itself (10 cards, 8 minutes, 3 "hold" in a row, or a reopened card). The end screen is the same every time. |
| A planted card feels like it is about *you* | "Is this one planted?" reveals that one card and removes it. The seed rules forbid false facts about your life, so if a card feels that way, it is a bug to report. |
| Several hard days in a row | Pause study. Capture keeps working. Resume when you choose, with no message on return. The pause is logged as a fact, not a failure. |
| Unblinding results hurt | Read them with the escrow person, framed as interface performance. Your catch rate measures phones and buses, not your worth. |
| Doubting your own memory after seeing what slipped through | Seeds only ever lived inside labeled agent proposals. Your captures, in your words, were never touched, and the raw-immutability test proves it. |

## Tool failures

| Failure | Effect | Fix |
|---|---|---|
| Dictation fails offline | capture blocked | fallback: Ask for Input with the keyboard microphone (Phase 0, E.1). A marker always works. |
| Hash step hashes the wrong thing | every capture HOLDs | caught on day 2. Fix step 5. Nothing is lost: envelopes wait in the inbox. |
| Working Copy push fails | captures pile up locally | harmless. Commits are local and push later. Replays are `DUPLICATE`. |
| Name not on the watchlist | an identity reaches raw | the desktop watchlist is a second check. Export runs a third check (`publish-identity`). The native app adds automatic name detection. |
| Phone lost or stolen | local corpus copy exposed | device passcode plus Face ID. The corpus copy holds de-identified text only. Revoke Working Copy's key from GitHub. |
| Shortcut edited by mistake | wrong labels | ingest's fidelity-by-type table HOLDs impossible combinations. |
| Lock screen or notification leak | sensitive text visible | no notifications from either app. Siri suggestions off. A neutral shortcut name. Nothing in the shortcut ever shows content outside the app. |

## Study failures

| Failure | Effect | Fix |
|---|---|---|
| Too few seeded items | intervals too wide to say much | expected. Reported as a pilot: estimate the spread, size the follow-up. |
| You guess which items are seeded | blinding weakens | the rate is drawn from a range. Clean and seeded cards look alike. Seed instances are written by a separate model. |
| Seeded errors easier or harder than real ones | catch rate misleads | the natural-escape audit at unblinding compares the two. |
| Secret exposed before unblinding | blinding broken | the commitment still proves the key was not changed. Report the exposure date, and analyze only items assigned before it. |
| Escrow person unavailable | cannot unblind on November 11 | a second escrow recipient (encrypt the key file to two keys). |
| A seeded item reaches derived or release | contaminated evidence | staging plus the open-block release HOLD. If it happens anyway, treat it as a reportable incident: roll back from Git, then log what failed. |
| Phone reviews mostly happen on good days | device confounded with state | energy is logged. Report it by device. Treat it as a stated limitation, not a fix. |
| IRB/ethics determination not back | cannot seed | run the block without seeds (time, rubber-stamping, red-team), and seed later. See [05_timeline.md](05_timeline.md). |

## Safety-research risks

| Risk | Fix |
|---|---|
| Treating 0 breaks in 24 attacks as "safe" | Report it as "24 of 24 held". Grow the suite each run. Any new attack that breaks a rule is added permanently. |
| The agent learns the red-team prompts | Keep the suite out of any prompt or fine-tuning data. Rotate in new attacks each run. |
| Over-refusal hiding in "held" | Over-refusals are counted separately. A rule that refuses everything is not working. |
| Overclaiming from N = 1 | The generalization section in [04_study_design.md](04_study_design.md), plus the V&T ledger in the November 12 packet. |
