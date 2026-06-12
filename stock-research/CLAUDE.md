# stock-research skill — orientation

## What this is

A dual-model qualitative stock research pipeline. Two skills coordinate across two terminals:

- **CC side** (this directory): orchestrator, summarization, analysis phases, final memo
- **Codex side** (`~/.codex/skills/stock-research-codex/`): independent verification, audit gates, optional adversarial counter-attack

It produces a sourced investment memo with reliability score and a forced "Key Insight" section (or honest "no edge identified" admission). Designed for personal use, not screen automation. Built around Strunk/Orwell/Munger writing standards and `[FACT|source|confidence]` claim labeling for every paragraph in working files.

Run from: `~/Research/` (where the project-level `.claude/settings.json` lives).

## ⚠️ VERY IMPORTANT — coordinate ALL skill changes with Codex

**Any change to the stock-research skill MUST be coordinated with Codex.** This is a dual-model architecture; CC and Codex own complementary sides of the same pipeline and share methodology references. Unilateral changes from one side break the symmetric contract that makes the cross-checks work.

**Coordination protocol — user is the message bus:**

1. **Before any non-trivial change**, CC writes a short message describing the proposed change (what, why, which side(s) it affects) and gives it to the user. The user pastes the message into a Codex CLI session.
2. Codex responds with agreement, pushback, or refinements. The user pastes Codex's response back to CC.
3. CC integrates: adopts where Codex caught real issues, pushes back where evidence supports CC's view (per `feedback_disagree_with_codex.md` — Codex's review is not gospel), reconciles where both views are defensible, and surfaces remaining open questions back to Codex through the user.
4. Iterate until convergence, then implement.

**What "non-trivial" means:** anything touching `SKILL.md`, `agents/`, `phases/`, `references/`, `scripts/` that changes behavior, adds/removes inputs/outputs, modifies section labels, changes file ownership rules, alters discount-rate / valuation / verification logic, or affects file paths that Codex reads or writes. Small typos and comment-only edits don't need round-tripping.

**For questions and confirmation:** CC can always send Codex a question or ask Codex to confirm something through the user. Format: `Question to Codex: <question>`. The user pastes; Codex replies; user pastes back. This is cheaper than discovering a divergence later.

**Why this matters:** the n=6 evidence base in this file shows distributed substantive catches across both sides — that distribution depends on both sides operating under the same shared methodology AND on each side knowing what the other is doing. Codex sometimes ships symmetric changes in PARALLEL with CC's planning (verified 2026-05-09 — Codex shipped its orchestrator-level reference precondition while CC was still planning the same change). Always check what Codex has already done before assuming CC owns both sides.

## How it works (orchestration overview)

Pipeline is multi-phase with manual terminal switches between CC and Codex. Each switch is a checkpoint where independence is preserved (each model reads sources without seeing the other's output yet). 9-10 switches per ticker depending on whether you opt into the Codex adversarial attack.

```
CC:    /stock-research TICKER                       Phase 0 (download)
Codex: $stock-research-codex TICKER --audit         Phase 0 audit gate
Codex: $stock-research-codex TICKER                 Step 1A (6 summaries incl. 10-K)
       or run resumable Step 1A: --step1a-10k -> --step1a-10q -> --step1a-proxy -> --step1a-insider -> --step1a-transcripts -> --step1a-customer -> --step1a-status
CC:    /stock-research TICKER --step1b              Step 1B + 1C (CC summaries + cross-check)
Codex: $stock-research-codex TICKER --step1d        Step 1D (Codex cross-check)
CC:    /stock-research TICKER --step1e              Step 1E + Verification A + Phase 2 (Gate) + Phase 3 (5 parallel agents + Agent F)
Codex: $stock-research-codex TICKER --consistency   Phase 3.5 cross-step thesis check
CC:    /stock-research TICKER --step3.5e            Phase 4 (Moat Durability) + Phase 5A (CC Valuation, multi-method, three-tier)
Codex: $stock-research-codex TICKER --valuation     Phase 5B (Codex independent valuation) ← NEW per Round 3 plan
CC:    /stock-research TICKER --reconcile-valuation Phase 5C (Reconciliation) + Phase 6 (Counter-Attack) ← NEW
Codex: $stock-research-codex TICKER --attack        OPTIONAL adversarial counter-attack
CC:    /stock-research TICKER --step11e             Phase 7 (Final Memo + Verification C + Verification D)
```

After each step, the running side outputs an exact handoff message telling you which terminal to switch to and which command to run.

11–12 manual terminal switches per ticker (vs 9–10 pre-Round-3). The two new switches (Phase 5B and Phase 5C) are the dual-model valuation — the centerpiece change that brings valuation up to the same cross-checking rigor as the rest of the pipeline.

## File layout

```
~/.claude/skills/stock-research/
├── CLAUDE.md                # this file
├── SKILL.md                 # orchestrator (frontmatter, flag routing, env notes)
├── shared/                  # prepended to every agent prompt at dispatch
│   ├── mission_frame.md     # epistemic ground rules + prompt-injection note
│   ├── claim_labeling.md    # [FACT|source|confidence] format (step files only)
│   └── writing_style.md     # Strunk/Orwell/Munger; prohibited phrases
├── references/              # NEW per Round 3 plan: shared methodology rules
│   ├── discount_rate_logic.md     # long-bond + ERP; 10% floor; multi-guardrail terminal g
│   ├── owner_earnings.md          # 1986 letter formula; equity vs EV rule; maint capex
│   ├── moat_durability_tiers.md   # research(b) durability table → Stage-1 + premium
│   ├── valuation_methods.md       # six methods + business-type → method matrix
│   └── three_tier_decision.md     # fair / hurdle / buy logic with ranges; MoS table
│   # Codex reads from this directory too — single source of truth
├── phases/                  # per-flag instructions
│   ├── phase0_download.md
│   ├── step1bc.md
│   └── step1e_pipeline.md   # handles --step1e, --step3.5e, --reconcile-valuation, --step11e
├── agents/                  # subagent prompt templates
│   ├── business_model.md    # Agent A (shallow research)
│   ├── industry.md          # Agent B (DEEP research)
│   ├── moat_current.md      # Agent C (shallow)
│   ├── accounting.md        # Agent D (shallow; reads full 10-K)
│   ├── management.md        # Agent E (shallow)
│   ├── customer_perspective.md  # Agent F (DEEP; criteria-based sourcing)
│   ├── moat_durability.md   # Phase 4 (DEEP; attack test)
│   ├── valuation.md         # Phase 5 (DCF + reverse DCF; Verification B run by orchestrator)
│   ├── counter_attack.md    # Phase 6 (DEEP on attacks 7-8)
│   └── final_memo.md        # Phase 7 (footnote format, Verification C + D)
└── scripts/                 # standalone Python (testable in isolation)
    ├── resolve_cik.py
    ├── extract_xbrl.py      # SHARES_JUMP detection, dei concept preference
    ├── strip_10k.py         # block-tags-to-newlines
    ├── extract_sections.py  # strict + gap-based section detection
    ├── parse_form4.py       # unpadded CIK
    ├── extract_8k.py
    └── detect_transcript_format.py
```

Outputs land at: `~/Research/{TICKER}_{D.M.YYYY}/` (timestamped per run; e.g., `MSFT_9.5.2026/`). Continuation flags resolve to this folder by globbing `Research/{TICKER}_*/` and picking the most recent mtime; legacy untimestamped `Research/{TICKER}/` folders are still readable as fallback.
- `raw/` — Phase 0 downloads + Step 1 summaries + canonicals
- `steps/` — Phase 2-7 analysis files
  - **Phase 5 specifically writes THREE valuation files:**
    - `step9_valuation_cc.md` — CC's independent valuation
    - `step9_valuation_codex.md` — Codex's independent valuation (no CC visibility)
    - `step9_valuation_reconciled.md` — CC's reconciled output combining both
    - `step9_valuation.md` — alias copy of reconciled output (preserves downstream prompt references in `final_memo.md`, `counter_attack.md`)
- `bugs_encountered.md` — running log of warnings/corrections per run
- `{TICKER}_research_memo.md` — final product

Cross-run calibration: `~/Research/outcomes_log.md` — append-only, one row per run, captures three-tier valuation outputs + verdict + reliability for cross-run analysis. Quarterly review of this file is the load-bearing experiment for whether the new architecture is well-calibrated or just consistently wrong in a different direction.

---

## How to improve this skill

The improvement loop is empirical: run, observe, propose, implement, validate. The format that worked in the session that built this skill (today's session, 2026-05-04):

### 1. Gather evidence

After each run, read in this order:

- `bugs_encountered.md` — automated warnings and corrections during the run. **This is the primary input.** Bug categories: data extraction failures, XBRL concept misses, section detection edge cases, transcript availability, stock splits detected, material 8-K events, Verification A/B/C/D corrections.
- The memo itself (`{TICKER}_research_memo.md`) — does the Key Insight section identify something non-obvious, or did Verification D replace it with "no edge identified"? Are the historical analogs in Phase 4 and base-rate citations in Phase 6 verifiable, or did they get confabulated despite the anti-confabulation rules?
- The cross-check files (`*_cc_xcheck.md`, `*_codex_xcheck.md`) — count substantive vs. stylistic discrepancies. The substantive ratio is the empirical justification for the dual-model architecture's complexity.
- The consistency check (`step3.5_consistency_check.md`) — did Codex catch any real inter-section contradictions, or was the file empty?

### 2. Write a one-page run review

Format:

```
# Run review — {TICKER} — {date}

## Decision and accuracy
- Skill's decision: BUY / WATCHLIST / PASS
- My prior view (write before reading the memo): ...
- Where they diverged and what convinced me to update (or not):

## Bug log highlights
[2-3 most important warnings or corrections from bugs_encountered.md]

## Confabulation check
- Phase 4 named analogs: verified / not verified / mixed
- Phase 6 base-rate citation: external-anchored / generated
- Key Insight: authentic / replaced with no-edge / generic summary slipped through

## Cross-check substantive ratio
- 10-Q: N substantive, M stylistic
- Proxy: ...
- (etc.)

## What broke (specific scripts or prompts that misfired)
## What surprised me (the analysis found something I'd have missed)
## What was generic (the analysis didn't add anything beyond a sell-side summary)
```

Keep these in `~/Research/{TICKER}/run_review.md`.

### 3. After 3-5 runs, decide what to change

Pattern that worked once:

- **Bring all evidence into a fresh Claude Code session.** Reference `bugs_encountered.md`, run reviews, plan archive at `~/.claude/plans/`, and this CLAUDE.md.
- **Critique-and-converge:** if you have time, run the proposal through a second model (the dialectical pattern from today). Where the two reviews agree is consensus; where they disagree is where the answer is least obvious and most worth thinking about. Both sides usually catch things the other misses.
- **Triage into slices:** bugs → robustness → structural changes → content additions. Each slice should be independently shippable.
- **Don't over-fit on one run.** The PANW empirical evidence drove a lot of architecture decisions. With 3-5 runs, some of those decisions may need revisiting (especially Slice 5 asymmetric model specialization — see `DESIGN_NOTES.md`).

### 4. Validate

After implementing changes, run the skill on a ticker you have a strong prior on. Check whether the changes:
- Catch the issue from the previous run that motivated them
- Don't break anything that worked
- Produce different output (not just "more reliable" output — analytical depth is the bigger lever)

Update `bugs_encountered.md` aggregation across runs to track changes empirically.

---

## Known problems and limitations

Three categories: **bugs** (need fixing), **unverified assumptions** (need empirical validation), **by-design tradeoffs** (chose them deliberately, document in case priorities change).

### Bugs (none currently known beyond what's been fixed)

All historically-fixed bugs and their detection runs are catalogued in `EVIDENCE.md`. If a new bug appears in `bugs_encountered.md` or `bugs_encountered_codex.md`, document the fix and append the entry to `EVIDENCE.md` when it's resolved.

### Validated structural decisions (n=7)

The cross-check value pattern, Phase 3.5 consistency check, bidirectional correction inbox, Codex's parallel bug log + run review, and (post-CRWD 2026-05-12) the Buffett-faithful valuation framework + Stage-0 underwriteability gate are all validated by the n=7 evidence base. Detail (which run validated which mechanism, with example catches) lives in `EVIDENCE.md`.

**The CRWD-driven v1.3 valuation rewrite (2026-05-12) inverted the discount-rate hierarchy:** Buffett rate (long-bond + mechanical real-rate cushion) is now PRIMARY; CAPM is a clearly-labeled illustrative parallel that does NOT feed buy/keep/sell. This reversed the Round-3 CAPM-creep documented in EVIDENCE.md "Decisions made and unmade." The CC ↔ Codex independent convergence on the Buffett framework after end-to-end reads of Berkshire transcripts 1994–2022 + letters 1977–2024 is the validation. Stage-0 underwriteability gate added as binary go/no-go filter before any DCF.

### Unverified assumptions (empirical validation needed)

These are architecture decisions that *might* be right but haven't been tested against enough runs to know:

- **Phase 0 audit gate hit rate.** Designed to catch upstream propagating bugs. PANW had two such bugs. PAYX produced 2 warnings (low-yield: competitor margin extraction gap, 8-K keyword matches), no critical blockers. MSFT similar. Codex's own honest read: keep it as a "collection-integrity guardrail," not as analytical validation.
- **Confabulation rate in deep-research outputs.** Phase 4 named analogs and Phase 6 base-rate citations are the highest-confabulation-risk outputs. Anti-confabulation rules are in place ("no verified analog found" admission, external-anchored base rates) but their effectiveness is untested. Spot-check 1-2 cited analogs per run.
- **Per-agent input slicing for focus.** Each agent reads a focused subset of files (Agent B reads only Item 1 + competitors + 8-K, not the full canonical 10-K). The argument is that focused inputs improve quality. If a run shows Agent X clearly missing something it could have caught from a file we excluded, expand that agent's inputs.
- **Key Insight Verification D effectiveness.** Section 3 of the memo can either be a real non-obvious insight or honestly admit no edge. Verification D's "would a sell-side analyst plausibly write this?" test is supposed to catch confabulated insights. Whether the test actually fires correctly is unverified — read every memo's Section 3 critically until you've seen the test reject something.
- **Stock-split detection threshold.** >30% YoY jump in `SharesOutstanding` triggers a flag. PANW's 3:1 and 2:1 splits triggered it cleanly. False positive risk: large buybacks compressing share count, large secondaries diluting it. Tune after 2-3 more runs.
- **`find_real_section` rule.** Currently uses "Item N. preceded by 'PART I' header AND followed by alpha prose, not page numbers". May misfire on unusual 10-K formatting. Falls back to gap-based detection if it does. Watch for cases where the gap fallback is invoked — that's a sign the strict rule is too strict.

### By-design tradeoffs and deferred decisions

The full list of deliberate tradeoffs (manual terminal switches, no per-stage analytical gates, scorecard tension, mission-frame divergence between CC and Codex, asymmetric customer-perspective xcheck, 8-K not summarized by Codex, axis-based primary-source classifier, FPI track, agent watchdog, opt-in Deep Research, competitor narrowing, adoption-status reporter) and the intentionally-deferred decisions (asymmetric model specialization, multi-quarter transcript absence-tracking, training-data analog lists, word-count symmetry, Phase 6 dual-model, Verification D test ticker, outcomes_log review cadence) lives in `DESIGN_NOTES.md`. Read it when revisiting why a design choice was made.

10-K coverage (after the 2026-05-10 reversal): dual-summary + cross-check, like the other core documents.

---

## Deferred Buffett-source-grounded extensions

After valuation (2026-05-12) and accounting (2026-05-13) were ported onto the Berkshire letters + transcripts, the original ranking had moat → management as the next two passes. Both are paused. The reasoning and the queue:

### Prerequisite gate — accumulate before extending

Do not start any framework in this section until `Research/outcomes_log.md` reaches **≥6 real research-run entries** (currently 2: MSFT, CRWD). Calibration tickers (MSCI, PGR, UNP, VRX back-test) do not count. The skill has more diagnostic apparatus than its track record can justify; the next dollar of effort earns more from running it on new tickers than from refining the framework against the source files again.

### Moat — queued, intentionally lighter than accounting

Moat is centrally Buffett — the castle/moat metaphor enters the 1995 letter and recurs through 2024, transcripts have decades of Q&A on moat erosion, "widening the moat" is a recurring management-test phrase. The current `agents/moat_current.md` is 35 lines and `agents/moat_durability.md` is 77; the asymmetry with `agents/accounting.md` at 170 + `references/accounting_principles.md` at 596 is real but should NOT be closed by matching shape.

**Target size: ~150–250 lines of reference, NOT 596.** Frame as 4–7 recognizable patterns, not a 26-principle checklist. Moat-pattern recognition stops being moat-pattern recognition if it is operationalized as a checklist — Buffett's own moat material is closer to pattern catalog than principle taxonomy. Resist the urge to mirror accounting's build.

**Pattern to follow (already established by valuation and accounting):**
1. Independent CC + Codex passes against `Feedbak/Berkshire-Hathaway-Letters-to-Shareholders_to2024.md` and `Feedbak/Berkshire Meeting Transcripts - 1994 - 2022 (1).md`, using the `[LT n]` / `[TX n]` citation convention.
2. Reconciliation via user-as-bus per the coordination protocol at the top of this file.
3. 4-tier verdict (suggested: Wide-and-widening / Wide-stable / Narrow / Eroding) with explicit erosion-evidence rules.
4. Operational rules — what makes Agent C / Agent (moat-durability) fire each verdict, integration into Section 4 of the memo.
5. Snapshot pre-change `agents/moat_current.md` + `agents/moat_durability.md` to `Feedbak/pre-v1/`.
6. Validation tests: one known wide-moat compounder (e.g., MCO, MSCI), one known eroded moat (e.g., legacy newspaper or department store), one ambiguous case.
7. Schema update in `outcomes_log.md` only if the verdict adds new cross-run information not already captured.

### Management — deprioritized, not removed

Tier-III governance (G1 audit committee / G2 comp committee / G3 accounting-optics-feeds-management) in `references/accounting_principles.md` already absorbs the candor + governance signal Buffett emphasizes most. A parallel Buffett-grounded management framework would mostly restate Tier-III with new vocabulary. The 77-line `agents/management.md` is the right size for what it does. **Revisit only if real runs show the management agent missing things Tier-III does not catch** — concretely, if 2+ runs surface a management-related issue that step7's Tier-III fires did not flag.

### Other candidates worth mining (ranked by primary-source density)

If moat ships and outcomes data is still thin, these are the next-richest seams in the Feedbak files:

- **Capital allocation discipline.** Letters are saturated — share repurchase rules (the IV-vs-price test specifically), retained-earnings test ("a dollar of retained earnings should create at least a dollar of market value"), "elephant" acquisition criteria, the dividend-vs-buyback-vs-reinvest hierarchy. Would fit as `references/capital_allocation.md` consumed by `agents/management.md` and feeding Section 2 of the memo. Probably the **highest-value extension after moat** because it directly bears on BUY/PASS via the buyback-vs-IV check that D9 currently only flags optics on.
- **Circle of competence.** Transcripts have decades of Q&A on how Buffett & Munger define, update, and police theirs. Could feed `references/underwriteability_gate.md` as a self-audit prompt: before the gate fires UNDERWRITABLE / PARTIAL / TOO HARD, force a circle-of-competence reflection. Light touch — likely an addition to existing gate logic, not a new reference file.
- **Float / insurance-specific economics.** Partially in accounting D6, but float-cost-of-capital, reserve-development discipline, and the "two-column owner-earnings for insurance" model from the late-1990s letters have more depth than D6 currently encodes. **Only worth doing if an insurance ticker (BRK, PGR, ACGL, CB) enters the real-run pipeline** — until then it is pure framework-building against a hypothetical use case.

### How each pass should be done

The pattern is now standard and should not be re-derived per pass:

1. Independent CC + Codex passes against both Feedbak files with `[LT n]` / `[TX n]` citations.
2. Reconciliation via user-as-bus (per top-of-file coordination protocol).
3. Verdict design — usually 4 tiers, with explicit opt-out cascade if the verdict should bind valuation (accounting does; moat may not need to).
4. Operational rules: which agent fires which verdict, what evidence each fire requires, what gets propagated downstream.
5. Snapshot pre-change agents + reference files to `Feedbak/pre-v1/<topic>/` before the change.
6. Validation tests on 2–3 known-labelled cases + 2–3 calibration tickers covering different business profiles.
7. Update `outcomes_log.md` schema only if the new framework produces a column that distinguishes cross-run patterns; otherwise leave the schema alone.

### What was considered and rejected here

A full Buffett-grounded management-framework parallel build (mirroring accounting's 596-line reference + verdict + opt-out cascade) was considered and **deliberately skipped** because of redundancy with Tier-III G1–G3. Future sessions should not re-propose this without first showing that real runs surfaced management-relevant misses Tier-III did not catch.

---

## Empirical evidence base

Detailed run-by-run evidence (PANW / PAYX / MSFT / DECK / SNOW / NVO / CRWD findings, what each run validated, what's still unknown at n=7, and the log of decisions made and unmade including the CRWD-driven CAPM reversal) lives in `EVIDENCE.md`. Read it when proposing skill changes.

---

## Companion skill — `/stock-report`

After a research run completes, build the HTML investment writeup with `/stock-report TICKER`. Consumes the canonical post-verification files in `Research/{TICKER}/raw/` + `Research/{TICKER}/steps/` and writes one self-contained HTML file at `Research/{TICKER}/{TICKER}_full_report.html`. Inline SVG charts; stdlib-only Python.

The full design (audience + shape, the 11-section operating-manual anatomy, universal writing rules, the eight orchestration steps including the coverage-audit gate, the GICS-keyed sector + industry primer system, iteration commands, evidence base, known issues) lives in the report skill's own `CLAUDE.md` at `~/.claude/skills/stock-report/`. Read that when iterating on the report skill.

## Plan archive

The dialectical history that produced this skill lives in `~/.claude/plans/`. To start an iteration: read this CLAUDE.md, the most recent plan, and `bugs_encountered.md` + `bugs_encountered_codex.md` from the latest 2-3 runs.

## Skill archive (full snapshots)

Date-stamped full snapshots (CC skill + Codex skill + plans) live at `~/Research/_archive/`. Run `py archive.py <label>` from that folder before AND after a change, so the snapshot pairs with the run output that produced it.

---

## A note for fresh Claude sessions

If you're a fresh Claude Code session being asked to improve this skill: the user values direct critique, distinguishes load-bearing critique from filler, and runs proposals through multiple models for second-opinion review. Don't be diplomatic for its own sake. Where you disagree with a previous reviewer, name it. Where you agree, say so concisely without restating their argument. The user reads dense responses fluently and dislikes summaries that re-state what they already wrote.

Output quality dominates convenience for this user — don't propose token-saving optimizations that compromise output unless context-window physics actually requires them. The dual-model dual-terminal friction is acceptable; per-stage convenience consolidations are not.
