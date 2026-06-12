# Valuation methods catalog — six methods + business-type matrix

The skill computes intrinsic value via the Buffett framework: Stage-0 underwriteability gate → owner earnings (Stage 1) → Buffett rate (Stage 2) → ONE conservative DCF (Stage 3) → margin of safety (Stage 4) → opportunity-cost floor check (Stage 5) → capital-allocation tests (Stage 6) → optional two-pillar (Stage 7) → illustrative CAPM parallel (Stage 8) → "what I'm wrong about" prose (Stage 9) → decision logic (Stage 10).

Methods are NOT averaged — they are typed by which decision input they feed and which business class they apply to. The decision rests on ONE conservative intrinsic value (M1/M2 result), validated by cross-checks (M3 reverse DCF, M4 TSR, M5 EPV).

---

## The six methods

### M1 — Hagstrom owner-earnings DCF (primary decision method for the single conservative case)

- Owner earnings per `owner_earnings.md` (1986 letter formula, starting from GAAP NI)
- Stage 1: explicit forecast at the triangulated conservative growth rate, for N years (N = moat-durability tier per `moat_durability_tiers.md`)
- Stage 2: 5-year linear fade from Stage-1 rate to terminal g
- Stage 3: Gordon perpetuity at terminal g (per `discount_rate_logic.md` guardrails); RONIC = WACC convention so growth creates no incremental terminal value
- Discount rate: Buffett rate per `discount_rate_logic.md`
- No equity risk premium added.

**Y1 convention (Hagstrom-canonical, mandatory):** Y1 = first PROJECTION year = base × (1+g), NOT Y1 = base year. So if Y0 (most recent actual) OE = $828M and g = 15%, then Y1 = $952.20M, Y10 = $3,349.72M. Getting this wrong understates intrinsic by ~13% (verified 2026-05-09 against Hagstrom Coke 1988 Table 8.1: correct convention reproduces $48,393M vs target $48,377M; wrong convention computes $42,081M).

**Output: ONE per-share intrinsic value number.** Plus the mandatory mechanical sensitivity table (per `agents/valuation.md` Stage 3 template).

### M2 — Three-stage with fade (alternative DCF shape for the same conservative case)

Functionally similar to M1; same Buffett rate, same conservative inputs. The "three-stage" refers to the FORECAST SHAPE (explicit Stage 1 + fade Stage 2 + terminal), not to three scenarios.

- Total CAP (competitive advantage period) = Stage-1 length per moat tier + 5y fade
- Stage 1 (years 1 to N1): explicit forecast at Stage-1 base growth, N1 = total CAP − 5
- Stage 2 (years N1+1 to N1+5): linear fade in both growth and RONIC toward terminal
- Stage 3 (terminal): RONIC = WACC; g per `discount_rate_logic.md` guardrails

Run at the Buffett rate only (no parallel CAPM rate in the decision sections). The illustrative CAPM rate is run separately in Stage 8 (see below).

### M3 — Reverse DCF (CROSS-CHECK; mandatory; load-bearing)

At current market price (× shares = market cap), solve for the implied Stage-1 growth.

**This is the load-bearing cross-check.** It answers "what growth is the market pricing?" — independent of the analyst's own growth forecast. If the implied growth is materially above any defensible trajectory, the price is unsustainable regardless of the analyst's own intrinsic estimate.

Run at:
- **Buffett rate (primary):** what growth must happen for an unlevered long-horizon owner to earn the Buffett-rate return?
- **CAPM rate (illustrative, decision-irrelevant):** what growth does the volatility school imply? Shown only in Stage 8.

Compare implied growth to:
- Trailing 5y / 10y revenue and owner-earnings CAGR
- Industry/TAM ceiling (step4_industry.md if present)
- Research-b empirical durability tiers
- Buffett 2003 [TX 42229]: above 10% sustained is "not an easy hurdle"; above 15% is "rarified atmosphere"

**Decision use:** feeds Stage-10 downgrade rule 3c (reverse-DCF implausibility) — triggers downgrade if implied growth > max(1.5× trailing 5y CAGR, industry-blend × 1.5, 25% absolute over 5–7 years).

**IMPORTANT — comparison denominator: MARKET CAP, not EV.** Owner earnings is levered (NI-derived). Per `owner_earnings.md`.

### M4 — TSR decomposition (CROSS-CHECK; feeds Stage-5 opportunity-cost floor)

```
expected_forward_TSR = owner_earnings_yield_at_current_price
                     + organic_owner_earnings_growth
                     + buyback_yield  (positive ONLY if avg_buyback_price < intrinsic_conservative)
                     − share_issuance_dilution_yield (positive ONLY if avg_issuance_price >
                                                      intrinsic_conservative; else 0 or negative)
```

SBC has no separate term — per `owner_earnings.md`, SBC is always netted into owner earnings, so OE yield and OE growth already reflect SBC's economic cost. Adding a separate SBC dilution term would double-count.

**Decision use:** feeds Stage-5 opportunity-cost floor check (per `discount_rate_logic.md` and `decision_logic.md`). If forward TSR < e_floor (10% default), Stage-10 downgrade 3a fires.

### M5 — Greenwald EPV (CROSS-CHECK; downside floor)

```
EPV = NOPAT / Buffett rate    (no growth assumed)
```

Per `discount_rate_logic.md`, use the Buffett rate (not the CAPM rate) for EPV. EPV at the Buffett rate tests "what is this business worth at the current rate with no growth?"

- If EPV ≥ price × shares: growth is free → strong size-up signal; surface in MOST FRAGILE ASSUMPTIONS (positive direction).
- If EPV << price (typical for compounders): growth premium being paid is large; require harder evidence on Stage-1 growth. Surface as positive-cross-check input to Stage-10 downgrade 3c (reverse-DCF implausibility).

### M6 — Buffett two-pillar (CROSS-CHECK; cash-rich balance sheets only)

Per Buffett 2007 [LT 26680]: *"Berkshire has two major areas of value. The first is our investments... Berkshire's second component of value is earnings that come from sources other than investments."*

```
intrinsic = per-share investments (at market) + per-share operating earnings × multiple
multiple: 10–12× pre-tax = 14–18× after-tax (per BRK 2010–2012 letters)
```

**Apply ONLY when non-operating assets > 10% of EV.** Examples: Apple 2016 ($215B cash), Berkshire, holding companies. CRWD precedent: $4.5B net cash = 3.4% of EV → skip.

Don't blend non-operating cash into operating earnings — that double-counts the interest income.

### Peer multiples (SANITY CHECK ONLY — never a decision input)

Read `raw/competitors.md` if present. Compute EV/EBITDA, P/E, FCF yield vs peer median. Note premium/discount.

Use language like: *"TICKER trades at X% premium/discount to peer median on EV/EBITDA. Quality differential per step5/step6: business [is/isn't] meaningfully better than peers. Premium [is/isn't] justified."*

Peer multiples DO NOT feed the verdict. They're context for the reader.

---

## Stage 6 — Capital-allocation tests (modifies intrinsic estimate or triggers Stage-10 downgrade)

Three explicit checks on management's ability to compound owner value:

### Stage 6A — The $1 retention test (per-share-owner-earnings basis)

Per Berkshire 1984 owner principle [LT 4604]: every $1 retained must produce ≥ $1 of value created over time.

**Primary test:** trailing 5y growth in normalized per-share owner earnings should exceed cumulative retained per-share owner earnings over the same period. This tests capital allocation directly — does management compound owner earnings per share on the capital they retain?

**Secondary confirmation:** trailing 10y growth in per-share market value should be at least commensurate with retained per-share owner earnings, after smoothing multiple compression/expansion. Use 10y window to dampen multiple cycles; flag if 5y test passes but 10y market test fails — that's a divergence worth investigating.

**Why primary is per-share-OE not per-share market value:** multiple compression/expansion can distort the market-value test in short windows (a great business mis-classifies in a bear market; a mediocre one passes in a bull market). The per-share-owner-earnings test is the load-bearing one.

If primary test fails, downgrade Stage-3 growth assumptions and flag in Stage-10 downgrade 3d.

### Stage 6B — Buyback / issuance asymmetry rules

Per Buffett 1985 [LT 5990]: repurchases create per-share value only when done below intrinsic. Above intrinsic, they destroy value. **The same rule applies in mirror to share issuance.**

- Buybacks below intrinsic_conservative → positive per-share value created
- Buybacks above intrinsic_conservative → per-share value destroyed (flag for Stage-10 downgrade 3d)
- Share issuance below intrinsic_conservative → per-share value destroyed (flag)
- Share issuance above intrinsic_conservative → per-share value created

For SBC-heavy SaaS, follow-on offerings and secondaries should be checked symmetrically — issuance at depressed prices is value-destroying even if accounting treats it as "raising capital."

Feeds Stage 5 TSR decomposition (buyback_yield term only positive if avg_buyback_price < intrinsic_conservative).

### Stage 6C — Look-through earnings (holdco-only)

Per Buffett 1991 [LT 16310]: for businesses with material equity portfolios (Berkshire-style, asset managers, holding companies), add investee retained earnings (less notional tax) to reported earnings.

Skip for typical operating businesses.

---

## Business-type → method matrix (with modifiers)

| Primary class | Primary DCF method | Required cross-checks | Skip / flag |
|---|---|---|---|
| **COMPOUNDER** | M1 or M2 (single conservative case at Buffett rate) | M3 (reverse DCF — load-bearing), M4 (TSR), M5 (EPV); M6 if cash-rich | — |
| **CYCLICAL** | M1 with mid-cycle normalized OE; M3 | M5 | M2 fade (cycles ≠ fades); flag with cyclical-overlay modifier per `decision_logic.md` |
| **CAPITAL-INTENSIVE** | M1 with forensic maint-capex; M3 | M5; peer multiples | — |
| **CAPITAL-INTENSIVE + COMPOUNDER** modifier | M1 + M2 (railroads with margin runway, e.g., BNSF) | M3, M5 | — |
| **INSURANCE / FLOAT** | NONE — exit Stage 1 | use book value + ROE; flag as out-of-DCF-scope | M1–M6 |
| **FINANCIAL** (banks, asset managers) | NONE — exit Stage 1 | use adjusted book + ROE | M1–M6 |
| **REIT / REAL ESTATE** | NONE — exit Stage 1 | use AFFO multiple, NAV, cap rate | M1–M6 |
| **HOLDING COMPANY** | sum-of-parts per segment, then aggregate (with Stage 6C look-through) | apply primary method per segment | M1–M6 at top level |
| **ASSET-HEAVY / SOTP** | M5 + replacement cost | M1; flag if EPV << price | M2 fade |
| **NO-CURRENT-FCF** (venture-like) | NONE — Stage 0 TOO HARD | use optionality framework; mark "speculative" | M1–M6 |
| **TOO-HARD** | NONE — Stage 0 TOO HARD | "no defensible valuation" finding; optional reverse-DCF context per `underwriteability_gate.md` | M1–M6 |

---

## Modifiers tune the methods (don't change the matrix row)

- `+SBC-heavy` (SBC > 10% of revenue): apply conditional-on-starting-point table per `owner_earnings.md`; include SBC sensitivity row in Stage 3 sensitivity table.
- `+capital-light` (<5% revenue maintenance capex): OE ≈ NI (after non-real-amort add-back); M5 EPV easier to compute reliably.
- `+regulatory-moat`: Stage-1 length to upper end of band per research (b).
- `+network-effects`: same.
- `+brand-habit-stable`: same.
- `+cyclical-overlay`: even on a compounder primary class, normalize through the cycle in M1; do NOT use trailing TTM as base. Triggers +5pp MoS adder per `decision_logic.md`.
- `+foreign-currency`: compute intrinsic in reporting currency, then convert via ADR ratio to USD share price.

---

## Method weights by business type (for reconciliation phase)

When CC and Codex disagree, the reconciliation phase weights methods this way:

```
COMPOUNDER:        M1 or M2 single conservative case anchors intrinsic
                   M3 reverse DCF is the diagnostic that bridges (load-bearing)
                   If M5 EPV ≥ price, that's load-bearing — surface as positive signal

CYCLICAL:          M1 mid-cycle normalized is primary
                   M5 EPV is the meaningful floor
                   Reverse DCF still valuable

CAPITAL-INTENSIVE: M1 with forensic maint-capex investigation; if maint-capex
                   estimate diverges between CC/Codex by >20%, that's the
                   load-bearing reconciliation question
```

---

## Stage 8 — Illustrative CAPM parallel (decision-irrelevant)

After the Buffett valuation is complete, run the SAME single conservative case at the CAPM rate as a clearly-labeled illustrative parallel. Section header in `agents/valuation.md` output:

```
=== ILLUSTRATIVE — HOW THE VOLATILITY / CAPM SCHOOL WOULD VALUE THIS (not a decision input) ===
```

Compute and present:
- CAPM rate per `discount_rate_logic.md` illustrative-CAPM section
- Same single conservative case (same growth, same length, same maintenance, same SBC) re-run at the CAPM rate
- Reverse DCF at current price at BOTH the Buffett rate AND the CAPM rate — comparison shows how much of "what the market is pricing" comes from the rate vs. the growth assumption
- TSR decomposition (one version; CAPM rate doesn't change TSR math)

State up front, citing Buffett 1998 [TX 19938]: *"we think all the capital asset pricing model-type reasoning with different rates of risk-adjusted return... we think it is nonsense."* The reader sees both lenses and why the volatility lens is rejected as a decision input.

---

## Sources

- 1986 letter [LT 10467]: owner-earnings formula
- 1991 letter [LT 16310]: look-through earnings (Stage 6C)
- 1984 letter [LT 4604]: $1 retention test (Stage 6A)
- 1985 letter [LT 5990]: buyback asymmetry (Stage 6B)
- 1992 letter [LT 17912]: Williams formula
- 2003 meeting [TX 41141, 42221, 42229, 43151]: same rate across all securities; growth-rate paradox; one MoS at the end
- 2007 letter [LT 26680]: Berkshire two-pillar (M6)
- 2008 meeting [TX 53670]: MoS scaled to certainty
- 2014 meeting [TX 61055, 61065]: scream test; rejection of formal projections
- Hagstrom, *The Warren Buffett Way*, Ch 8 (M1 template; Coke worked example)
- Greenwald, *Value Investing* (M5 EPV)
- Terry Smith, Fundsmith annual letters (M4 TSR decomposition)
- McKinsey, *Valuation* (Koller, Goedhart, Wessels) — value-driver formula for the M2 fade structure
- Research (a) `Feedbak/(a) BuffettMunger valuation methodology.md` — primary-source synthesis
- Research (c) `Feedbak/(c) DCF methodology for compounders.md` — practitioner literature (note: CAPM/ERP elements are documented as illustrative only here, not decision inputs)
