# Owner earnings — operational rules

This file is the methodology for the cash-flow base in every DCF the skill produces. CC and Codex both read this file.

See also: `references/accounting_principles.md` — the broader interpretation framework that the accounting agent applies. The accounting agent produces the GAAP NI → **pre-valuation economic earnings bridge** that valuation consumes as its pre-Stage-1 baseline. Valuation then applies the maintenance-capex and working-capital rules below to convert economic earnings → final owner earnings.

## The 1986 letter formula — verbatim

From Buffett's 1986 Berkshire shareholder letter, Scott Fetzer purchase-accounting appendix [LT 10467]:

> *"If we think through these questions, we can gain some insights about what may be called 'owner earnings.' These represent (a) reported earnings plus (b) depreciation, depletion, amortization, and certain other non-cash charges such as Company N's items (1) and (4) less (c) the average annual amount of capitalized expenditures for plant and equipment, etc. that the business requires to fully maintain its long-term competitive position and its unit volume. (If the business requires additional working capital to maintain its competitive position and unit volume, the increment also should be included in (c). However, businesses following the LIFO inventory method usually do not require additional working capital if unit volume does not change.)"*

Buffett 1986 [LT 10485]: *"we consider the owner earnings figure, not the GAAP figure, to be the relevant item for valuation purposes — both for investors in buying stocks and for managers in buying entire businesses."*

---

## Canonical formula (starting from GAAP Net Income)

The skill's canonical owner-earnings formula. Apply this verbatim. Other starting points (OCF, adjusted FCF, non-GAAP) require the conditional-on-starting-point table below.

**Consume the accounting agent's bridge first.** Before applying the SBC / amortization / maintenance-capex rules below, read `steps/step7_accounting.md` for the `=== GAAP NI → PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===` and `=== OWNER-EARNINGS INPUT FLAGS FOR VALUATION ===` blocks.

The accounting agent has already quantified Tier-I earnings overstatement (non-real PPA amortization, post-2018 MTM separation, recurring "non-recurring" charges, pension normalization, M2 SBC handling per starting point). The valuation agent's owner-earnings derivation then applies the maintenance-capex and working-capital rules below to the **accounting-adjusted economic earnings**, not to raw GAAP NI. Document the bridge magnitude in the valuation file.

If the accounting agent's opt-out flag is RECOMMEND PARTIAL or RECOMMEND TOO HARD, the valuation file must explicitly acknowledge this and either proceed with low confidence or mark No-Buy. Silent GAAP consumption in the presence of a material accounting flag is forbidden.

**Symmetric handling for Conservative verdicts.** If the accounting agent's verdict is Conservative AND the `=== HIDDEN VALUE FROM CONSERVATIVE ACCOUNTING ===` block identifies specific items where reported numbers understate economic reality (over-reserved insurance, R&D fully expensed at a capital-generative firm, over-depreciated PP&E with replacement cost > book), the valuation agent must add those back to economic earnings (or to net asset value, per the line-item nature). Symmetric to the overstatement flow — do not silently ignore conservative understatement.

**Disagreement protocol.** If the valuation agent disagrees with the accounting bridge (e.g., believes accounting overstated an adjustment or missed one), it must explicitly document the disagreement and the alternative number. Silent re-derivation is forbidden. Disagreements escalate to Phase 5C reconciliation per the binding-unless-escalated cascade in `references/underwriteability_gate.md`.

```
Owner earnings = GAAP Net Income
              + D&A (real depreciation of real productive assets)
              + non-real amortization add-backs
                  (acquisition-related purchase-price-allocation amortization that does not
                   represent economic cost — per Buffett 2018 [LT 37831], typically ~80% of
                   GAAP amortization at acquisition-heavy firms)
              − Maintenance capex (NOT total capex; judgment per business class — see rules below)
              − Incremental working capital required to sustain unit volume
              + Working capital float net (e.g., deferred revenue growth net of AR growth for SaaS)
                  [SaaS-WC-float caveat below — analytical extension, NOT a literal 1986 rule]
```

### SBC is NOT added back

Per Buffett 2015 [LT 35528]:

> *"'Stock-based compensation' is the most egregious example. The very name says it all: 'compensation.' If compensation isn't an expense, what is it? And, if real and recurring expenses don't belong in the calculation of earnings, where in the world do they belong?"*

> *"Wall Street analysts often play their part in this charade, too, parroting the phony, compensation-ignoring 'earnings' figures fed them by managements."*

SBC is real compensation. GAAP Net Income already deducts it as a compensation expense. **Do NOT add it back.** Adding SBC back is the exact "compensation-ignoring earnings" practice Buffett calls the "most egregious" charade.

### Conditional-on-starting-point table

Different starting points imply different SBC handling. The danger is double-counting (subtracting SBC twice) or under-counting (forgetting it was added back). Apply this table strictly:

| Starting point | SBC handling | Per-share denominator |
|---|---|---|
| **GAAP Net Income** (preferred) | Do nothing — SBC already deducted in NI | Current diluted shares outstanding |
| **GAAP Operating Cash Flow (OCF)** | RE-DEDUCT SBC (OCF added it back as non-cash) | Current diluted shares outstanding |
| **Wall Street "Adjusted FCF" / "Free Cash Flow"** | RE-DEDUCT SBC (typically added back) | Current diluted shares outstanding |
| **Non-GAAP earnings / EPS-non-GAAP** | RE-DEDUCT SBC (added back by management) | Current diluted shares outstanding |

**Preferred starting point: GAAP Net Income.** It is the most transparent; SBC is unambiguously already deducted; the formula above is the literal Buffett 1986 form.

### Dilution presentation rule

SBC is charged ONCE in owner earnings (via the table above). The per-share denominator uses CURRENT diluted shares outstanding for the primary intrinsic-per-share calculation. Future dilution is implicitly captured because SBC's full cash-economic value is already in the numerator.

**Do NOT also divide by projected year-5 shares** — that triple-counts for SBC-heavy SaaS:
- Charged once in the numerator (SBC reduces NI)
- Charged again by projecting share count forward
- Decision-economics: massive understatement of intrinsic

A separate optional sensitivity row may show "intrinsic per share at projected year-5 share count" as a sensitivity check, but it is NOT the primary number.

### SBC-heavy GAAP-loss businesses — decision tree (added 2026-05-13 post-CRWD)

CRWD's reconciled valuation surfaced a real edge case: when current owner earnings are near-zero or negative because of SBC-heavy growth economics, applying the canonical rule above produces a multiplier with no meaningful base. The temptation is to start from issuer FCF and apply a dilution haircut on the denominator. That is an acceptable scenario / sensitivity, but NOT a substitute for canonical Buffett owner earnings.

Decision tree:

1. **Canonical Buffett OE remains the primary number.** If starting from OCF or any issuer FCF concept, re-deduct SBC per the conditional-on-starting-point table above and use current diluted shares per the Dilution presentation rule. This is the first attempt for every business, including SBC-heavy SaaS.

2. **If canonical OE is near-zero or negative** because SBC-heavy growth economics make current OE unusable, do NOT force a normal DCF off issuer FCF as "owner earnings." Forcing it produces a Buffett-style number that is methodologically not Buffett.

3. **Issuer FCF + dilution-haircut is allowed only as a clearly-labeled non-canonical scenario** — published alongside but not in place of the canonical treatment. Label inside the valuation file: `Non-canonical scenario: issuer FCF + dilution haircut. Does NOT feed primary buy/keep/sell.` Phase 5A.b Verification B enforces the label.

4. **Primary buy/keep/sell decision in this regime should lean on:**
   - **Mature after-SBC margin** — what SBC-as-percentage-of-revenue and operating margin will look like at steady-state scale, derived from the most mature comparable (Adobe / Salesforce / Microsoft Office at scale). The compounding case is the path from current SBC-heavy economics to that steady state.
   - **Reverse DCF** — what growth rate is the current price implying, and does it require unrealistic execution? Reverse DCF is unaffected by canonical-OE breakdown because it solves for growth given price.
   - **EPV floor** — the no-growth franchise value (after-tax EBIT × (1 − tax) / cost of capital), separate from any SBC-heavy compounding case. EPV anchors the downside.
   - **Underwriteability gate** — Stage-0 (`references/underwriteability_gate.md`). If the case requires the alternate framework to produce a buy number, that itself is a signal the business may be in PARTIAL or TOO HARD territory.

**Reverse-DCF base disclosure (per Codex 2026-05-13).** Reverse DCF is not fully independent of canonical-OE breakdown — it still needs a starting base. When applying any of the three bases above (canonical OE, mature after-SBC margin, non-canonical issuer FCF), the valuation file MUST state which base feeds the reverse-DCF solve and label any change of base explicitly. Phase 5A.b Verification B checks this disclosure exists.

In other words: when canonical OE breaks down, do not paper over the breakdown with an alternate definition of owner earnings. The breakdown is information about the business.

### SaaS WC-float caveat

The "+ working capital float net" line is an **analytical extension by analogy, NOT a literal 1986 rule.** Buffett's 1986 formula treats incremental WC as a SUBTRACTION when required to sustain unit volume. The skill extends this when working capital is a NET SOURCE (e.g., a SaaS where deferred revenue growth exceeds AR growth — customers prepay for services not yet delivered, creating float similar to insurance float per Buffett's float framework [LT 23116 / 26680]).

Two operational guardrails when including this line:

1. **Maturity caveat:** WC-float contribution scales with growth. As deferred-revenue growth slows toward steady state, the addback diminishes. Do NOT extrapolate growth-mode WC-float magnitudes through the fade or terminal periods. Apply the line only in Stage 1, with a fade to zero by terminal.

2. **Dominance flag:** if WC float exceeds 50% of owner earnings, the "what I'm most likely wrong about" Stage 9 prose MUST explicitly address WC-float sustainability — under what scenarios does the float reverse or shrink? Treat as a single-judgment risk on par with growth or moat.

---

## Three things routinely missed

1. **(c) is MAINTENANCE capex, not total capex.** Total capex includes growth investment that you do NOT subtract from owner earnings. For asset-light franchises (Coke, See's, software with low PP&E), reported D&A ≈ maintenance capex, so OE ≈ NI (after adding back non-real amortization). For capital-intensive businesses (BNSF, utilities, manufacturers), maintenance capex > D&A. Buffett 1986 [LT 10483]: *"The aggregate numbers we publish are estimates… all such numbers are imprecise and often seriously misleading."*

2. **Owner earnings ≠ free cash flow as Wall Street computes it.** Wall Street FCF = CFO − total capex (often with SBC added back). Buffett OE = NI + D&A + non-real amort − maintenance capex − incremental WC required + WC-float net. OE is *less conservative* than total-capex FCF for growing capital-light businesses (excludes growth capex) and *more conservative* than SBC-add-back FCF (deducts SBC implicitly via NI).

3. **Owner earnings ≠ EBITDA.** Buffett is hostile to EBITDA. 1989 letter [LT 14725]: *"To induce lenders to finance even sillier transactions, they introduced an abomination, EBDIT — Earnings Before Depreciation, Interest and Taxes... Such an attitude is clearly delusional."* 2015 letter [LT 33825]: *"When CEOs tout EBITDA as a valuation guide, wire them up for a polygraph test."*

---

## Maintenance vs growth capex — operational guidance

The hardest single judgment in owner earnings. Buffett: *"(c) must be a guess."*

```
Step 1: read total capex from XBRL (PaymentsToAcquirePropertyPlantAndEquipment)
Step 2: read D&A from XBRL (DepreciationDepletionAndAmortization)
Step 3: classify the business

ASSET-LIGHT (software, brands, payment networks; PP&E < 20% of revenue):
  Tied to PP&E growth rate:
    Steady-state (PP&E growing < 3%/yr): trailing 3-year average D&A (smooths noise)
    Growth-mode (PP&E growing ≥ 3%/yr):  current-year D&A (trailing avg lags actual asset base)
  Flag if total capex > 1.5× D&A consistently for 3+ years → growth capex dominates;
  use D&A as maint and treat excess as growth investment (NOT deducted from OE).

CAPITAL-INTENSIVE (railroads, utilities, manufacturers):
  Maintenance capex ≈ 60–80% of trailing total capex.
  MUST cite management's stated maint vs growth split (10-K Item 7, earnings calls).
  If management doesn't disclose: use 70% as default and flag as [HUMAN-VERIFY].
  BNSF post-2010 precedent: maintenance ≈ $2–2.5B against total ≈ $3.5–5B.
  Buffett 2018 [LT 37834]: *"depreciation charge understates our true economic cost."*

ACQUISITION-HEAVY:
  Add back ~80% of GAAP amortization as non-real (purchase-price-allocation, customer relationships).
  Keep ~20% as real (software, IP that genuinely depletes).
  Per Buffett 2014 [LT 33819]: at Berkshire, ~20% of amortization is real, ~80% non-real.

SBC-HEAVY (SBC > 10% of revenue):
  No special maintenance-capex rule — but require SBC sensitivity row in Stage 3 table.
  Apply the conditional-on-starting-point table above for SBC handling.

CYCLICAL:
  Maintenance capex ≈ trough-period total capex (avoids inflating off peak years).
  Use 5–7 year history to identify trough.

R&D-S&M-MAINTENANCE-VS-GROWTH (GEICO precedent):
  By analogy to Buffett 2002 GEICO marketing split [TX 28569]:
  *"I used the GEICO example... it might be $50 million to maintain... and how much we are spending,
  beyond that maintenance cost, to build the business for the future."*
  For SaaS where R&D and S&M dwarf PP&E capex, judgment-based split of those line items.
  Document explicitly: "S&M maintenance ≈ $X; growth portion = $Y treated as reinvestment, not deducted."
```

Maintenance-capex is the highest-confabulation-risk number in the entire valuation. Both CC and Codex independently derive it; reconciliation surfaces divergences > 20% relative or > 5% intrinsic-effect.

---

## Equity vs EV — the comparison rule

**This is a categorical methodology choice. Get it wrong and the entire DCF is meaningless.**

```
If your cash-flow definition starts from NET INCOME (Buffett owner earnings):
  → cash flow is LEVERED (computed AFTER interest expense)
  → DCF NPV is an EQUITY VALUE
  → Compare DCF NPV to MARKET CAP (= shares × price)
  → DO NOT subtract debt or add cash; that's already implicit in the equity-level rate

If your cash-flow definition starts from NOPAT (unlevered free cash flow):
  → cash flow is UNLEVERED (before interest expense)
  → DCF NPV is an ENTERPRISE VALUE
  → Compare DCF NPV to EV (= market cap + debt − cash)
  → Equity value = EV − net debt

Peer EV/EBITDA, EV/EBIT, EV/Revenue → separate sanity-check section, never a tier input.
```

This skill defaults to **equity-level (NI-derived owner earnings → market cap comparison)** because it's the literal Buffett 1986 formula. EV-based DCF is the McKinsey/Damodaran convention; valid but moves further from the framework being implemented.

---

## FCF definition labeling rule (mandatory file-level invariant)

Any file under `{BASE}/raw/*.md` or `{BASE}/steps/*.md` that uses the string "FCF" or "free cash flow" MUST label which definition on first use. Three accepted labels:

- `OE_Buffett_1986` — the canonical formula above
- `FCF_10K_convention` — OCF − PP&E capex (management's typical reporting)
- `FCF_proxy_convention` — OCF − PP&E capex − capitalized internal-use software

Downstream files inherit the labeled definition. **Step 3.5 propagation gate enforces** — every unlabeled "FCF" occurrence is a propagation issue and must be corrected before Phase 4 proceeds.

Default for the skill's valuation work: `OE_Buffett_1986`. If using a shortcut (e.g., reporting management's `FCF_10K_convention` for context), bridge to `OE_Buffett_1986` explicitly before any DCF input.

---

## External-FCF ingestion bridge rule (mandatory)

Sell-side reports routinely report "FCF" as `OCF − PP&E capex` with SBC added back (treating SBC as non-cash) and capitalized software omitted. The skill must NEVER consume this number as owner-earnings-equivalent.

When ingesting any externally-labeled "FCF" (analyst report, company IR, peer-multiples comparison), the canonical file MUST show the conversion bridge:

```
External "FCF" (as labeled by source)                              $X
+ capitalized internal-use software (if not already deducted)      −$Y
− SBC at cash-cost layer (Buffett 2015 rule)                       −$Z
± other reconciliation items                                       ±$W
= Owner earnings (Buffett 1986 OE_Buffett_1986)                    $(X − Y − Z ± W)
```

Without the bridge, downstream agents cannot tell whether the number is comparable to the owner-earnings base used in the DCF.

---

## Worked example (CRWD FY26, illustrative — calibration only, not load-bearing)

| Line | Value |
|---|---:|
| GAAP Net Income | $(162.5)M |
| + D&A | +$250M |
| − Maintenance capex (≈ D&A run-rate, asset-light default) | −$250M |
| + Net working-capital float (deferred revenue growth net of AR growth) | +$400M |
| **= Owner earnings (Buffett 1986)** | **≈ $237M** |
| Per share at current 254M diluted shares | ≈ $0.93/share |

For reference, the prior CRWD reconciliation used $1.25B as base — that was OCF-derived with SBC implicitly added back, which is the framing Buffett 2015 explicitly rejects. The new framework produces owner earnings ~5× smaller, materially changing intrinsic value. **This is the expected magnitude of correction for SBC-heavy SaaS.**

Stage 9 prose section for CRWD MUST address WC-float sustainability — at $400M, it exceeds the 50%-of-OE dominance threshold.

---

## Sources

- 1986 Berkshire annual letter, Scott Fetzer purchase-accounting appendix [LT 10467–10560] (verbatim definition above)
- 1989 letter [LT 14725]: EBITDA hostility
- 1996 meeting [TX 12069–12143]: compulsory reinvestment Q&A — operational rule on (c)
- 2002 meeting [TX 28569]: GEICO marketing maintenance-vs-growth split
- 2014 letter [LT 33819]: amortization split (~80% non-real, ~20% real)
- 2015 letter [LT 35528]: SBC is real compensation — the "most egregious example" of the management/Wall-Street charade
- 2018 letter [LT 37834]: BNSF depreciation understates economic cost
- Research (a) `Feedbak/(a) BuffettMunger valuation methodology.md`, sections 1 and 2
- Research (c) `Feedbak/(c) DCF methodology for compounders.md`, section 5 (SBC + share count handling) — note: research (c) endorses the dilution-modeling approach; this file requires consistency with the conditional-on-starting-point table above to avoid double-counting.
