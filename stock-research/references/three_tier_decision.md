# Decision logic — intrinsic value, buy trigger, opportunity-cost floor

**Note on filename:** this file is named `three_tier_decision.md` for backward compatibility with Codex's valuation precondition check. The framework inside is no longer three rate-tiers — it's one conservative intrinsic + buy trigger + opportunity-cost floor + illustrative CAPM parallel. CC and Codex both read this file.

The decision-relevant output of every valuation:

```
INTRINSIC VALUE       — ONE conservative estimate at the Buffett rate
                        (long-bond + mechanical real-rate cushion; per `discount_rate_logic.md`)
                        Output: a single per-share number from the DCF.
                        PLUS: mandatory mechanical sensitivity table (Stage 3 below).

BUY TRIGGER           — intrinsic_conservative × (1 − required_MoS)
                        MoS sized per the 3×3 matrix below.

OPPORTUNITY-COST      — Forward expected total return at current price ≥ e_floor
FLOOR CHECK             e_floor = 10% (Buffett 2003 default) OR ~7–8% (Munger S&P framing)
                        Per `discount_rate_logic.md`. SEPARATE from the discount rate.

CAPITAL-ALLOCATION    — $1 retention test (per-share-owner-earnings basis)
TESTS                   Buyback / issuance asymmetry vs intrinsic
                        Look-through earnings (holdco only)

ILLUSTRATIVE CAPM     — Same conservative case re-run at CAPM rate
PARALLEL                Clearly labeled non-decision; for the reader's information only.
```

---

## Why one conservative estimate, not a range or three scenarios

Buffett's own practice is single-point estimation with a "scream" filter [TX 61055]:

> *"It should be so obvious that you don't have to carry it out to tenths of a percent or hundredths of the percent. It should scream at you."*

Three labeled scenarios (pessimist / neutral / optimist) is the McKinsey/sell-side artifact. Munger 2014 [TX 61065]:

> *"some of the worst business decisions I've ever seen are those that are done with a lot of formal projections and discounts back... the higher mathematics, with more false precision, should help you. But it doesn't."*

Sensitivity to specific inputs is real and useful. **Three labeled scenarios are not.** The skill outputs ONE conservative number + a mandatory mechanical sensitivity table (per-input perturbations) + a Stage 9 prose section forcing narrative uncertainty into words rather than into precise-looking parallel DCFs.

---

## Margin of safety — the 3×3 matrix

Two axes: Stage-0 underwriteability (per `underwriteability_gate.md`) × Phase-4 moat-durability tier (per `moat_durability_tiers.md`).

### Structural rule (applied BEFORE the matrix)

Phase-4 **VULNERABLE** moat is by definition incompatible with Stage-0 **UNDERWRITABLE**. A vulnerable moat means cash flows are NOT defensibly forecastable for 10+ years. If both flags appear, reclassify Stage-0 to PARTIAL — or TOO HARD if the vulnerability is decisive. Apply BEFORE the matrix.

### The matrix

| | Moat HIGH (regulatory, brand-habit-stable, two-sided network) | Moat MODERATE (counter-positioning, scale in stable channel) | Moat LOW (tech-scale, brand+scale in fast-moving) |
|---|---|---|---|
| **UNDERWRITABLE** (10y+ predictable) | 25–30% | 30–35% | 35–40% |
| **PARTIAL** (moderate certainty, material disruption vectors) | 35–40% (rare — high moat but industry shifting) | 40–45% | 45–50%+ |
| **TOO HARD** | no valuation-based BUY/WATCHLIST/PASS | no valuation-based BUY/WATCHLIST/PASS | no valuation-based BUY/WATCHLIST/PASS |

### Modifier adders (applied AFTER the cell is selected)

- **VULNERABLE-moat adder:** use the LOW moat column as the base cell, then add **+5pp**. (Structural rule already forced Stage-0 to PARTIAL or TOO HARD; LOW column is the correct base because VULNERABLE is the next tier below LOW in the moat-durability ladder.)
- **Cyclical-overlay modifier (+5pp):** business class is COMPOUNDER but industry earnings are materially cyclical (semis equipment in chip cycles; auto parts in vehicle cycles; mining services in commodity cycles). Tagged in Phase 3 when 5y EBIT margin standard deviation > 30% of mean.
- **Reverse-DCF stretch modifier (+5pp):** reverse DCF at current price implies Stage-1 growth > max(1.5× trailing 5y CAGR, 25% absolute over 5–7 years). The absolute ceiling prevents high-growth SaaS from escaping the stretch test on relative-multiple alone.

Modifiers stack additively. **Cap at 60% total MoS.** Above 60%, the business should probably be reclassified TOO HARD — if MoS demands are that high, the cash flows aren't defensibly forecastable.

### Why this scaling

Buffett 2008 [TX 53670]:
> *"if we buy something like See's Candy as a business or Coca-Cola as a stock, we don't think we need a huge margin of safety because we don't think we're going to be wrong about our assumptions in any material way."*

See's / Coke sit in the top-left cell (~25–30% MoS). Buffett's empirical Coke 1988 entry was ~66% MoS below Hagstrom-computed intrinsic — the skill's MoS table is the lower bound of his observed practice.

For lower-tier moats (LOW, PARTIAL, VULNERABLE), the MoS scales up to reflect lower confidence in the underlying forecast. NOT in the rate — in the price.

### Buy trigger

```
Buy trigger = intrinsic_conservative × (1 − required_MoS)
```

Apply the MoS against the single conservative intrinsic estimate from Stage 3. Not against a range upper. Not against a "neutral" scenario.

---

## Opportunity-cost expectancy floor

Per Buffett 2003 [TX 41277]:
> *"The 10% we mention. That's the figure we quit on. We don't want to buy equities where our real expectancy is below 10 percent... whether short rates are 6 percent or whether short rates are 1 percent."*

The 10% is NOT the discount rate. It is a SEPARATE forward-expected-return filter applied at current price, AFTER intrinsic value is computed.

```
expected_forward_TSR = owner_earnings_yield_at_current_price
                     + organic_owner_earnings_growth
                     + buyback_yield  (positive ONLY if avg_buyback_price < intrinsic_conservative;
                                       else 0 or negative)
                     − share_issuance_dilution_yield  (positive ONLY if avg_issuance_price >
                                                      intrinsic_conservative; else 0 or negative)

  (SBC: no separate term. Per `owner_earnings.md`, SBC is always netted into owner earnings
   (charged once via GAAP NI). OE growth and OE yield already reflect SBC's economic cost.
   Adding a separate SBC dilution term here would double-count.)

Check: expected_forward_TSR ≥ e_floor
  e_floor = 10% (Buffett 2003 default) OR
            ~7–8% (S&P-500 long-run real / after-tax; Munger opportunity-cost framing
                  per [TX 14210, 81870])
  User-configurable per ticker; default 10%.
```

If `expected_forward_TSR < e_floor` even with intrinsic value > current price, downgrade verdict — return at current price doesn't clear opportunity cost.

Munger 2008 [TX 55299]:
> *"if I have something available that I think will give me 8 percent for sure and I can buy all I want of it, and you've got a perfectly good investment that I think will earn 7, I don't have to waste 5 minutes with you."*

---

## Decision logic (sequential, with explicit precedence)

```
Step 1 — TOO HARD gate
  If Stage 0 = TOO HARD:
    → "No valuation-based decision. Business does not clear certainty filter."
    → EXIT. No BUY/WATCHLIST/PASS emitted.
    → (Optional reverse-DCF read of market expectations allowed per
       underwriteability_gate.md, clearly labeled non-decision.)

Step 2 — Compute base verdict from price vs. intrinsic
  If price > intrinsic_conservative:                base = PASS
  If buy_trigger < price ≤ intrinsic_conservative:  base = WATCHLIST
  If price ≤ buy_trigger:                            base = BUY

Step 3 — Apply downgrades (each independently reduces base by ONE notch:
                            BUY → WATCHLIST → PASS; PASS stays PASS)

  3a. Opportunity-cost floor:
       If expected_forward_TSR < e_floor:           −1 notch

  3b. Stage-0 PARTIAL:
       If Stage 0 = PARTIAL (not UNDERWRITABLE):    −1 notch

  3c. Reverse-DCF implausibility:
       If reverse DCF at current price implies Stage-1 growth >
       max(1.5× trailing 5y CAGR, industry-blend × 1.5, 25% absolute over 5–7y):
                                                    −1 notch
       (Absolute ceiling prevents high-growth SaaS from escaping on
        relative-multiple alone.)

  3d. Capital-allocation flag:
       If avg buyback price > intrinsic_conservative
       OR $1 retention test fails per `valuation_methods.md` Stage 6A
       (trailing 5y retained per-share owner earnings have NOT produced
        ≥ commensurate growth in normalized per-share owner earnings;
        market-value test is secondary confirmation over 10y window only):
                                                    −1 notch
       (Apply at most once even if both fire — they correlate.)

Step 4 — Final verdict = base after all downgrades.

Step 5 — Always surface in MOST FRAGILE ASSUMPTIONS:
  - Which downgrades fired
  - Sensitivity-table extremes (Stage 3 of valuation file)
  - The "evidence that would change my mind" item from Stage 9
```

Maximum downgrade is 2 notches (BUY → PASS). **A BUY verdict requires that NONE of the four downgrades fire** — i.e., UNDERWRITABLE certainty, reverse DCF inside defensible range, capital allocation good, opportunity-cost floor cleared, AND price ≤ buy_trigger. This is intentionally strict — Buffett's empirical buys cleared all five tests.

---

## What I'm most likely wrong about (Stage 9 prose section, MANDATORY)

This is the qualitative-uncertainty section that the rejected three-scenario structure would have lived in. Forced into prose, the analyst must engage with failure modes rather than generating three precise-looking numbers from the same fuzzy guesses.

Required subsections in `step9_valuation_cc.md` (and Codex's equivalent):

1. **The case where intrinsic is materially higher than my conservative estimate.** What would have to be true? What specific evidence would confirm or refute it? What's my honest probability assessment?

2. **The case where intrinsic is materially lower.** Same structure. What would have to be true for the business to underperform my conservative case?

3. **My judgment on which is more likely, given current evidence.** Not probability-weighted math (Buffett rejects that). One-paragraph honest read: *"I think the downside case is more / less likely than the upside case because [specific evidence]."*

4. **The single piece of evidence that would change my mind.** Must be:
   - **observable** in a publicly disclosed metric (10-K / 10-Q / 8-K / earnings call)
   - **time-bounded** (a specific report or window, e.g., "by Q3 FY27" or "in the next 10-K")
   - **named precisely** (e.g., "Q3 FY27 revenue growth below 18%" — NOT "growth slows materially")
   
   Unfalsifiable phrasing fails the section's purpose.

This section is where calibration actually happens. A reader 5 years later can audit not just the number but the reasoning that produced it.

---

## Sources

- 1986 letter [LT 10485]: owner earnings as the relevant valuation figure
- 1992 letter [LT 17961]: margin of safety as cornerstone — *"If we calculate the value of a common stock to be only slightly higher than its price, we're not interested in buying."*
- 2003 meeting [TX 41277, 43151]: 10% expectancy floor; ONE MoS at the end, not stacked
- 2008 meeting [TX 53670, 55290, 55299]: MoS scaled to certainty; opportunity-cost framing
- 2014 meeting [TX 61055, 61065]: "scream" test; rejection of formal scenarios
- Research (a): Buffett's empirical Coke 1988 ~66% MoS
- Research (b): durability tier evidence base for the 3×3 matrix axes
