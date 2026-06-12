# Phase 5A — CC Valuation (Buffett framework, single conservative case + sensitivity)

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

This phase produces CC's independent valuation per the Buffett-faithful framework. Codex builds its own valuation in parallel (`--valuation` flag, terminal switch). CC's reconciliation phase (`--reconcile-valuation`) consumes both. Until reconciliation runs, CC's valuation must remain procedurally independent of Codex's.

## PRECONDITION CHECK — fail loudly if any of these are missing

```
References (REQUIRED — methodology depends on them):
  ~/.claude/skills/stock-research/references/discount_rate_logic.md
  ~/.claude/skills/stock-research/references/owner_earnings.md
  ~/.claude/skills/stock-research/references/moat_durability_tiers.md
  ~/.claude/skills/stock-research/references/valuation_methods.md
  ~/.claude/skills/stock-research/references/three_tier_decision.md
  ~/.claude/skills/stock-research/references/underwriteability_gate.md
```

If ANY missing, abort with: `REFERENCES MISSING: required methodology files not found.` **Do NOT attempt valuation without references — they encode the methodology.**

## INPUTS

REQUIRED (must exist; abort if any missing):
- `{BASE}/raw/xbrl_summary.txt`         primary financial data
- `{BASE}/raw/10k.md`                    annual filing canonical
- `{BASE}/raw/transcripts.md`            recent earnings calls (note TRANSCRIPT_SOURCE_QUALITY header)
- `{BASE}/steps/step6_moat_durability.md` drives Stage-0 gate + Stage-1 length
- `{BASE}/steps/step7_accounting.md`     drives tax normalization, accounting flags

REQUIRED IF PRESENT (read when file exists; log absence in `=== MOST FRAGILE ASSUMPTIONS ===`, do not abort):
- `{BASE}/raw/10q.md`                    freshest financials
- `{BASE}/raw/competitors.md`            peer multiples sanity check
- `{BASE}/steps/step3_business_model.md` business classification input
- `{BASE}/steps/step4_industry.md`       industry growth, TAM, terminal-growth flag
- `{BASE}/steps/step5_moat_current.md`   moat type → Stage-0 input
- `{BASE}/steps/step8_management.md`     capital allocation policy → Stage 6 tests

If a "required if present" file is missing: note absence in `=== MOST FRAGILE ASSUMPTIONS ===`, downgrade confidence on the affected dimension, do not invent the missing input.

WebFetch the current stock price for {TICKER} (try finance.yahoo.com/quote/{TICKER} or similar). WebFetch current 30-Year US Treasury yield (treasury.gov, finance.yahoo.com/quote/^TYX). WebSearch trailing-12m core PCE inflation (BEA, Fed FRED). WebSearch analyst consensus revenue growth estimates if available.

## PROCEDURAL INDEPENDENCE RULE — DO NOT VIOLATE

**During this phase (before writing `step9_valuation_cc.md`):**
- DO NOT read `{BASE}/steps/step9_valuation_codex.md` (shouldn't exist yet; if it does from an aborted prior run, ignore it).
- DO NOT read current-run valuation entries in `{BASE}/cc_catches_against_codex.md` (older entries from prior steps are fine and expected).
- Read only the input list above.

The reconciliation phase (`--reconcile-valuation`) is where both valuations get read together. This phase produces independent CC output.

RESEARCH DEPTH — MEDIUM: bounded WebSearch for current price, 30Y Treasury yield, core PCE inflation, consensus estimates, and ONE peer-multiples sanity check. The math + assumption derivation is the work.

---

## STEP 0 — Underwriteability gate (BEFORE any DCF)

Per `references/underwriteability_gate.md`. Classify the business into ONE of three buckets BEFORE running any DCF:

- **UNDERWRITABLE** — cash flows predictable 10+ years with current evidence
- **PARTIAL** — moderate certainty; material disruption vectors present
- **TOO HARD** — cash flows not defensibly forecastable

Inputs (per `underwriteability_gate.md`):
1. Phase 4 moat-durability 10y confidence tier (from `step6_moat_durability.md`)
2. Disruption-vector count and probabilities (from `step6_moat_durability.md` and `step4_industry.md`)
3. Industry change rate (low / moderate / high)
4. Unit-volume and pricing-power predictability
5. Competitive position trajectory (widening / holding / narrowing)

**Structural rule:** Phase-4 VULNERABLE moat is incompatible with Stage-0 UNDERWRITABLE. Reclassify to PARTIAL (or TOO HARD if decisive). Apply BEFORE the matrix in Stage 4.

If verdict is **TOO HARD**: stop after this section. Write the gate verdict + optional reverse-DCF read of market expectations (clearly labeled non-decision) per `underwriteability_gate.md`. Skip Stages 1–8. Output `=== VERDICT === No valuation-based decision. Business does not clear certainty filter.`

If verdict is **UNDERWRITABLE** or **PARTIAL**: proceed to Stage 1.

## STEP 1 — Owner earnings derivation

Per `references/owner_earnings.md`. Compute from XBRL data using the canonical formula starting from GAAP NI:

```
Owner earnings = GAAP Net Income (NetIncomeLoss from xbrl_summary.txt)
              + D&A (DepreciationDepletionAndAmortization)
              + non-real amortization add-backs (acquisition-related; typically ~80% of GAAP amortization at acquisition-heavy firms)
              − Maintenance capex (judgment per business class — see Step 2)
              − Incremental working capital required to sustain unit volume
              + Working capital float net (SaaS-WC-float caveat in owner_earnings.md applies)
```

**SBC is NOT added back.** Starting from GAAP NI, SBC is already deducted. Per Buffett 2015 [LT 35528]: SBC is real compensation; adding it back is the "most egregious example" of management/Wall-Street charade. Apply the conditional-on-starting-point table in `owner_earnings.md` to handle non-GAAP starting points.

Use trailing 4-quarter (TTM) values where 10-Q is present. State the period used (e.g., "TTM through Q3 FY26"). State which XBRL concept supplied each number.

For FOREIGN-CURRENCY filers (modifier +foreign-currency): compute owner earnings in REPORTING CURRENCY. Final intrinsic-per-share converts to share-price currency (ADR ratio / FX) only at output.

For SaaS with WC-float dominance (WC float > 50% of OE): trigger Stage 9 prose requirement to address sustainability explicitly.

## STEP 2 — Maintenance capex

Per `owner_earnings.md` Maintenance vs growth capex section. The hardest single judgment in owner earnings.

```
ASSET-LIGHT (PP&E < 20% of revenue):
  Steady-state (PP&E growing < 3%/yr): trailing 3-year average D&A
  Growth-mode (PP&E growing ≥ 3%/yr):  current-year D&A
  Flag if total capex > 1.5× D&A for 3+ years.

CAPITAL-INTENSIVE:
  60–80% of trailing total capex. Cite management split if disclosed; else 70% as default + [HUMAN-VERIFY].

ACQUISITION-HEAVY:
  Add back ~80% of GAAP amortization as non-real.

SBC-HEAVY:
  No special maint-capex rule; require SBC sensitivity row in Step 7 sensitivity table.

CYCLICAL:
  Trough-period total capex (5–7 year history).
```

State the assumption explicitly: *"Maintenance capex assumed at $X = [method]; growth capex of $Y treated as reinvestment, not deducted from owner earnings."*

## STEP 3 — Stage-1 growth (9-indicator triangulation, conservative pick)

Compute estimates from MULTIPLE indicators (use what's available; log absences):

```
G1  trailing 5y revenue CAGR              (XBRL Revenue rows)
G2  trailing 4Q TTM revenue growth        (XBRL Revenue, most recent vs year-ago)
G3  trailing 5y owner-earnings CAGR       (computed from XBRL)
G4  trailing 5y per-share FCF CAGR        (captures buyback compounding)
G5  trailing 5y NOPAT growth              (operating-income post-tax)
G6  analyst consensus revenue (NTM)       (WebSearch; flag source)
G7  analyst consensus EPS or FCF (NTM)    (WebSearch; flag source)
G8  management guidance if specific       (transcripts.md, recent_8k.md)
G9  backlog / RPO / unit-volume indicator (transcripts, 10-Q; SaaS, defense, infra only)
G10 (optional) bottoms-up TAM × penetration
```

**Conservative pick:** use **MEDIAN or LOWER** of the available indicators, with narrative anchoring. Per Buffett 2003 [TX 43151]: *"be as realistic as you can on those numbers, but with any errors being on the conservative side."*

DIVERGENCE FLAG: if max − min > 5pp, state: *"Growth methods diverge by Xpp; business in transition or fragile predictability; intrinsic carries unusually wide uncertainty band."* Downgrade Stage-1 confidence one notch.

**Constraints:**
- Growth < discount rate over the long horizon (per Buffett 2003 [TX 42221]).
- Stage-1 growth above 15% requires extraordinary justification (per Buffett 2003 [TX 42229]: above 10% is "not an easy hurdle," above 15% is "rarified atmosphere").

Stage-1 LENGTH per `moat_durability_tiers.md` (DO NOT stretch optimistically):
```
durability HIGH:           10–15 years
durability MODERATE:        7 years
durability LOW:             5 years
durability VULNERABLE:      forces Stage-0 PARTIAL per structural rule
```

## STEP 4 — Discount rate (ONE rate)

Per `references/discount_rate_logic.md`. Compute the Buffett rate:

```
nominal_30Y_Treasury    (WebFetch)
trailing_12m_core_PCE   (WebFetch)
real_long_bond = nominal_30Y_Treasury − trailing_12m_core_PCE

if real_long_bond ≥ 1.5%:           r = nominal_30Y_Treasury
if 0.5% ≤ real_long_bond < 1.5%:    r = nominal_30Y_Treasury + 1pp
if real_long_bond < 0.5%:           r = nominal_30Y_Treasury + 2pp
```

State the nominal 30Y, core PCE, real long-bond, cushion applied (if any), and final r. Also report the 10Y Treasury as a cross-check; if 10Y and 30Y diverge by more than 50 bp, flag in MOST FRAGILE ASSUMPTIONS.

**No ERP. No beta. No CAPM in the decision-relevant rate.** Same rate across all businesses.

For the illustrative CAPM rate (used only in Step 11 / Stage 8 output section, not for the decision):
```
r_capm = nominal_30Y_Treasury + ERP × beta_adjustment
  ERP = 4.0–5.0%
  beta_adjustment per moat tier (per discount_rate_logic.md illustrative-CAPM section)
```

Compute r_capm separately and surface only in the illustrative section.

## STEP 5 — Terminal growth (multiple guardrails)

ALL must hold:
```
g ≤ long_bond_yield
g ≤ normalized nominal GDP (USD: 2.0–3.0%; lower for declining-currency)
r − g ≥ 3pp
g ≤ industry_long_run_growth (FLAG, not hard rule)
```

Typical USD compounder today: g = 2.0–2.5%. For declining industries: g = 0% or negative — make the case.

## STEP 6 — Run methods per business class

Per `references/valuation_methods.md` matrix. For COMPOUNDER (full Buffett framework):

### M1 / M2 — owner-earnings DCF (single conservative case, Buffett rate)

Stage 1 explicit forecast (N years per moat tier) + Stage 2 fade (5 years, linear glide from Stage-1 rate to terminal g) + Stage 3 terminal (Gordon at terminal g; RONIC = WACC).

Show full DCF table: `Year | Owner Earnings | Discount Factor | PV`

Sum PV(Stage 1) + PV(Stage 2 fade) + PV(terminal) = total intrinsic.

Per-share intrinsic = total intrinsic / **CURRENT diluted shares outstanding** (from `dei/EntityCommonStockSharesOutstanding`).

**DO NOT divide by projected year-5 shares.** SBC's economic cost is already in the numerator via GAAP NI; using projected shares would triple-count. A separate optional sensitivity row may show intrinsic at projected year-5 shares but it is NOT the primary number.

Y1 convention (Hagstrom-canonical, mandatory): Y1 = base × (1+g), NOT Y1 = base. See `valuation_methods.md` M1.

### M3 — Reverse DCF (CROSS-CHECK; load-bearing)

At current market cap, solve for implied Stage-1 growth.

Run at:
- **Buffett rate (primary):** decision input. Compare implied growth to trailing 5y / 10y actuals, industry/TAM ceiling, research-b base rate.
- **CAPM rate (illustrative):** surface only in Stage 8 output section, decision-irrelevant.

Comparison denominator: MARKET CAP (NOT EV) per `owner_earnings.md`.

### M4 — TSR decomposition (CROSS-CHECK; feeds Stage-5 floor)

```
expected_forward_TSR = OE_yield_at_current_price
                     + organic_OE_growth (use Stage-1 growth)
                     + buyback_yield (positive ONLY if avg_buyback_price < intrinsic_conservative)
                     − share_issuance_dilution_yield (positive ONLY if avg_issuance_price >
                                                      intrinsic_conservative; else 0 or negative)
```

SBC: no separate term. Per `owner_earnings.md`, SBC is already netted into owner earnings.

Target: ≥ `e_floor` (10% default, user-configurable per ticker). Surface verdict.

### M5 — Greenwald EPV (CROSS-CHECK; downside floor)

`EPV = NOPAT / Buffett_rate` (no growth assumed; NOPAT from operating income × (1 − statutory tax)).

If EPV ≥ price × shares: growth is free → surface positively in MOST FRAGILE ASSUMPTIONS.
If EPV << price (typical for compounders): document the size of growth premium being paid.

### M6 — Buffett two-pillar (CROSS-CHECK; cash-rich balance sheets only)

Apply if non-operating assets > 10% of EV.

`intrinsic = per-share investments at market + per-share operating earnings × multiple`
- multiple: 10–12× pre-tax = 14–18× after-tax (per BRK 2010–2012 letters).

### Peer multiples (SANITY CHECK ONLY — never a decision input)

Read `raw/competitors.md` if present. Note premium/discount; flag whether justified by quality differential.

## STEP 7 — Sensitivity table (mandatory, mechanical)

Compute and display the following table:

| Input perturbed | Direction | Δ intrinsic (% of base) |
|---|---|---|
| Discount rate +1pp | down | ... |
| Discount rate −1pp | up | ... |
| Stage-1 growth +2pp | up | ... |
| Stage-1 growth −2pp | down | ... |
| Stage-1 length +2y | up | ... |
| Stage-1 length −2y | down | ... |
| Terminal g +0.5pp | up | ... |
| Terminal g −0.5pp | down | ... |
| Maintenance capex +20% relative | down | ... |
| Maintenance capex −20% relative | up | ... |
| **SBC ±20% (REQUIRED for SBC-heavy: SBC > 10% of revenue OR > 50% of |GAAP NI|)** | varies | ... |

Each row is a SINGLE-input perturbation of the same base case. **Not three scenarios** — narrative-driven optimist/pessimist content goes in the prose Stage 9 section.

SBC sensitivity row operational definition (when required): perturb assumed forward SBC magnitude by ±20% of current run-rate. Under GAAP-NI starting point, this flows through NI directly — a $1B SBC line at +20% becomes $1.2B, reducing NI by $200M, reducing owner earnings by $200M. Show resulting Δ intrinsic.

## STEP 8 — Margin of safety and buy trigger

Per `references/three_tier_decision.md` 3×3 matrix.

**Structural rule applied BEFORE the matrix:** VULNERABLE moat forces Stage-0 to PARTIAL (or TOO HARD). Apply.

Look up the cell:

| | Moat HIGH | Moat MODERATE | Moat LOW |
|---|---|---|---|
| **UNDERWRITABLE** | 25–30% | 30–35% | 35–40% |
| **PARTIAL** | 35–40% | 40–45% | 45–50%+ |

Apply modifier adders (after the cell):
- VULNERABLE-moat adder: use LOW column as base, +5pp
- Cyclical-overlay (+5pp if business class is COMPOUNDER but 5y EBIT margin std dev > 30% of mean)
- Reverse-DCF stretch (+5pp if reverse DCF implies Stage-1 growth > max(1.5× trailing 5y CAGR, 25% absolute over 5–7y))

Stack additively. Cap at 60% — above which the business should be reclassified TOO HARD.

```
Buy trigger = intrinsic_conservative × (1 − required_MoS)
```

## STEP 9 — Opportunity-cost floor check (Stage 5 of framework)

Per `references/discount_rate_logic.md` opportunity-cost section + `three_tier_decision.md`.

Compute `expected_forward_TSR` (per Step 6 M4 above).

Check: `expected_forward_TSR ≥ e_floor` (10% default, user-configurable).

If FAIL: trigger Stage-10 downgrade 3a.

## STEP 10 — Capital allocation tests (Stage 6 of framework)

Per `valuation_methods.md` Stage 6 (A/B/C). Compute:

**A. $1 retention test (per-share OE basis):** trailing 5y growth in per-share OE vs cumulative retained per-share OE. Flag if primary test fails.

**B. Buyback / issuance asymmetry:** check trailing buyback avg price vs intrinsic_conservative; check share issuance (incl. SBC vesting) avg price vs intrinsic_conservative. Flag if value-destroying.

**C. Look-through earnings:** apply only for holdco-style businesses with material equity portfolios.

If any flag fires, trigger Stage-10 downgrade 3d.

## STEP 11 — Tax normalization, future share count, cross-checks

(Same as prior versions of this agent — preserved.)

Read `step7_accounting.md`. If accounting agent flagged effective tax rate >5pp below US statutory, compute owner_earnings_normalized using statutory rate; run M1/M2 on both; conservative pick is the lower.

If accounting flagged ongoing tax audits with material amounts at stake: apply lower-bound tax-rate haircut. If valuation-allowance changes inflated recent NI: use 3-year average tax rate, not trailing.

Verify before writing output:
- M1 intrinsic uses current diluted shares (NOT projected year-5).
- Reverse DCF at Buffett rate gives growth ≤ trailing actuals when current price < buy trigger (sanity check).
- M5 EPV is consistent with M1/M2 trajectory (EPV should be < intrinsic for any growing business).
- Total CAP (Stage 1 + fade in M2) matches the moat-tier table.

## REQUIRED OUTPUT — exact section labels

Both CC and Codex use IDENTICAL labels. Reconciliation is a mechanical diff per section.

```
=== RATE ANCHOR ===
[per discount_rate_logic.md valuation-freshness header]

=== UNDERWRITEABILITY GATE ===
[UNDERWRITABLE | PARTIAL | TOO HARD; full evidence per underwriteability_gate.md template]
(If TOO HARD: optional reverse-DCF non-decision context only; STOP after this section.)

=== OWNER EARNINGS DERIVATION ===
[1986 formula applied starting from GAAP NI; conditional-on-starting-point table cited;
period; XBRL concepts; maintenance capex judgment shown; SBC handling explicit
(do NOT add back); WC-float treatment if SaaS]

=== DISCOUNT RATE ===
[Buffett rate per Step 4: nominal 30Y, core PCE, real long-bond, cushion (if any), final r.
10Y cross-check. Primary-source justification.
NO ERP, NO beta in this section.]

=== STAGE-1 GROWTH AND DURATION (single conservative case) ===
[9-indicator triangulation table; conservative pick (median or lower) with narrative anchoring;
Stage-1 length from moat tier; explicit divergence-flag if >5pp range]

=== TERMINAL GROWTH ===
[guardrails check; single terminal g]

=== INTRINSIC VALUE (per share, Buffett rate) ===
[ONE single-point number from the DCF. Full DCF table shown.
Per-share = total intrinsic / current diluted shares (NOT projected year-5).]

=== SENSITIVITY TABLE (mandatory, mechanical) ===
[The 10-row table from Step 7. SBC row REQUIRED if SBC > 10% of revenue or > 50% of |GAAP NI|.]

=== MARGIN OF SAFETY AND BUY TRIGGER ===
[3×3 cell from Step 8 + modifier adders. buy_trigger = intrinsic × (1 − MoS). 60% cap.]

=== OPPORTUNITY-COST FLOOR CHECK ===
[expected_forward_TSR computation; vs e_floor 10% default; PASS or FAIL]

=== CAPITAL ALLOCATION TESTS ===
[$1 retention test (per-share OE basis); buyback/issuance asymmetry; look-through if holdco.
Any flags fired feed Stage-10 downgrade 3d.]

=== REVERSE DCF (Buffett rate) ===
[Implied Stage-1 growth at current price; vs trailing 5y CAGR, industry-blend, 25% absolute ceiling.
Verdict on whether reverse-DCF stretch modifier fires (+5pp MoS).]

=== ILLUSTRATIVE — HOW THE VOLATILITY / CAPM SCHOOL WOULD VALUE THIS (not a decision input) ===
[Required disclaimer at top per discount_rate_logic.md illustrative-CAPM section.
r_capm = long_bond + ERP × beta_adjustment.
Same single conservative case re-run at r_capm.
Reverse DCF at r_capm (compare to Buffett-rate reverse DCF — surfaces rate sensitivity).
TSR decomposition (rate-independent).]

=== WHAT I'M MOST LIKELY WRONG ABOUT ===
[MANDATORY prose section, >200 words. Four required subsections per three_tier_decision.md Stage 9:
1. Case where intrinsic is materially higher than conservative estimate
2. Case where intrinsic is materially lower
3. Judgment on which is more likely (one paragraph, evidence-based, not probability-weighted)
4. Single piece of evidence that would change my mind (observable + time-bounded + precisely named)
If WC-float > 50% of OE: MUST explicitly address WC-float sustainability.]

=== MOST FRAGILE ASSUMPTIONS ===
[3–5 highest-leverage assumptions; what would change intrinsic by 20%+.
List which Stage-10 downgrades fired and why.]

=== VERDICT ===
[BUY / WATCHLIST / PASS per Stage-10 decision logic in three_tier_decision.md.
Sequential: base verdict from price vs intrinsic → apply downgrades.
Max 2 notches. Surface dispersion if sensitivity-table extremes exceed 30% of base.]
```

Apply claim labeling.

OUTPUT FILE: `{BASE}/steps/step9_valuation_cc.md`

## HANDOFF MESSAGE (after writing output)

Print exactly:
```
CC valuation complete. Next: switch to Codex terminal and run:
  $stock-research-codex {TICKER} --valuation
Codex will produce steps/step9_valuation_codex.md independently.
After Codex completes, switch back to CC and run:
  /stock-research {TICKER} --reconcile-valuation
```

## Verification B — DISPATCHED BY ORCHESTRATOR (not this agent)

Verification B is the arithmetic + input re-check of `step9_valuation_cc.md`. It MUST run outside this agent's invocation so an in-agent context cap does not abort it mid-run.

**The CRWD run exposed the same methodology bug for Verification B that the prior bug exposed for Verification D:** the valuation agent ran out of usage cap inside Verification B, forcing the orchestrator to fall back to inline verification anyway. The fix is to make orchestrator ownership explicit: this agent writes `step9_valuation_cc.md` and stops. The orchestrator runs Verification B after.

**This agent's responsibility ends after writing `step9_valuation_cc.md`.** Do not invoke any verification step here. The orchestrator handles it per `phases/step1e_pipeline.md` Phase 5A.b.
