# Moat durability tiers — empirical anchors for Stage-1 length and certainty premium

This file maps the Phase 4 moat-durability finding to operational valuation parameters. The empirical anchors come from the 28-case research-(b) reference set — both moats that lasted 30+ years and moats that collapsed despite looking durable.

## The empirical durability table

From research (b), Section "Q1: Are certain moat types empirically more durable?"

| Tier | Type | Median observed durability | Example cases |
|------|------|---------------------------|---------------|
| Most durable | Regulatory + statutory embedding | 50+ years and counting | Moody's |
| Very durable | Two-sided network with mutual switching costs | 50+ years | Visa, Mastercard, MS Office |
| Very durable | Brand + habit in stable consumption category, with distribution lock | 50+ years | Coke, See's, Hermès, Diageo, McDonald's, Disney parks |
| Moderately durable | Counter-positioning with structural cost asymmetry | 30+ years and ongoing | Costco |
| Moderately durable | Process Power in deep-tech with high capital + tacit-knowledge barriers | 30+ years (state-actor risk) | ASML, TSMC |
| Vulnerable | Pure scale economies in contestable channel | 20–40 years variable | Walmart (stable), Sears (decayed), newspapers (decayed) |
| Most vulnerable | Brand + scale in fast-moving technology | 10–20 years before disruption | Kodak, Nokia, Intel, Britannica |

## Joint test for Stage-1 length: durability AND runway

A long Stage-1 forecast requires BOTH high durability AND high reinvestment runway. A mature staple (Coca-Cola today) has 50+ year moat durability but limited reinvestment runway → Stage-1 should be 10y, not 15y. A regulatory moat with growing TAM (Moody's expanding into ESG / private credit) has both → 15y is defensible.

```
Stage-1 length decision rule:
  durability HIGH + runway HIGH:        12–15 years
    (Moody's-style with TAM growth, Visa with payment digitization,
     Microsoft with cloud + AI, Hermès with global luxury demand)
  durability HIGH + runway MODERATE:    10 years
    (Coca-Cola, See's, McDonald's mature franchises)
  durability MODERATE:                   7 years
    (Costco, ASML — process-power with state-actor risk)
  durability VULNERABLE:                 5–7 years
    (Walmart, McDonald's franchise saturation)
  durability MOST VULNERABLE:            5 years
    (tech-scale moats: Kodak/Nokia/Intel categories)
  unforecastable:                        no DCF — exit Phase 5
```

The judgment call: how to assess "reinvestment runway." Anchor to:
- Phase 4 (moat durability) findings on disruption vectors and confidence at 3y/10y
- Industry agent (step4) findings on TAM and growth drivers
- Capital allocation findings (step8) on whether management is reinvesting at high incremental returns

## The most reliable warning signals (research b, Q2)

These determine whether to DOWNGRADE confidence even when the static moat type is high-durability:

1. **Declining incremental ROIC even with stable reported ROIC** — strongest single signal. Visible in Intel (10nm delays absorbed margin while reported numbers held), GE Capital (commercial-paper roll-over risk hidden in profits), Sears (real-estate monetization sustained reported earnings while operating economics hollowed out).

2. **Customer concentration shifts / share loss in the most price-sensitive segment first** — strong signal. Nokia (low-end Asian competition first, then iPhone at top), Kodak (consumer film volumes before professional), Bed Bath & Beyond (price-sensitive customers to Amazon first).

3. **Capex underinvestment relative to a credible new threat** — strong signal in clear cases. Sears vs. Target/Walmart 2008–14, Blockbuster vs. Netflix infrastructure.

4. **Buffett's "cockroach" rule** — multiple bad-news items in close sequence. Tesco's accounting issues followed market-share losses followed by margin contraction inside 18 months. Sears 2007–2010.

If 2+ of these signals are present, downgrade Stage-1 length by one tier even if the static moat type is high-durability.

## Industry growth interaction (research b, Q3)

**Moats decay faster in declining industries even without direct technological substitution.** Newspapers, Yellow Pages, traditional broadcast TV. The mechanism: declining industries cannot fund the R&D, capex, and management-talent renewal needed to maintain a moat; they cycle through restructuring instead.

If Phase 4 places the company in a structurally declining industry, force terminal growth toward 0% or negative — do not default to 3%.

## Calibration limit (research b, Q5)

**Of 11 collapse cases in research (b), only ~5–6 were callable 5 years out, and 9–10 were callable 3 years out from public information.** This sets the upper bound on Stage-1 confidence. Anyone projecting moat durability with confidence beyond 5 years is extrapolating beyond what historical analysis supports for collapse-prediction.

## Sources

- Research (b): 28-case curated moat reference set (full)
- Hamilton Helmer, *7 Powers* (taxonomy)
- Bruce Greenwald, *Competition Demystified* (local scale + customer captivity framing)
- Anita McGahan and Michael Porter, "Persistence of Shocks to Profitability" (1999)
- Pat Dorsey / Morningstar moat methodology
