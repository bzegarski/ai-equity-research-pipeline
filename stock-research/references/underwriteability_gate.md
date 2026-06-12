# Underwriteability gate — Stage 0 of every valuation

Before any DCF runs, classify the business. This is the load-bearing addition to the valuation framework — without it, the skill produces precise-looking DCFs for businesses that should never have been DCF'd.

The gate is grounded in Buffett's go/no-go framing across multiple meetings, most explicitly:

Buffett 1998 [TX 19927]:
> *"We look at riskiness, essentially, as being sort of a go/no-go valve in terms of looking at the future businesses. In other words, if we think we simply don't know what's going to happen in the future, that doesn't mean it's necessarily risky, it just means we don't know. It means it's risky for us. It might not be risky for someone else who understands the business. In that case, we just give up. We don't try to predict those things."*

Buffett 2008 [TX 53672]:
> *"if a business gets to the point where we think the industry in which it operates, the competitive position or anything is so chancy that we can't really come up with a figure, we don't really try to compensate for that sort of thing by having some extra large margin of safety. We really want to try to go on to something that we understand better."*

Buffett 1996 [TX 8987]:
> *"I don't think you can stick something — numbers on a highly speculative business, where the whole industry's going to change in five years, and have it mean anything when you get through."*

---

## The three classifications

**UNDERWRITABLE** — cash-flow trajectory predictable for 10+ years with current evidence. Owner-earnings DCF defensible. Proceed to Stage 1.

**PARTIAL** — moderate certainty; material uncertainties present but not disqualifying. Examples: disruption vectors at 15–30% probability per Phase 4/6; secular shift in progress but not yet decisive; high-quality current execution against an attacker. Run the DCF but require larger MoS at the end; flag confidence as Low. Proceed to Stage 1 with caveats.

**TOO HARD** — cash flows not defensibly forecastable. Examples: early-stage biotech with no approved product; commodity producer at unknowable forward prices; business whose entire industry will change in 5 years; bank/insurer/REIT (use methodology-specific frameworks, not owner-earnings DCF).

For TOO HARD: **no DCF, no BUY/WATCHLIST/PASS verdict from valuation.** Per Buffett's framing, do not fudge inputs to compensate. Walk away from the valuation question.

**Allowed exception for TOO HARD output:** the valuation file MAY publish a reverse-DCF read of market expectations, clearly labeled non-decision. Reverse DCF is reading the market, not underwriting forward — it's appropriate even when forward valuation isn't. Format:

> *"At current price, the market implies X% growth for N years. For context, the industry blend is Y%, trailing 5y actuals were Z%, and no Fortune 500 has sustained > 15% over 50 years. This is informational only; no BUY/PASS verdict is offered because the business does not clear the certainty filter."*

---

## Inputs to the classification

Five inputs, weighed together by the agent. No mechanical formula — Buffett 1986 [LT 10483] *"vaguely right rather than precisely wrong"* applies.

### Input 1 — Phase 4 (moat durability) 10-year confidence tier

The Phase 4 output (`step6_moat_durability.md`) classifies 10-year moat confidence as HIGH / MODERATE / LOW / VULNERABLE per the research-b durability table.

Mapping (default; override allowed with explicit reasoning):
- HIGH (regulatory, brand-habit, two-sided network) → tilts UNDERWRITABLE
- MODERATE (counter-positioning, scale in stable channel) → tilts UNDERWRITABLE or PARTIAL
- LOW (tech-scale, brand+scale in fast-moving) → tilts PARTIAL
- **VULNERABLE → CANNOT be UNDERWRITABLE.** Structural rule: a vulnerable moat means cash flows are NOT defensibly forecastable for 10+ years. Must be PARTIAL or TOO HARD. See `decision_logic.md` MoS matrix.

### Input 2 — Pre-valuation disruption-vector evidence

Aggregate disruption-vector evidence from the files available BEFORE Phase 5A (Phase 6 has not run yet at the point Stage 0 fires — `step10_counter_attack.md` does not exist):

- `step6_moat_durability.md` (Phase 4 disruption-vector inventory with named historical analogs and probabilities — **this is the load-bearing source**)
- `step4_industry.md` (industry shifts, regulatory threats, secular trends)
- `step5_moat_current.md` (current moat strength vs identified threats)
- `step7_accounting.md` (Buffett accounting framework — Tier-I earnings-overstatement quantification + Tier-II red flags + Tier-III culture/governance evidence; cascade-relevant signal is the opt-out flag, not the verdict tier)
- `step8_management.md` (management quality, alignment, capital allocation)
- `raw/customer_perspective.md` if present (Agent F output: customer-ranking evidence, substitution signals)
- `raw/competitors.md` (competitive positioning, peer dynamics)

Count vectors with ≥15% 10-year probability per the Phase 4 framework:

- 0–1 vectors → tilts UNDERWRITABLE
- 2–3 vectors → tilts PARTIAL
- 4+ vectors → tilts PARTIAL or TOO HARD (especially if vectors are mutually-reinforcing or address different attack surfaces)

**Note:** Phase 6 counter-attack (`step10_counter_attack.md`) may LATER challenge or revise the Stage-0 verdict, but it is NOT a Stage-0 input — Phase 6 runs after Phase 5C. The Phase 4 moat-durability inventory is the primary disruption-vector source for Stage 0.

### Input 3 — Industry change rate

Buffett 1996 [TX 8987]: industries that will "change in five years" cannot be valued by 10-year DCF. Markers:
- Pace of technological substitution
- Regulatory regime stability
- Consumer-behavior persistence

Examples by industry archetype:
- Consumer staples (Coke, See's, Hershey) → low change rate → UNDERWRITABLE if other inputs allow
- Cybersecurity / SaaS → moderate-to-high change rate → typically PARTIAL even with strong current quality
- Early-stage biotech / quantum / autonomous vehicles → high change rate → TOO HARD

### Input 4 — Unit-volume + pricing-power predictability

The two most-Buffett-faithful tests of forecastability:

- Can you defensibly forecast unit volume 10 years out? (Per 1986 [LT 10472]: maintenance capex is what's required to sustain *unit volume*.)
- Does the business have observable pricing power (per Buffett's See's framework — can raise prices without losing material volume)?

If neither answer is "yes with evidence," PARTIAL at best.

### Input 5 — Competitive position trajectory

Is the moat currently widening, holding, or narrowing? Use Phase 4 evidence:
- Widening → UNDERWRITABLE-leaning
- Holding → UNDERWRITABLE or PARTIAL
- Narrowing → PARTIAL, possibly TOO HARD if narrowing rate is material

---

### Accounting opt-out flag cascade (BINDING UNLESS EXPLICITLY ESCALATED)

The accounting agent emits two orthogonal fields. The Stage-0 cascade reads ONLY the **opt-out flag**, not the verdict tier (the verdict feeds other consumers — management agent, final memo, Phase 5C reconciliation).

The opt-out flag is **binding unless explicitly escalated** — the cascade is the default. The valuation agent may deviate from the default ONLY with explicit written escalation to Phase 5C reconciliation (where the disagreement is logged and resolved with the user as message bus per the dual-model protocol in `CLAUDE.md`). Silent override is forbidden; explicit override is allowed when source-backed.

Accounting is NOT the sole Stage-0 authority — accounting drives the default cascade; valuation may overrule with documented reason at Phase 5C.

```
Opt-out flag = RECOMMEND TOO HARD    → Stage 0 forced to TOO HARD.
                                       Rationale: Buffett 2008 [TX 53670] —
                                       wider MoS does not rescue
                                       unanalyzability.

Opt-out flag = RECOMMEND PARTIAL     → UNDERWRITABLE → PARTIAL.
                                       PARTIAL stays PARTIAL.

Opt-out flag = WATCH                 → No automatic downgrade. Caveats
                                       surfaced in Stage-0 confidence prose.

Opt-out flag = NONE                  → No accounting-driven Stage-0 effect.
```

---

## Operational mapping (not a hard rule — judgment final)

| Pattern | Classification |
|---|---|
| HIGH moat + 0–1 disruption vectors + low industry change + clear unit-volume runway + pricing power | UNDERWRITABLE |
| HIGH moat + 2 vectors + moderate change + unit volume forecastable | UNDERWRITABLE (lower confidence) |
| MODERATE moat + 2–3 vectors + moderate change | UNDERWRITABLE or PARTIAL — judgment call |
| LOW moat + 3+ vectors + moderate-to-high change | PARTIAL |
| VULNERABLE moat (any other inputs) | PARTIAL minimum; TOO HARD if vectors are decisive |
| Industry will change in 5 years (per Buffett 1996) | TOO HARD |
| Pre-revenue / no current owner earnings | TOO HARD (use optionality framework, not owner-earnings DCF) |
| Bank / insurer / REIT | TOO HARD for the standard owner-earnings DCF; use methodology-specific framework |

---

## Output to the valuation file

Every valuation file starts with the Stage 0 verdict and the evidence. Format:

```
=== UNDERWRITEABILITY GATE ===

Verdict: UNDERWRITABLE | PARTIAL | TOO HARD

Evidence:
- Phase 4 moat tier (10y): [HIGH | MODERATE | LOW | VULNERABLE] — [one-sentence reason from step6]
- Pre-valuation disruption-vector count (≥15% 10y probability per Phase 4 inventory in step6_moat_durability.md): N — [list]
- Industry change rate: [Low | Moderate | High] — [one-sentence justification]
- Unit-volume predictability: [Strong | Moderate | Weak] — [evidence]
- Pricing-power evidence: [Strong | Moderate | Weak | Absent] — [evidence]
- Competitive position trajectory: [Widening | Holding | Narrowing] — [evidence]

Classification reasoning (2-3 sentences): [why this verdict given the inputs]

Implication for Stage 4 MoS: [reference the row/cell of the matrix per decision_logic.md]
```

If verdict is TOO HARD, the file may include a reverse-DCF section per the allowed exception above, then STOP. Do not run Stages 1–8.

---

## Why this gate matters

Without Stage 0, the skill mechanically produces DCFs for any business with positive owner earnings. Many of those DCFs will be plausible-looking and decision-shaped. They will also be wrong, because the cash flows on which they rest are not defensibly forecastable.

Buffett's framework explicitly rejects this. He walks away from businesses he doesn't understand, even when the price looks cheap. The skill's prior architecture (CAPM-based with risk-adjusted rate) tried to compensate for low certainty by raising the rate. Per Buffett 1997 [TX 8990]:

> *"If you say I'm going to stick an extra 6 percent in on the interest rate to allow for the fact [that the business is risky] — I tend to think that's kind of nonsense. I mean, it may look mathematical. But it's mathematical gibberish in my view."*

Stage 0 is the architectural alternative: instead of fattening the rate to handle uncertainty, refuse to value uncertain businesses at all. Don't produce a precise-looking answer where no defensible answer exists.

---

## Regression test (run on these reference tickers)

Verification that the gate is calibrated correctly:

| Ticker | Expected verdict | Reasoning |
|---|---|---|
| AAPL | UNDERWRITABLE | HIGH moat (consumer ecosystem); 1–2 disruption vectors at low-moderate probability; moderate industry change rate; strong unit volume + pricing-power evidence; widening moat (services growth) |
| CRWD | PARTIAL | LOW-MODERATE moat at 10y per step6; 4 disruption vectors at 15–30% probability; high industry change rate; strong current quality but uncertain 10y trajectory |
| Early-stage biotech (no approved drug) | TOO HARD | No current owner earnings; cash flows not defensibly forecastable; binary regulatory outcomes |
| Moody's | UNDERWRITABLE | HIGH moat (regulatory NRSRO designation); 0–1 vectors at low probability; low industry change rate; strong pricing power; holding-to-widening moat |
| Hershey | UNDERWRITABLE | HIGH moat (brand-habit); 1–2 vectors at low probability; low industry change rate; demonstrable pricing power; holding moat |
| Canadian Pacific | UNDERWRITABLE (with capital-intensive overlay) | MODERATE moat (rail duopoly + irreplaceable infrastructure); 1 vector; low industry change rate; pricing power demonstrable; holding moat |

If a fresh-ticker valuation misclassifies one of these reference cases, the gate definition needs tightening before that valuation is trusted.

---

## Sources

- 1986 letter [LT 10472, 10483]: maintenance capex / "(c) must be a guess" / "vaguely right rather than precisely wrong"
- 1996 meeting [TX 8987]: industry-changes-in-five-years rejection
- 1997 meeting [TX 8984, 8990]: circle of competence; rejection of risk-rate compensation
- 1998 meeting [TX 19927, 19929]: go/no-go valve framing
- 2003 meeting [TX 24026]: Treasury rate is yardstick, but uncertainty filter is binary
- 2008 meeting [TX 53672]: walk away, don't compensate with bigger MoS
- Research (a) `Feedbak/(a) BuffettMunger valuation methodology.md`: synthesis of go/no-go practice
- Research (b) `Feedbak/(b) Curated moat reference set.md`: durability tier evidence base
