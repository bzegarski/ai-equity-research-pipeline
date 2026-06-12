# Codex Independent Valuation Agent

DO NOT READ `steps/step9_valuation_cc.md`.
If it exists, ignore it. Independence is the entire point of this phase.

Do not read `steps/step9_valuation.md`, `steps/step9_valuation_reconciled.md`, or `raw/cc_catches_against_codex.md` during this phase. Read only the source inputs listed below, the shared references listed below, and current market-data sources needed for price, shares, rates, inflation, and consensus.

## PRECONDITION CHECK

Fail loudly if any of these shared methodology references are missing:

- `~/.claude/skills/stock-research/references/discount_rate_logic.md`
- `~/.claude/skills/stock-research/references/owner_earnings.md`
- `~/.claude/skills/stock-research/references/moat_durability_tiers.md`
- `~/.claude/skills/stock-research/references/valuation_methods.md`
- `~/.claude/skills/stock-research/references/three_tier_decision.md`
- `~/.claude/skills/stock-research/references/underwriteability_gate.md`
- `~/.claude/skills/stock-research/references/accounting_principles.md`

If ANY reference is missing, abort with exactly:

```text
REFERENCES MISSING: CC has not built shared references yet. Run CC's Phase C first.
```

Do not attempt valuation without the references. Do not fall back to your own methodology. Do not maintain a Codex-local copy of these references.

## Inputs

For ticker `TICKER`, use the path conventions from `SKILL.md`. Resolve `BASE` through the timestamped-folder rule in `SKILL.md`; do not assume a bare `Research/TICKER` folder.

Required inputs. If any are missing, abort and tell the user which file is missing:

- `RAW/xbrl_summary.txt`
- `RAW/10k.md`
- `RAW/transcripts.md`
- `STEPS/step6_moat_durability.md`
- `STEPS/step7_accounting.md`

Required-if-present inputs. Read these when they exist; if absent, do not abort:

- `RAW/10q.md`
- `RAW/competitors.md`
- `RAW/customer_perspective.md`
- `STEPS/step3_business_model.md`
- `STEPS/step4_industry.md`
- `STEPS/step5_moat_current.md`
- `STEPS/step8_management.md`
- `STEPS/step4b_customer_perspective.md`

If a required-if-present file is missing, note the absence in `=== MOST FRAGILE ASSUMPTIONS ===`, downgrade confidence on the affected dimension, and do not invent the missing input.

When reading `STEPS/step7_accounting.md`, specifically consume these blocks:

- `=== GAAP NI -> PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===` / `=== GAAP NI to PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===`
- `=== OWNER-EARNINGS INPUT FLAGS FOR VALUATION ===`
- `=== OPT-OUT FLAG ===`
- `=== HIDDEN VALUE FROM CONSERVATIVE ACCOUNTING ===`

If `STEPS/step7_accounting.md` exists but lacks the pre-valuation economic earnings bridge or opt-out flag, abort and tell the user that CC must rerun the accounting agent under the v1 Buffett accounting framework before Codex valuation. Do not silently fall back to the old generic accounting output.

Stage 0 must use only pre-Phase-6 evidence: `step6_moat_durability.md`, `step4_industry.md`, `step5_moat_current.md`, `step7_accounting.md`, `step8_management.md`, `raw/customer_perspective.md` if present, and `raw/competitors.md`. Do not read `STEPS/step10_counter_attack.md` or any Phase 6 counter-attack file. Phase 6 may later challenge or revise the Stage-0 verdict, but it is not a Phase 5B valuation prerequisite.

Current market-data exception: valuation needs current price, market cap or share count, 30-year Treasury yield, 10-year Treasury yield, trailing-12-month core PCE inflation, normalized nominal GDP or terminal-growth context, and sometimes analyst consensus. Source and date these from current public sources when they are not already in the input files. If current market data cannot be verified, mark all price-dependent conclusions `[HUMAN-VERIFY | Low]` and do not issue a BUY verdict.

## File Hygiene

Write only:

- `STEPS/step9_valuation_codex.md`

Do not write or modify:

- `STEPS/step9_valuation.md`
- `STEPS/step9_valuation_reconciled.md`
- `STEPS/step9_valuation_cc.md`
- `RAW/cc_catches_against_codex.md`

After writing `STEPS/step9_valuation_codex.md`, update `CODEX_BUGS` through the normal Codex run-log block. Log underwriteability ambiguity, accounting opt-out cascade ambiguity, pre-valuation economic earnings bridge disagreement, owner-earnings starting-point ambiguity, SBC handling risk, FCF bridge gaps, discount-rate/cushion source issues, capital-allocation-test uncertainty, missing optional inputs, and self-corrections. Do not touch CC's inbox from this phase.

## Required Output Sections

For UNDERWRITABLE or PARTIAL businesses, write `STEPS/step9_valuation_codex.md` with these exact top-level section labels, in this order:

```text
=== RATE ANCHOR ===
=== UNDERWRITEABILITY GATE ===
=== OWNER EARNINGS DERIVATION ===
=== DISCOUNT RATE ===
=== STAGE-1 GROWTH AND DURATION (single conservative case) ===
=== TERMINAL GROWTH ===
=== INTRINSIC VALUE (per share, Buffett rate) ===
=== SENSITIVITY TABLE (mandatory, mechanical) ===
=== MARGIN OF SAFETY AND BUY TRIGGER ===
=== OPPORTUNITY-COST FLOOR CHECK ===
=== CAPITAL ALLOCATION TESTS ===
=== REVERSE DCF (Buffett rate) ===
=== ILLUSTRATIVE -- HOW THE VOLATILITY / CAPM SCHOOL WOULD VALUE THIS (not a decision input) ===
=== WHAT I'M MOST LIKELY WRONG ABOUT ===
=== MOST FRAGILE ASSUMPTIONS ===
=== VERDICT ===
```

For TOO HARD businesses, write `=== RATE ANCHOR ===`, `=== UNDERWRITEABILITY GATE ===`, optional `=== REVERSE DCF (Buffett rate) ===` as non-decision market-expectations context, `=== MOST FRAGILE ASSUMPTIONS ===`, and `=== VERDICT ===`. The verdict must say: `No valuation-based decision. Business does not clear certainty filter.`

Use the paragraph confidence labels required by `SKILL.md`. Tables may use source/confidence columns instead of repeating tags in every cell.

## Governing Framework

Read the seven shared references before valuing. They govern over the checklist below. The checklist exists to make Codex's output symmetric with CC's v1.3 valuation framework and v1 Buffett accounting framework.

### RATE ANCHOR

State the valuation date, current stock price, market cap or current diluted shares used, 30-year Treasury yield, 10-year Treasury yield, trailing-12-month core PCE inflation, computed real long-bond yield, cushion applied, final Buffett discount rate, and data source/date for each. If the 10-year and 30-year Treasury yields differ by more than 50 bp, flag it in `MOST FRAGILE ASSUMPTIONS`.

Apply the valuation freshness rule from `discount_rate_logic.md`: if the nominal 30-year Treasury has moved more than +/-75 bp between the valuation date and decision date, the valuation must be re-run before any BUY/WATCHLIST/PASS action.

### UNDERWRITEABILITY GATE

Classify the business before any DCF:

- `UNDERWRITABLE`: cash-flow trajectory is predictable for 10+ years with current evidence.
- `PARTIAL`: moderate certainty; material pre-valuation disruption vectors remain.
- `TOO HARD`: cash flows are not defensibly forecastable.

Use `underwriteability_gate.md`. The load-bearing disruption-vector source at Phase 5B is the Phase 4 moat-durability inventory in `step6_moat_durability.md`, supplemented by `step4_industry.md`, `step5_moat_current.md`, `step7_accounting.md`, `step8_management.md`, `raw/customer_perspective.md` if present, and `raw/competitors.md`.

Apply the structural rule: VULNERABLE moat cannot be UNDERWRITABLE. Reclassify to PARTIAL or TOO HARD before margin-of-safety sizing.

Apply the accounting opt-out cascade from `underwriteability_gate.md` and `accounting_principles.md`. The cascade reads the `=== OPT-OUT FLAG ===` block in `step7_accounting.md`, not the accounting verdict tier:

- `RECOMMEND TOO HARD`: force Stage 0 to `TOO HARD`.
- `RECOMMEND PARTIAL`: downgrade `UNDERWRITABLE` to `PARTIAL`; leave `PARTIAL` as `PARTIAL`.
- `WATCH`: surface the caveat in Stage-0 confidence prose; no automatic downgrade.
- `NONE`: no accounting-driven Stage-0 effect.

The cascade is binding unless explicitly escalated. Codex may deviate only by writing a source-backed disagreement in `=== UNDERWRITEABILITY GATE ===` and `=== MOST FRAGILE ASSUMPTIONS ===` so CC can resolve it in Phase 5C reconciliation. Silent override is forbidden.

If Stage 0 is TOO HARD, do not run a forward DCF, do not emit BUY/WATCHLIST/PASS, and do not compensate by raising the discount rate. You may include a reverse-DCF read of market expectations as non-decision context.

### OWNER EARNINGS DERIVATION

Default to Buffett owner earnings from `owner_earnings.md`.

First consume the `=== GAAP NI -> PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===` / `=== GAAP NI to PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===` and `=== OWNER-EARNINGS INPUT FLAGS FOR VALUATION ===` blocks from `step7_accounting.md`. Treat the accounting bridge as the pre-Stage-1 economic earnings baseline. Valuation owns the final owner-earnings input: apply maintenance-capex and working-capital judgment from `owner_earnings.md` to the accounting-adjusted economic earnings, or explicitly document a source-backed disagreement with the accounting bridge. Silent re-derivation from raw GAAP NI is forbidden when the accounting bridge reports a material adjustment, opt-out flag, or Conservative hidden-value item.

If the accounting verdict is `Conservative`, read `=== HIDDEN VALUE FROM CONSERVATIVE ACCOUNTING ===`. Add specific, source-backed hidden-value items to economic earnings or net asset value only when their line-item nature supports the treatment. If ignored, explain why.

Preferred starting point is GAAP Net Income:

```text
Owner earnings = GAAP Net Income
               + D&A
               + non-real amortization add-backs
               - maintenance capex
               - incremental working capital required to sustain unit volume
               + working-capital float net, only when justified by owner_earnings.md
```

SBC rules:

- Starting from GAAP Net Income: do nothing. SBC is already deducted. Do not add it back and do not subtract it again.
- Starting from GAAP Operating Cash Flow, Wall Street adjusted FCF, or non-GAAP earnings: re-deduct SBC because those metrics typically add it back.
- Use current diluted shares outstanding as the primary denominator. Projected future shares may appear only as a sensitivity input.
- Do not both charge SBC in owner earnings and model future share dilution as the primary denominator.

If using the accounting bridge and it starts from GAAP Net Income, the SBC bridge line should be `$0 incremental adjustment` with a note that SBC is already deducted in GAAP NI. Still report SBC burden as a valuation risk when relevant, using SBC as a percentage of revenue, SBC as a percentage of absolute GAAP Net Income, and 5-year dilution net of buybacks. Only re-deduct SBC when starting from OCF, adjusted FCF, or non-GAAP.

FCF rules:

- Any use of "FCF" or "free cash flow" must label the definition on first use.
- Never consume externally labeled FCF as owner-earnings-equivalent without the bridge required by `owner_earnings.md`.
- If the bridge cannot be built, keep the FCF number as a non-decision comparison and flag the gap.

Maintenance-capex rules:

- Asset-light steady state: use trailing 3-year average D&A when PP&E growth is below 3% per year.
- Asset-light growth mode: use current-year D&A when PP&E growth is at least 3% per year.
- If total capex is greater than 1.5x D&A for 3+ years, flag growth capex dominance; use D&A as maintenance unless evidence proves otherwise.
- Capital-intensive: use management's maintenance/growth split when disclosed; otherwise use 60-80% of trailing total capex with `[HUMAN-VERIFY]`.
- Acquisition-heavy: add back only non-real purchase-price amortization. Do not add back amortization that reflects genuinely depleting software, IP, or customer assets.
- R&D/S&M maintenance versus growth: deduct the maintenance portion needed to preserve competitive position. Use management disclosure when available; otherwise label the split as a judgment.

### DISCOUNT RATE

Use one decision-relevant discount rate: the Buffett rate from `discount_rate_logic.md`.

- Primary anchor: nominal 30-year US Treasury yield.
- Cushion: apply the mechanical real-rate cushion from `discount_rate_logic.md`. Label it as skill policy derived from Buffett, not a literal Buffett formula.
- No ERP, no beta, no CAPM, and no volatility adjustment in the decision sections.
- Same rate across businesses that clear Stage 0. Differences belong in the numerator, Stage-0 gate, and margin of safety.
- Document the pre-tax-rate-on-after-tax-owner-earnings convention.

CAPM/beta/ERP may appear only in the illustrative section.

### STAGE-1 GROWTH AND DURATION

Produce one conservative forecast, not three labeled scenarios.

Triangulate Stage-1 growth from available indicators:

- trailing 5-year revenue CAGR
- trailing 4Q TTM revenue growth
- trailing 5-year owner-earnings CAGR
- trailing 5-year per-share owner-earnings or labeled FCF CAGR, after FCF bridge
- trailing 5-year NOPAT growth where relevant
- analyst consensus revenue growth for the next 12 months, if sourced
- analyst consensus EPS or FCF growth for the next 12 months, if sourced and FCF definition is bridged
- management guidance if specific
- backlog, RPO, deferred revenue, or unit-volume indicator where available
- bottoms-up TAM penetration only if `step4_industry.md` provides a defensible TAM model

Use the median or lower of the available indicators unless a specific source-quality reason supports another conservative input. If indicators diverge widely, state the dispersion and reflect it in Stage 0, MoS, and `MOST FRAGILE ASSUMPTIONS` rather than inventing scenarios.

Stage-1 length must come from moat durability and reinvestment runway:

- HIGH: 10-15 years
- MODERATE: 7 years
- LOW: 5 years
- VULNERABLE: reclassify Stage 0 to PARTIAL or TOO HARD

Stage-1 growth above 15% requires extraordinary evidence. Long-horizon growth must be below the discount rate.

### TERMINAL GROWTH

Use one terminal growth rate. It must satisfy all guardrails in `discount_rate_logic.md` and `valuation_methods.md`:

- `g <= long-bond yield`
- `g <= normalized nominal GDP`
- `r - g >= 3 percentage points`
- lower or negative terminal growth for declining industries

Default USD terminal context is 2.0-2.5% only when the business and currency support it. Do not use 3%, 5%, or 10% because it is convenient.

### INTRINSIC VALUE

Run the single conservative Stage-1 + 5-year fade + terminal structure from `valuation_methods.md` at the Buffett rate. Output one intrinsic value per current diluted share.

Do not output narrative scenario ranges. Do not average unrelated methods. Cross-checks may challenge the single intrinsic value, but the decision rests on the conservative Buffett-rate owner-earnings valuation.

Keep cash-flow basis and comparison base consistent:

- Levered owner earnings from GAAP NI compare to equity market cap and current diluted shares.
- Unlevered NOPAT/FCF compare to EV, then subtract net debt to reach equity.
- Do not add cash or subtract debt inside a levered owner-earnings DCF.

For foreign filers or ADRs, track reporting currency, trading currency, and ADR ratio. If ambiguity remains, mark valuation `[HUMAN-VERIFY | Low]` and do not issue BUY.

### SENSITIVITY TABLE

Include a mechanical one-input-at-a-time sensitivity table. Show the percentage change in intrinsic value from the base case for:

- discount rate +1pp
- discount rate -1pp
- Stage-1 growth +2pp
- Stage-1 growth -2pp
- Stage-1 length +2 years
- Stage-1 length -2 years
- terminal growth +0.5pp
- terminal growth -0.5pp
- maintenance capex +20% relative
- maintenance capex -20% relative
- SBC +20% and -20% for SBC-heavy businesses only, required when SBC is greater than 10% of revenue or greater than 50% of absolute GAAP Net Income

For the SBC row, perturb forward SBC magnitude through GAAP NI or the selected starting-point bridge. Do not model this as a separate dilution term.

### MARGIN OF SAFETY AND BUY TRIGGER

Apply one margin of safety at the end. Use the 3x3 Stage-0 x moat-durability matrix in `three_tier_decision.md`, with the VULNERABLE structural rule and adders:

- VULNERABLE moat: use LOW moat base cell and add 5pp after Stage 0 is forced to PARTIAL or TOO HARD.
- cyclical-overlay: add 5pp.
- reverse-DCF stretch: add 5pp when the reference threshold is met.
- cap total MoS at 60%; above 60%, reconsider TOO HARD.

Buy trigger:

```text
buy_trigger = intrinsic_conservative * (1 - required_MoS)
```

### OPPORTUNITY-COST FLOOR CHECK

Calculate expected forward TSR at the current price:

```text
owner-earnings yield at current price
+ organic owner-earnings growth
+ buyback yield, only when average buyback price is below intrinsic_conservative
- value-destructive issuance effect, only when average issuance price is below intrinsic_conservative
```

Do not include a separate SBC dilution term when SBC is already netted into owner earnings.

Compare expected forward TSR to the opportunity-cost floor from `discount_rate_logic.md`, default 10% unless the user or reference specifies a different floor. If expected forward TSR does not clear the floor, downgrade per `three_tier_decision.md`.

### CAPITAL ALLOCATION TESTS

Run all applicable tests from `valuation_methods.md`:

- $1 retention test on normalized per-share owner earnings. Use market value only as secondary confirmation because multiple cycles distort short windows.
- Buyback asymmetry: buybacks below intrinsic create per-share value; buybacks above intrinsic destroy per-share value.
- Share-issuance asymmetry: issuance below intrinsic destroys per-share value; issuance above intrinsic can create value.
- Look-through earnings only for holding companies or businesses with material equity portfolios.

Capital-allocation failures can modify growth assumptions, trigger a downgrade, and must be surfaced in `MOST FRAGILE ASSUMPTIONS`.

### REVERSE DCF

Run reverse DCF at the Buffett rate. Solve what Stage-1 growth the current price implies, using the same owner-earnings base, Stage-1 duration, fade shape, terminal growth guardrails, and share count policy.

Compare implied growth to trailing history, guidance, industry growth, moat-durability evidence, and the absolute ceiling in `three_tier_decision.md`. If the reverse DCF is implausible, apply the specified downgrade and surface the result.

For TOO HARD businesses, reverse DCF may be shown as non-decision market-expectations context only.

### ILLUSTRATIVE CAPM SECTION

After the Buffett valuation is complete, include:

```text
=== ILLUSTRATIVE -- HOW THE VOLATILITY / CAPM SCHOOL WOULD VALUE THIS (not a decision input) ===
```

This section may compute CAPM rate, rerun the same single conservative case at CAPM, and show reverse DCF at CAPM. It must state that CAPM/beta/volatility are not decision inputs under the Buffett framework. Do not let this section affect BUY/WATCHLIST/PASS.

### WHAT I'M MOST LIKELY WRONG ABOUT

Write more than 200 words of prose, not a table. Include four subsections:

- The case where intrinsic value is materially higher than the conservative estimate.
- The case where intrinsic value is materially lower.
- Judgment on which side is more likely and why.
- The single piece of evidence that would change the call.

The evidence that would change the call must be observable in public disclosure, time-bounded, and precisely named. Vague claims such as "growth slows materially" fail this section.

### VERDICT

Use the sequential decision logic in `three_tier_decision.md`:

1. If Stage 0 is TOO HARD, emit no valuation-based BUY/WATCHLIST/PASS.
2. Otherwise compute the base verdict from price versus intrinsic and buy trigger.
3. Apply one-notch downgrades for failed opportunity-cost floor, PARTIAL Stage 0, reverse-DCF implausibility, and capital-allocation failure.
4. Saturate downgrades at two notches.

Always state which downgrades fired. A BUY verdict requires that no downgrades fire and price is at or below the buy trigger.

## Fragility Checks

Before finalizing, explicitly check:

- Did any required-if-present input absence impair Stage 0, owner earnings, growth, discount rate, buybacks, SBC, or capital-allocation tests?
- Did `step7_accounting.md` include the required v1 accounting bridge, owner-earnings input flags, opt-out flag, and Conservative hidden-value block? If not, abort and require CC accounting rerun.
- Did owner earnings consume the accounting pre-valuation economic earnings bridge, or explicitly document a source-backed disagreement? If not, fix it.
- Did the Stage-0 verdict honor the accounting opt-out cascade, or explicitly escalate a source-backed disagreement for Phase 5C? If not, fix it.
- Did Stage 0 accidentally use Phase 6 or `step10_counter_attack.md`? If yes, remove it and redo Stage 0.
- Did any FCF input lack a definition label or owner-earnings bridge? If yes, bridge it or block it from decision use.
- Did owner earnings start from GAAP NI while SBC was also subtracted or future shares were used as the primary denominator? If yes, fix it.
- Did owner earnings start from OCF/adjusted FCF/non-GAAP while SBC was not re-deducted? If yes, fix it.
- Did levered owner earnings get compared to EV? If yes, fix it.
- Did the model mix currencies or ignore ADR ratio? If yes, fix or flag.
- Did current price, shares, Treasury yields, inflation, or analyst consensus come from stale or unsourced data? If yes, source it or mark low confidence.
- Did Stage-1 growth extrapolate current rates despite low moat durability or divergent growth indicators? If yes, reduce growth, raise MoS, or downgrade Stage 0.
- Did terminal value dominate the model? If yes, surface the sensitivity.
- Did the illustrative CAPM section leak into the verdict? If yes, remove it from the decision path.

## Handoff

After writing `STEPS/step9_valuation_codex.md` and updating `CODEX_BUGS`, tell the user exactly:

```text
Codex independent valuation written to step9_valuation_codex.md. Switch to CC and run /stock-research TICKER --reconcile-valuation.
```
