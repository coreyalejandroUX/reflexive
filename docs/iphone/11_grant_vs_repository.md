# 11. Where the grant application and the repository disagree

Use this list to correct future applications. Each row gives what the application says, what I could check, and suggested wording. "Could not verify" means I had no access. It does **not** mean the claim is false.

**Checked:**
- the Catalyst application, both versions, and its visual companion page;
- GitHub `reflexive` (empty until October 26) and `ms-ai-project-workbench` (a separate project);
- the June study zip in Drive.

**Not found anywhere I can reach:** the 68-capture corpus and the workspace with 19 tests.

| # | The application says | What I found | Suggested wording until fixed |
|---|---|---|---|
| G1 | Pilot corpus: "68 validated captures", on "schema version 2.1", "already separated into raw, evidence, record, derived and release layers". | Could not verify. The corpus is not in any reachable repo or in Drive. | Name where it lives (private repo), or say "held privately; available to reviewers on request". |
| G2 | §1 says "68 validated **episodes**". §5 says "68 validated **captures** (52 platform interactions, 12 AI-workspace consultations, four **derived artifacts**)". | Internal inconsistency. In your own layer model a derived artifact is not a capture, and an episode is a Structure output, not a capture. | Pick one unit. For example: "64 captures structured into N episodes, plus 4 derived artifacts". Run `tools/fidelity_report.py` to get the real counts. |
| G3 | "Accessible local workspace: 19 automated tests, type-checking, linting and production builds pass." | Could not verify. No TypeScript workspace among the four repos this account can reach. (`ms-ai-project-workbench` has two Node test files and no type-checking or lint, and it is a different project.) | Name the workspace repo, or say "local workspace, not yet public". |
| G4 | "Tested refusals (working checkpoint on the companion site)". | On the companion page the four refusal buttons return fixed, pre-written verdicts, whatever the record contains. The capture routing is real but simple rules ("Reflexive routing 0.3, explicit rules, no model"). | "Demonstrated refusals". After October 30: "9 of 9 structural refusal tests pass; live-agent red-team results in the pilot report". |
| G5 | Four fidelity labels: direct, user-supplied, transcription, reconstruction. | The companion's checkpoint record stores "Corroborated…" / "Documented…" / "Reconstruction only…" in a field also named `fidelity`. | Two questions, two fields: capture method and support strength (proposal P7). Do not describe the corpus's labels until the report has run. |
| G6 | "Every agent action records its input, the policy version applied, model, output, confidence and the human's disposition, in a provenance log aligned with W3C PROV." | Labeled "works or will work". No PROV log found. The companion's audit trail stores time, action and detail only. | Split the sentence: what works today (hashing, audit trail, rule-set version) and what is planned (a PROV-aligned log with model and confidence). |
| G7 | "Local-first agent" (§2). The companion says "Nothing is sent to a server." | Interpretation runs on ChatGPT/Codex (cloud models), per the same application. The companion demo is local; the real agent is not. | "Local-first storage; interpretation uses a cloud model on de-identified text". |
| G8 | Visual companion link. | The two versions of the application point to two different demos: a `chatgpt.site` prototype and a claude.ai artifact. | Use one link in all applications, or name both and say what each shows. |
| G9 | "Users can inspect, correct, embargo, withdraw or delete." | No withdraw or delete path exists in this kit yet. Ingest is strictly append-only. | "Correction by new versioned records today; withdrawal and deletion are being built." |
| G10 | Outcome metrics: attention per capture under 2 minutes; inter-reviewer agreement. | Nothing measures capture time yet. Single participant, and no second reviewer arranged. | List these as "will be measured in the pilot". Name the independent coder (budget line) as the source of agreement data. |
| G11 | Demo is "mobile-first, screen-reader-ready". | Not tested with a screen reader. The application itself lists "screen-reader testing with users" under "still to prove". | "Built to screen-reader guidelines; testing with users is planned". |

## Consistent, no change needed

- The seven steps and who acts at each.
- The five layers.
- The four refusal rules and their outcomes (HOLD, REFUSE, ESCALATE, REFUSE).
- Human decisions: interpretation, codebook and hypothesis changes, identity, every release.
- Single participant; studies with others need ethics or IRB review.

## Also worth knowing

`ms-ai-project-workbench` uses a third fidelity wording: `user_supplied_verbatim_or_explicitly_labeled`. If an application describes "Reflexive's fidelity labels" across your projects, three vocabularies exist today.
