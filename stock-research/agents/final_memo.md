# Phase 7 — Final Memo

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS:
- Read **all step files** in `{BASE}/steps/` (full content; the user accepts higher token cost for completeness)
- `{BASE}/raw/10k.md` (canonical, for spot-checking facts)

This is the product memo. The CLAIM-LABELING format here is **different** from step files — see "FINAL MEMO CLAIM FORMAT" below.

## CONSTRAINTS

- Preserve uncertainty. Do not smooth contradictions.
- The conclusion MUST reflect what survived the counter-attack (`step10_counter_attack.md`).
- Unrebutted counter-attack points MUST lower confidence scores.
- **Decision must come from evidence, not from a default.**
  - BUY only when the three-tier valuation framework produces `current_price < buy_trigger` AND no Phase 4/5/6/7 finding contradicts the BUY.
  - PASS only when one or more criteria genuinely failed; specify which (e.g., "PASS because price > fair value range" or "PASS because moat confidence Low + cyclical-overlay → no valuation-based BUY allowed").
  - WATCHLIST when the price is between fair value and buy trigger, OR the verdict is downgraded one notch because total range width > 30% of midpoint (per `references/three_tier_decision.md`).
  - **PASS-as-tiebreaker is not allowed.** "When in doubt, PASS" is replaced by "when in doubt, surface the dispersion as the load-bearing finding and downgrade the verdict by one notch from what the valuation alone implies."

## FINAL MEMO CLAIM FORMAT (different from step files)

In step files, every paragraph opens with `[FACT | source | confidence]`. In this memo:

- **Verified facts:** plain prose. Superscript number at the end of the sentence.¹ Source-notes table at the bottom of each section. XBRL-verified numbers need no superscript — they're already verified.
- **`[HUMAN-VERIFY]` items:** keep visible inline prefix:
  > **⚠️ VERIFY:** [claim] — [why unverified]
  These are action items for the user; they must stay conspicuous.
- **`[INTERPRETATION]` items:** plain prose; end the sentence with `(judgment)`.

Source notes at the bottom of EACH section (not end of document):
> ¹ 10-K Item 7 | ² proxy.md | ³ Q2 FY26 earnings transcript | etc.

## REQUIRED SECTIONS — in this exact order

```
# {TICKER} — Investment Memo — [date]

## Data freshness
- 10-K data as of: [10-K filing date from raw/phase0_log.txt]
- 10-Q data as of: [10-Q filing date]
- Most recent 8-K: [date of most recent 8-K in raw/recent_8k.txt]
- Stock price anchored to: [date price was fetched in step9_valuation.md]

[If 10-K is more than 9 months old, add: "NOTE: The 10-K is [N] months old.
 Review raw/recent_8k.txt for material post-filing events."]
```

### Section 1 — DECISION (one line in bold)
- BUY at $X (target position size: Y% of portfolio)
- WATCHLIST — trigger price $X, what must verify before buying
- PASS — what would change to WATCHLIST

### Section 2 — SCORECARD (1-5)
| Dimension | Score | One-sentence justification |
|---|---|---|
| Business quality (economics + moat) | __/5 | ... |
| Moat durability confidence | __/5 | ... |
| Accounting quality | __/5 | Cite the 4-tier verdict (Clean / Acceptable with caveats / Concerning / Conservative) + opt-out flag (NONE / WATCH / RECOMMEND PARTIAL / RECOMMEND TOO HARD) from `step7_accounting.md` per `references/accounting_principles.md`. The score reflects both fields. |
| Management quality | __/5 | Includes accounting-candor cross-read from `step7_accounting.md` Tier-III evidence per `agents/management.md`. |
| Valuation attractiveness | __/5 | ... |
| Overall confidence | __/5 | ... |

### Section 3 — THE KEY INSIGHT

State the single most non-obvious, most important finding from this entire research. This is the one claim that differentiates this analysis from a generic analyst note.

Criteria:
- Should surprise a reader who has read the standard sell-side coverage
- Supported by primary-source evidence
- Has a concrete implication for the investment decision
- May be bullish or bearish

If you cannot find a genuinely non-obvious insight, write **literally** this:
> "No edge identified: the consensus view appears to be correctly pricing this business. The analysis confirms the market's assessment but does not find a differentiated angle."

This admission is valuable — it tells the user not to expect to find an edge here.

### Section 4 — THE BUSINESS (one paragraph; smart-teenager simple, no jargon)

### Section 5 — INVESTMENT CASE (bull case, evidence-based)

### Section 6 — THE RISKS (bear case)
**Length and rigor must be substantively comparable to Section 5.** No padding the bear case to clear a word count; each bull point should have a corresponding bear point that addresses the same dimension.

### Section 7 — WHAT THE COUNTER-ATTACK REVEALED
Reading from `step10_counter_attack.md`: which criticisms were valid? Which were refuted? Which were not addressed (these are the most important)?

### Section 8 — VALUATION

Read from `step9_valuation.md` (the reconciled alias produced by Phase 5C — combines CC and Codex independent valuations under the Buffett framework) AND `step7_accounting.md` (the pre-valuation economic earnings bridge that valuation consumes per `references/owner_earnings.md`).

- 8a-pre. **Accounting integrity context (three questions).** Before the valuation gate, surface the accounting agent's answers to Buffett's three questions [LT 12184-12195, 1988] from `step7_accounting.md`'s `=== BUFFETT'S THREE QUESTIONS ===` block:
  - Q1 (worth): does the accounting agent's bridge let valuation answer this at all? State the bridge magnitude (% of |GAAP NI|, or $-magnitude if |GAAP NI| < $50M).
  - Q2 (obligations): pension/OPEB gap, long-tail reserve adequacy, float reversibility.
  - Q3 (managers): Tier-III governance evidence (cross-ref Section 5 management).

  Then state the accounting **verdict** (4-tier) and **opt-out flag** (4-tier) from the accounting agent, and note the Stage-0 cascade implication. If the opt-out flag is RECOMMEND PARTIAL or RECOMMEND TOO HARD AND valuation proceeded anyway, document the explicit escalation reason (per the binding-unless-escalated rule in `references/underwriteability_gate.md`).
- 8a. **Underwriteability gate verdict.** UNDERWRITABLE / PARTIAL / TOO HARD. If TOO HARD, this section is shortened to the gate-verdict + optional reverse-DCF context only; no buy/keep/sell from valuation.
- 8b. **Single conservative intrinsic value (per share, Buffett rate).** ONE number from the DCF. State the Buffett rate (long-bond + cushion if any), Stage-1 growth, Stage-1 length, terminal g. Include the mechanical sensitivity table.
- 8c. **Buy trigger.** `buy_trigger = intrinsic_conservative × (1 − required_MoS)`. State the 3×3 matrix cell + any modifier adders (VULNERABLE / cyclical-overlay / reverse-DCF stretch) used to size MoS.
- 8d. **Opportunity-cost floor check.** Expected forward TSR at current price vs. `e_floor` (10% default OR user-configured ~7–8% per Munger framing). PASS or FAIL.
- 8e. **Capital-allocation flags.** $1 retention test (per-share-OE basis), buyback/issuance asymmetry vs intrinsic. Surface any flags that fired.
- 8f. **Reverse DCF (Buffett rate).** Implied Stage-1 growth at current price vs. trailing actuals, industry blend, and the 25%-absolute ceiling. State whether reverse-DCF stretch modifier (+5pp MoS) fired.
- 8g. **Illustrative CAPM parallel (decision-irrelevant).** Same conservative case re-run at the CAPM rate; reverse DCF at CAPM rate. Clearly labeled non-decision per `references/discount_rate_logic.md` illustrative-CAPM section. Reader sees both lenses; only the Buffett lens drives the verdict.
- 8h. **"What I'm most likely wrong about" (prose, mandatory, non-trivial).** Surface the four required subsections from `step9_valuation.md` Stage 9: the materially-higher case, the materially-lower case, judgment on which is more likely, and the single piece of observable + time-bounded + precisely-named evidence that would change the call.
- 8i. **Reconciliation summary.** Any decision-flipping divergences between CC and Codex from `step9_valuation_reconciled.md`. If a `=== DECISION-FLIPPING DIVERGENCE ===` section exists, surface verbatim — load-bearing.
- 8j. **Entry-price framework.** Map current price to BUY / WATCHLIST / PASS per the Stage-10 sequential decision logic in `references/three_tier_decision.md`. Cross-reference Section 9 (kill / reconsideration criteria).

### Section 9 — KILL / RECONSIDERATION CRITERIA (required for ALL three decisions)

**For BUY:** 5-7 criteria, each answerable yes/no on a quarterly basis. Pre-commit to sell if any single criterion triggers.

**For WATCHLIST:**
- "If I buy at the trigger price, I will sell if: [3-5 criteria]."
- "I will remove from watchlist if: [2-3 criteria that mean the thesis is broken]."

**For PASS:**
- "I will reconsider if: [2-3 criteria that would upgrade to WATCHLIST]."
- A PASS with no reconsideration path is a permanent dismissal — confirm that is intended.

### Section 10 — OPEN QUESTIONS (3-5 most important unresolved)

### Section 11 — THREE WAYS I'M WRONG (epistemic humility about THIS analysis, not about the business)

### Section 12 — SINGLE METRIC TO WATCH (12-24 months)

---

## Source notes at the end of the memo
[Master list of sources cited; reliability score from Verification C]

## After writing the draft to `steps/step11_final_memo.md`, run Verification C inline:

**NOTE: Verification D is dispatched by the orchestrator (parent skill), not by this agent.** The CRWD run exposed a methodology bug where this agent ran Verification D inline instead of as a cold subagent. Verification D's whole purpose is to evaluate the Key Insight from fresh context — inline execution defeats it. The orchestrator now spawns a fresh `general-purpose` Agent after this agent completes. Your job ends after Verification C + writing the corrected memo. Do NOT run Verification D yourself.

### Verification C — Full fact-check

For each specific factual claim:
1. Verify against `raw/10k.md` and `raw/xbrl_summary.txt`.
2. Use WebSearch for: founding dates, executive tenure dates, stock price history, competitor margins, brand ownership events.
3. Score each claim: Verified / Corrected / [HUMAN-VERIFY].
4. **Spot-check 2-3 cited historical analogs from Phase 4 and 1 base-rate citation from Phase 6** against the actual cited source. Confabulation check.
5. Calculate overall reliability % = (verified + corrected) / total claims checked.

Scan the draft for all prohibited phrases from `shared/writing_style.md`. Rewrite each.

Write `{BASE}/steps/verification_c.md`:
```
| Claim | Correct value | Source | Status |
|---|---|---|---|
Overall reliability: X%
```

### Verification D — DISPATCHED BY ORCHESTRATOR (not this agent)

Verification D is the Key Insight authenticity check. It MUST run as a fresh-context subagent so it does not inherit the writer's bias toward its own framing.

**The CRWD run exposed a methodology bug:** the final-memo agent (this agent) was instructed to "dispatch" Verification D as a subagent, but in practice ran it inline. The fresh-context test never fired. The fix: orchestrator (parent skill) spawns the cold subagent directly after this agent completes.

**This agent's responsibility ends after Verification C.** Do not invoke Agent tool with Verification D prompts here. The orchestrator handles it per `phases/step1e_pipeline.md` Phase 7.

Apply all Verification C corrections to `step11_final_memo.md`.

If reliability < 85%, add at top of memo:
```
RELIABILITY WARNING: Automated verification found reliability at X%.
See steps/verification_c.md for the error table.
Do not rely on any [HUMAN-VERIFY] items without checking the source yourself.
```

Append each Verification C correction to `{BASE}/bugs_encountered.md`:
```
[Verification C] CORRECTED: [claim] -> [correct value] (source: [source])
```
(Verification D logging is handled by the orchestrator after dispatching the cold subagent; see `phases/step1e_pipeline.md` Phase 7.)

Then append:
```
Total issues this run: N warnings, M corrections
```

Copy the corrected, verified memo to `{BASE}/{TICKER}_research_memo.md`.

OUTPUT FILE: `{BASE}/steps/step11_final_memo.md`, then copy to `{BASE}/{TICKER}_research_memo.md`

## Pre-append step — validate step files (lightweight, non-blocking)

After the memo is written and before running the auto-outcomes-append, run the lightweight validator:

```bash
py "~/.claude/skills/stock-research/scripts/validate_step_files.py" --base "{BASE}"
```

**Failure handling:** if the validator exits non-zero, append a single line to `{BASE}/bugs_encountered.md`:
```
[Phase 7] WARNING: validate_step_files.py reported issues — <stderr summary>; continuing to auto-outcomes-append (which will mark unparseable fields as [PARSE-FAIL] per Codex correction 7)
```
Then STILL proceed to the auto-outcomes-append step below. The validator surfaces problems but does NOT block the run; the append script will mark unparseable fields rather than failing the whole row.

## Final step — auto-append outcomes log

After the memo is fully written, copied to `{TICKER}_research_memo.md`, the validator has run, and all bug-log entries flushed, run:

```bash
py "~/.claude/skills/stock-research/scripts/append_outcome.py" --base "{BASE}"
```

**Failure-mode handling (per plan, Codex correction 5):** the auto-append is TELEMETRY, not the product. The user-facing memo is the product and is already complete by this point. Run the script as a single Bash invocation — the Bash tool reports non-zero exit automatically, so do **not** chain `; echo "EXIT=$?"`, capture `$?` manually, redirect with `2>&1;`, or compose any pre-flight `stat` / `ls` checks. If the script exits non-zero, append a single line to `{BASE}/bugs_encountered.md`:
```
[Phase 7] WARNING: outcomes log append failed — <stderr message>; memo otherwise complete
```
Either way Phase 7 completes successfully. Do NOT roll back the memo. Do NOT raise an error to the user. The duplicate-run case (no-op-with-warning) exits 0 and needs no log entry.
