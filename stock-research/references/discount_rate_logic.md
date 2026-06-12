# Discount rate and terminal growth — operational rules

This file is the methodology for the rate in the denominator of every DCF the skill produces. CC and Codex both read this file. Any change here must be coordinated with the user as message bus (per `CLAUDE.md`).

The framework is grounded in 30 years of Buffett and Munger primary sources (Berkshire annual meeting transcripts 1994–2022 + shareholder letters 1977–2024). CC and Codex independently converged on the same framework after end-to-end reads of both source files.

---

## The decision-relevant rate

**ONE rate. Same rate across all businesses.** No ERP. No beta. No CAPM. Risk is handled via the Stage-0 underwriteability gate (`underwriteability_gate.md`), the margin of safety on price (`decision_logic.md`), and the cash-flow predictability filter — NOT in the rate.

### Tenor: 30-year US Treasury yield

Buffett says "long-term government rate" and never specifies tenor. The skill defaults to 30Y because:

1. Hagstrom's worked Coke example uses 30Y.
2. The "remaining life of the asset" forecast (Buffett 1992 letter [LT 17912]) is conceptually perpetual; a long-duration anchor matches.
3. Buffett's own context (1993 letter, 1996 meeting) was 30Y.

Report the 10Y as a cross-check. If 10Y and 30Y diverge by more than 50 bp, flag in MOST FRAGILE ASSUMPTIONS of the valuation file.

### Cushion trigger (skill policy, mechanical)

Buffett 1993 letter and 1997 meeting [TX 8966]: *"There may be times, when in a very — because we don't think we're any good at predicting interest rates, but probably in times of very — what would seem like very low rates — we might use a little higher rate."*

Buffett never gave specific thresholds. The skill operationalizes this judgmentally — **label this as skill policy, derived from but not literally stated by Buffett**:

```
real_long_bond = nominal_30Y_Treasury − trailing-12m core PCE inflation

if real_long_bond ≥ 1.5%:           r = nominal_30Y_Treasury    (no cushion)
if 0.5% ≤ real_long_bond < 1.5%:    r = nominal_30Y_Treasury + 1pp
if real_long_bond < 0.5%:           r = nominal_30Y_Treasury + 2pp
```

The historical real long-bond yield averages ~2%. The cushion kicks in only when real rates are unusually low. No discretionary "operator feels rates are suppressed" judgment — the rule decides.

### Worked example (today's environment)

- Nominal 30Y Treasury ≈ 5.0%
- Trailing-12m core PCE ≈ 3.0%
- Real long-bond ≈ 2.0% → ≥ 1.5% → no cushion
- **r = 5.0%**

Sensitivity:
- If core PCE rose to 4.5% with nominal 30Y unchanged: real = 0.5%, in [0.5%, 1.5%) → +1pp → r = 6.0%.
- If nominal 30Y fell to 3.5% with core PCE at 3.0%: real = 0.5% → +1pp → r = 4.5%. The cushion narrows but doesn't eliminate the rate decline. Buffett 2017 [TX 109773]: *"interest rates are to the value of assets what gravity is to matter."* The rate must move with rates; the cushion dampens extremes only.

### Pre-tax vs after-tax basis

Owner earnings (Stage 1, per `owner_earnings.md`) are after-tax (start from GAAP Net Income). The Treasury yield is pre-tax. Buffett discounts after-tax cash flows at the gross Treasury rate without haircutting the rate for tax — this is mildly inconsistent in strict economics but it's his stated practice. Buffett 1994 meeting: *"discounting future after-tax streams of cash at at least a 10 percent rate."*

The skill follows the same convention. Document explicitly in every valuation file's header: *"Owner earnings are after-tax (NI-derived). Discount rate is the gross long-term Treasury yield per Buffett's practice; no tax haircut applied to the rate."*

### Same rate across businesses

Buffett 2003 [TX 41141]: *"the question on discount rates, we use the same discount — I mean in theory — we would use the same discount rate across all securities, because if you really knew the cash they were going to produce, you know, that would take care of it."*

Differentiation between businesses happens in:
- **Numerator** (cash flows — growth, length, maintenance reinvestment, working capital)
- **Stage-0 gate** (whether the business clears the certainty filter at all)
- **Margin of safety** (sized per the 3×3 matrix in `decision_logic.md`)

NOT in the rate.

---

## What this rule rejects (with primary-source citations)

### No equity risk premium

Buffett 1997 [TX 8968]: *"we don't put the risk factor in, per se, because essentially, the purity of the idea is that you're discounting future cash. And it doesn't make any difference whether cash comes from a risky business or a safe business — so-called safe business."*

Buffett 1997 [TX 8990]: *"If you say I'm going to stick an extra 6 percent in on the interest rate to allow for the fact [that the business is risky] — I tend to think that's kind of nonsense. I mean, it may look mathematical. But it's mathematical gibberish in my view."*

### No CAPM, no beta

Buffett 1998 [TX 19938]: *"we think all the capital asset pricing model-type reasoning with different rates of risk-adjusted return and all that, we tend to think it is — well, we don't tend to — we think it is nonsense."*

Munger 1998 [TX 19947]: *"This great emphasis on volatility in corporate finance we just regard as nonsense."*

Buffett 1998 [TX 19953]: *"If we have a business about which we're extremely confident as to the business result, we would prefer that it have high volatility than low volatility. We will make more money out of a business where we know where the endgame is going to be if it bounces around a lot."* Volatility is opportunity for an unlevered long-horizon cash buyer, not risk to discount for.

### No risk-adjusted discount rate

Buffett 1998 [TX 19932]: *"we don't say, 'Well, we don't know what's going to happen, so therefore we'll discount it at 9 percent instead of 7 percent,' some number that we don't even know. That is not our way to approach it."*

Buffett 1998 [TX 19936]: *"We feel that once it passes a threshold test of being something about which we feel quite certain, that the same discount factor tends to apply to everything."*

---

## Risk handling (NOT in the rate)

Per Buffett's repeated framing, risk lives in three places — none of them the denominator:

1. **Stage-0 underwriteability gate** (`underwriteability_gate.md`): if cash flows aren't defensibly forecastable, walk away. Don't compensate with a fatter discount rate.
   - Buffett 1998 [TX 19927]: *"We look at riskiness, essentially, as being sort of a go/no-go valve... if we think we simply don't know what's going to happen in the future... we just give up."*

2. **Margin of safety on price** (`decision_logic.md` MoS matrix): demand a meaningful gap between intrinsic and price.
   - Buffett 1998 [TX 15075]: *"we adjust by simply trying to buy it at a big discount from that present value calculated using the risk-free interest rate."*

3. **Circle of competence**: only underwrite what you understand.
   - Buffett 1997 [TX 8984]: *"we don't want to go below a certain threshold of understanding."*

---

## Opportunity-cost expectancy floor (SEPARATE from discount rate)

The "10%" attributed to Buffett is NOT a discount rate — it is a forward-expected-return filter applied at current price, AFTER intrinsic value is computed.

Buffett 2003 [TX 41277]: *"The 10% we mention. That's the figure we quit on. We don't want to buy equities where our real expectancy is below 10 percent... whether short rates are 6 percent or whether short rates are 1 percent."*

Munger 2008 [TX 55290]: *"The concept of a hurdle rate makes nothing but sense, and yet a lot of terrible errors are made by people who are talking about hurdle rates."*

The skill applies `e_floor = 10%` as default. User-configurable per ticker — alternative anchor is the S&P-500 long-run real/after-tax return (~7–8%) per Munger's opportunity-cost framing [TX 14210, 81870]. Operationalized in Stage 5 of `decision_logic.md`. NOT applied here in the rate.

---

## Terminal growth — multiple guardrails (ALL must hold)

```
g ≤ long_bond_yield                  (Damodaran's hard rule; matches Buffett's "growth > rate = infinity" point at TX 42221)
g ≤ normalized nominal GDP            (USD: 2.0–3.0%; lower for declining-currency regimes)
discount_rate − g ≥ 3pp               (mathematical safety margin; flag if violated)
g ≤ industry_long_run_growth          (FLAG, not hard rule — hard to operationalize for diversified businesses)
```

For declining industries (newspapers, traditional retail, terminal-decline categories), `g` may be 0% or negative. Force the agent to make this case explicitly rather than defaulting to 3%.

Today (long bond ~5%): typical USD compounder `g = 2–2.5%`. **Setting g = 4.5% because long bond is 4.5% is mechanically wrong** — the GDP and r−g constraints bind first.

---

## Illustrative-CAPM section (decision-irrelevant)

**This section is presented after the Buffett valuation in every valuation file, clearly labeled as illustrative.** It does NOT feed BUY/WATCHLIST/PASS.

The user requested this section so the reader can see how the volatility / sell-side school would value the same business. Per the user: *"Then I would like to have a section (that doesn't influence buy/keep/sell decision) that could calculate using other methods also based in volatility JUST TO SHOW ME HOW OTHERS MAY CALCULATE IT."*

### CAPM rate formula

```
r_capm = long_bond + ERP × beta_adjustment

ERP = 4.0–5.0%  (Damodaran-consistent)
beta_adjustment per moat tier (research-b durability ladder):
  Regulatory + statutory:                    0.85
  Two-sided network:                         0.85
  Brand + habit stable:                      0.90
  Pure scale economies:                      0.95
  Brand + scale in fast-moving tech:         1.05
  Cyclical / capital-intensive overlay:      1.10
```

Today's environment (long bond ~5%): typical compounder r_capm ≈ 9–10%.

### Required disclaimer at the top of this subsection

Every valuation file must include this exact framing at the top of the illustrative-CAPM subsection:

> *"This calculation uses the CAPM / sell-side methodology (long-bond + ERP × beta). It is presented as an illustrative parallel showing how the volatility school would value the same business. It is NOT a decision input. The buy/keep/sell verdict uses only the Buffett rate above. Buffett 1998: 'we think all the capital asset pricing model-type reasoning... is nonsense.' Volatility is opportunity for an unlevered long-horizon buyer, not risk."*

---

## Valuation freshness rule

Per Buffett 2017 [TX 109773]: *"interest rates are to the value of assets what gravity is to matter."* When the long-bond moves materially after a valuation is written, intrinsic values move with it.

**Re-run trigger:** if the nominal 30Y Treasury moves more than ±75 bp between the valuation date and the decision date, the intrinsic value must be re-computed before any BUY/WATCHLIST/PASS action.

Every valuation file's header must document the rate-as-of-valuation so the trigger is checkable. Format:

```
=== RATE ANCHOR ===
30Y Treasury (valuation date YYYY-MM-DD): X.XX%
Trailing-12m core PCE: Y.YY%
Real long-bond: Z.ZZ% → [no cushion | +1pp cushion | +2pp cushion]
Discount rate applied: r = N.NN%
```

---

## Sources

- Berkshire annual meeting transcripts 1994–2022 (especially 1996, 1997, 1998, 2000, 2003, 2008, 2014, 2017)
- Berkshire shareholder letters 1977–2024 (especially 1986 Scott Fetzer appendix, 1989, 1992 Williams quote, 1993, 1994 Owner's Manual)
- Hagstrom, *The Warren Buffett Way*, Chapter 8 (worked Coke example; long-bond yardstick)
- Damodaran, "The D rate is a receptacle for your hopes and fears" (Myth 4.4) — for the rejected CAPM-school view documented here as illustrative-only
- Research (a) `Feedbak/(a) BuffettMunger valuation methodology.md` — primary-source synthesis

Specific line citations: [TX 8964, 8966, 8968, 8984, 8990, 14150, 14210, 15075, 18495, 19927, 19932, 19936, 19938, 19947, 19953, 21068, 24026, 41141, 41277, 42221, 55290, 81870, 109773]; [LT 10467, 17912, 17961, 35528].
