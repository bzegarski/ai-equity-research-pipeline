# Accounting principles — Buffett/Munger framework

This file is the load-bearing methodology for the accounting agent's diagnostic sweep. CC's `agents/accounting.md` and Codex's `agents/accounting_codex.md` both read this file. Codex's `agents/valuation_codex.md` also reads it as part of its agent-level preflight (loud-fail if missing).

Sister files (do NOT duplicate; cross-reference):
- `references/owner_earnings.md` — canonical mechanics for SBC handling, maintenance capex, non-real amortization, working-capital float. The accounting agent produces the **pre-valuation economic earnings bridge**; the valuation agent then applies `owner_earnings.md`'s maintenance-capex and working-capital rules to convert that bridge output → final owner earnings.
- `references/underwriteability_gate.md` — Stage-0 cascade that reads the accounting agent's opt-out flag (binding unless explicitly escalated).

Citation form: `[LT n]` = line in `Feedbak/Berkshire-Hathaway-Letters-to-Shareholders_to2024.md`; `[TX n]` = line in `Feedbak/Berkshire Meeting Transcripts - 1994 - 2022 (1).md`.

---

## Organizing frame — Buffett's three questions (1988 letter)

The accounting agent's output is anchored on Buffett's own framing of what financial statements are FOR. From the 1988 Berkshire shareholder letter [LT 12184–12195]:

> *"When financial statements are prepared by other parties to assist managers and owners, the data should help answer three primary questions about a business: (1) Approximately how much is the company worth? (2) What is the likelihood that it can meet its future obligations? (3) How good a job are its managers doing, given the hand they have been dealt?"*

The diagnostic toolkit below (26 principles in 5 tiers) is a means to answer these three questions for the specific company under review. Most principles do not fire for most companies — the agent reports fires, not silent non-fires.

---

## Foundation tier (3 principles — meta-frame)

### F1 — Economic earnings over reported earnings

GAAP is the starting point, not the conclusion. Every accounting agent output must explicitly state whether GAAP earnings **overstate**, **understate**, or **roughly represent** owner economics.

Primary sources:
- 1977 [LT 21–44]: foundational framing — return on equity capital is "a more appropriate measure of managerial economic performance" than EPS gains, because EPS rises mechanically with reinvested earnings even when the underlying return is mediocre. Earliest accounting principle in the corpus.
- 1979 [LT 925–946]: EPS-as-stopped-clock framing made explicit. Buffett 1979 [LT 939]: *"even a 'stopped clock' can look like a growth stock if the dividend payout ratio is low."* And [LT 941–946]: *"The primary test of managerial economic performance is the achievement of a high earnings rate on equity capital employed (without undue leverage, accounting gimmickry, etc.) and not the achievement of consistent gains in earnings per share."* The agent must distinguish genuine compounding from mechanical EPS effects.
- 1986 [LT 10485]: *"we consider the owner earnings figure, not the GAAP figure, to be the relevant item for valuation purposes."*
- 1986 [LT 10556–10561]: *"the accountants' job is to record, not to evaluate. The evaluation job falls to investors and managers… accounting is but an aid to business thinking, never a substitute for it."*
- 1988 [LT 12184–12195]: the three-questions framing (above).

Operational rule: every agent output's Q1 paragraph (under the three-questions output frame) must give a verdict — overstates / understates / roughly represents — and cite the line items driving the verdict.

### F2 — Buffett's three questions as output frame

The agent's output structure follows the three questions verbatim. This is enforced by the OUTPUT FORMAT block in `agents/accounting.md`. Q1 → valuation-relevant assessment. Q2 → solvency / obligation-meeting capacity. Q3 → management's stewardship of the financials (capital allocation, candor, accounting choices).

[LT 12184–12195, 1988].

### F3 — Two-plus-two degrees-of-freedom diagnostic

Buffett 1988 [LT 12202–12232], the "cooperative accountant" passage:

> *"'How much,' says the client, 'is two plus two?' Replies the cooperative accountant, 'What number did you have in mind?'"*

Enumerate every estimate management chose. For each, label conservative (C) / neutral (N) / aggressive (A) and quantify the earnings impact. Mandatory inputs to enumerate (when present in the 10-K / 10-Q / footnotes):
- Pension expected return assumption (vs long-Treasury yield)
- Deferred-tax valuation allowance changes
- Insurance loss reserves / bank loan-loss provisions / warranty reserves
- Environmental + litigation reserves
- Impairment thresholds + timing
- Useful-life assumptions (PP&E, intangibles)
- Capitalization vs. expensing policies (software development, R&D adjacent)
- Revenue-recognition timing within ASC 606 (variable consideration, performance-obligation splits)
- Inventory valuation method changes (FIFO/LIFO/average)

Operational rule: F3 output is a table — `| Estimate | Chosen value | C/N/A | Earnings impact | Footnote |` — with at least 3 rows per company.

---

## Tier I — Mechanical bridge adjustments (8 principles; produce $-lines)

These principles produce explicit $-lines in the GAAP NI → pre-valuation economic earnings bridge. The bridge is the load-bearing handoff from accounting to valuation.

### M1 — Pre-valuation economic earnings bridge (accounting produces; valuation owns final)

The accounting agent produces a **GAAP NI → pre-valuation economic earnings bridge** as a mandatory line-by-line table with adjustment flags. This bridge removes the obviously-wrong stuff (non-real PPA amortization, post-2018 MTM, recurring "non-recurring" charges, pension assumption gaps, SBC handling per starting point). The bridge does NOT include maintenance capex or working-capital judgment — those belong to the valuation agent per `owner_earnings.md`.

**Ownership boundary:**
- Accounting OWNS: the pre-valuation bridge, accounting-quality verdict, opt-out flag, evidence for G3 (routes to management).
- Valuation OWNS: the final owner-earnings number (consumes bridge OR documents explicit disagreement); silent re-derivation forbidden.
- Management OWNS: the candor verdict (reads Tier-III evidence; issues judgment).

Cross-references: `references/owner_earnings.md` (canonical mechanics). Do NOT duplicate. Cite specific sections.

Primary sources: 1986 [LT 10467–10557] Scott Fetzer appendix; 1996 [TX 8956].

### M2 — SBC is real compensation (conditional-on-starting-point rule)

Per Munger 2004 [TX 35653] no-double-count discipline. Handling depends on starting point:

- **Starting from GAAP NI:** SBC is already expensed. Do NOT add back. Use current diluted shares as denominator. Do NOT also model future dilution as the primary denominator (that would triple-count SBC: once via NI reduction, once via re-deduction, once via projected dilution).
- **Starting from OCF / adjusted FCF / non-GAAP:** SBC was added back as "non-cash." Re-deduct it as cash compensation.
- Either way: never both (double-count), never neither (free pass).

The 1999 warrant-valuation method [TX 21472] is the practical alternative for cross-check: take 5y total SBC ÷ 5 (annualized) and ask "what would the company have received in cash for those options if sold to the public as warrants?" — that's the market-value floor on SBC's real cost.

Mandatory reporting:
- SBC as % of revenue (5y average)
- SBC as % of |GAAP NI| (5y average)
- 5y dilution rate net of buybacks (FDS growth rate)
- Flag if 5y FDS growth > 3%/yr after buyback offset

Primary sources: 1985 [LT 8085]; 1992 [LT 18208]; 2015 [LT 35528] ("SBC is the most egregious example"); 2016 [LT 36612]; 1997 [TX 13386]; 1998 [TX 17321]; 1999 [TX 21472]; 2004 [TX 35653 Munger double-count rebuttal].

### M3 — EBITDA banned (graduated rule with explicit lead-KPI test)

EBITDA appearing somewhere in financial materials ≠ flag. EBITDA as **lead KPI** = flag.

**Lead-KPI operational test.** The flag fires if EBITDA appears in ANY of:
- (a) Investor-deck headline-KPI page
- (b) MD&A management-commentary opening paragraph
- (c) Compensation-plan performance metrics in the DEF 14A proxy

Mere mention elsewhere in financial materials does NOT trigger.

For coverage ratios, use **pre-tax EBIT/interest**, never EBITDA/interest [LT 31769].

Buffett 2002 [TX 34074] base-rate framing: presence of EBITDA-as-lead-metric correlates with elevated fraud rate. The flag is empirical, not normative.

Primary sources: 1986 [LT 10513] (cash-flow without (c) is absurd); 1989 [LT 14725] ("abomination"); 2008 [LT 31769] (coverage ratio rule); 2013 [LT 33826] ("polygraph test"); 2014 [LT 35540] ("nose lengthen"); 2015 [LT 35536] (BNSF depreciation gap); 2018 [LT 37817] ("adjusted EBITDA"); 2024 [LT 41099] ("banned measurement"); 1998 [TX 18522] ("utter nonsense"); 2002 [TX 34073, 34074] (fraud base rate); 2003 [TX 40210, 40227 Munger "bullshit earnings"]; 2012 [TX 74445]; 2017 [TX 97507] ("reverse float").

### M4 — Maintenance capex by business class (policy defaults; agent flags, valuation finalizes)

The accounting agent identifies the business class and the gap (if any) between GAAP D&A and required maintenance capex. The valuation agent applies the final maintenance-capex subtraction per `owner_earnings.md`. Accounting does NOT subtract maintenance capex in the bridge — that subtraction belongs in valuation.

Business-class flags:
- **Asset-light** (consumer staples, software-only, services): maintenance capex ≈ D&A. No M4 flag.
- **Capital-intensive** (rail, utility, pipeline, telecom, oil & gas): maintenance capex typically exceeds D&A by 30–80%. M4 fires with [HUMAN-VERIFY] flag. The 60–80% range is **skill policy** derived from Buffett's BNSF anchor [TX 92685], NOT a literal Buffett formula.
- **Acquisition-heavy**: separate amortization handling per M5 below.
- **SBC-heavy** (modern SaaS): require an SBC sensitivity row (already covered by M2; M4 flag if PP&E/revenue ratio justifies separate analysis).

Operational reporting:
- Business class identification with 1-sentence justification
- 5y D&A vs 5y total capex
- Management's stated maintenance-vs-growth capex split (from 10-K) if disclosed
- Flag for valuation: "M4 applies — maintenance capex > D&A by X-Y% based on business class; valuation must apply subtraction"

Primary sources: 1986 [LT 10472, 10506] (maintenance capex concept); 2015 [LT 35536] (BNSF: "the depreciation charge we record in our railroad business falls far short of the capital outlays needed to merely keep the railroad running properly"); 2016 [LT 36578] ("GAAP-prescribed depreciation charges… in certain cases materially understate true economic costs"); 2018 [LT 37834] ("Berkshire's $8.4 billion depreciation charge understates our true economic cost"); 2002 [TX 28543] (GEICO marketing maintenance-vs-growth split — extends concept beyond capex to S&M/R&D when separable); 2016 [TX 92685] (BNSF "true maintenance capex… is higher than 60 percent of [total capex]" — the policy-anchor for 60–80% range).

### M5 — Amortization category-specific split (~80/20 policy default)

Real (software, depleting IP) vs. non-real (PPA goodwill, customer relationships, trade names). Bridge $-line: add back non-real amortization (it is not an economic cost).

**The ~20% real / ~80% non-real ratio is skill policy** from Buffett 2014 [LT 33819] empirical statement at Berkshire ("We would call about 20% of these 'real,' the rest not"), NOT a universal formula. Verify per-company against the intangibles roll-forward in the 10-K footnotes.

Specific cases:
- **Bank core-deposit-intangible amortization:** fictional when deposits are growing. Wells Fargo 2009 [LT 31841; TX 62803]: *"In no sense, except GAAP accounting, is this whopping charge an expense."* — add back entirely if deposits are growing.
- **Software amortization:** keep as real if economic life is genuinely declining.
- **Customer relationships / trade names / brand intangibles from PPA:** typically non-real if business is sustaining or growing.

Operational reporting: itemize intangibles roll-forward; classify each line; sum non-real → add-back $-line in bridge.

Primary sources: 1983 [LT 5775–5786] (foundational appendix); 2014 [LT 33819] (20/80 split); 2018 [LT 37831] (Berkshire's $1.4B add-back); 2012 [LT 31830] (software amort is real; customer relationships are not); 1983 [LT 5660] (economic goodwill increases); 2009 [TX 62803] (Wells Fargo core-deposit amortization fictional); 2011 [TX 71298] (two-step framework: economics on tangible; management on returns including goodwill).

### M6 — Pension/OPEB normalization

Mandatory output line, every company with material pension/OPEB plans:

```
Disclosed pension return assumption: X%
Long-Treasury yield:                 Y%
Gap:                                 Z pp
Plan assets:                         $N
Implied earnings overstatement:      $M (Gap × Plan assets)
```

**The 2-pp gap threshold for flagging is skill policy.** Buffett's anchor is qualitative — 2007 [LT 27354] S&P 363 firms used 8% average return assumption while long Treasury < 5% (a ~3pp gap that he calls out as a systematic earnings overstatement). The skill flags when Gap > 2pp; the 2-pp policy default is conservative relative to Buffett's specific example.

Adjust net debt for unfunded OPEB obligations (separate from the income-statement adjustment).

Discount-rate assumption on liabilities: also flag if materially out of line with current corporate-bond curves (a low discount rate inflates current pension expense; a high one understates the liability).

Primary sources: 2001 [TX 30050, 30095] (assumption-vs-current-environment); 2001 [TX 30104 Munger earthquake-fault analogy] ("would be like living right on an earthquake fault that was building up stress every year and projecting that the longer it's been without an earthquake the less likely an earthquake is to occur"); 2003 [TX 40239 Munger "lollapalooza"]; 2003 [TX 40242 Buffett: "companies are recording pension income in the hundreds of millions, while at the same time being underfunded in their pension plan in the many billions"]; 2006 [LT 26376]; 2007 [LT 27353–27410].

### M7 — Recurring "non-recurring" charges

Count years in the trailing 10y with material restructuring / integration / "one-time" / impairment / "special" charges. Two thresholds, EITHER fires (Buffett 1992 + 2016 framing):

- **≥ 3 of 10y AND charges are similar-in-nature** (serial restructurings, repeated integration costs, recurring impairments in the same segment). Genuinely-distinct one-time events spaced across a decade do NOT count toward the count threshold.
- OR **cumulative > 20% of cumulative NI** (no similar-in-nature qualifier — magnitude alone fires).

If either fires, treat the run-rate as a recurring operating cost in the bridge $-line. Flag any "adjusted earnings" reconciliation that excludes them.

Munger 1999 [TX 22180] big-bath warning:

> *"it's the big bath accounting, and the subsequent release back into earnings of taking an overly large bath, that create a lot of the abuse."*

Track also the release pattern: if a "big bath" charge is taken in year N and "favorable development" releases earnings in years N+1, N+2, that's the abusive pattern.

Primary sources: 1988 [LT 12202] ("white-lie smoothing"); 1992 [LT 17466] ("toad" passage on restructuring charges); 1999 [TX 21461] ("never had a charge like that"); 1999 [TX 22180 Munger big-bath]; 2004 [TX 41568] ("lumpy or peculiar"); 2016 [LT 36589–36597] ("Two of [analysts'] favorites are the omission of 'restructuring costs'…"); 2016 [LT 36594] (bad behavior contagious); 2016 [LT 36122] (Berkshire never has "restructuring charges").

### M8 — MTM / realized-gains separation (post-2018 ASU 2016-01)

If marketable securities > 20% of total assets, report **operating earnings ex-MTM** as the canonical bridge line; route THAT to valuation, not GAAP bottom-line NI.

Buffett 2017 [LT 37164]: *"For analytical purposes, Berkshire's 'bottom-line' will be useless."*

Buffett 2018 [LT 37766]: *"our huge equity portfolio… will often experience one-day price fluctuations of $2 billion or more, all of which the new rule says must be dropped immediately to our bottom line… Our advice? Focus on operating earnings, paying little attention to gains or losses of any variety."*

Buffett 2019 [LT 38185]: *"Berkshire's 2018 and 2019 years glaringly illustrate the argument we have with the new rule. In 2018… we reported GAAP earnings of only $4 billion. In 2019… GAAP earnings to the $81.4 billion… Those market gyrations led to a crazy 1,900% increase in GAAP earnings!"*

Operational rule: for equity-heavy holdcos (insurers, BRK-style conglomerates, some banks), the bridge's primary line is operating earnings ex-MTM. GAAP bottom-line still reported alongside, but explicitly excluded from valuation inputs.

Primary sources: 1978 [LT 478]; 2017 [LT 37164, TX 95846]; 2017 [TX 95867 Munger: "You can blame the audit profession for that one. That was really stupid."]; 2018 [LT 37766]; 2019 [LT 38185]; 2017–2019 [TX 99004, 102266].

---

## Tier II — Qualitative red flags (10 principles; judgment-based)

These principles report under `=== PRINCIPLES THAT FIRED ===`, NOT in the bridge. Each fire requires one-sentence evidence with citation.

### D1 — Goodwill three-way classification

Economic / spurious / unresolved. Large goodwill is NOT automatically a flag. Test against:
- Returns on tangible capital (net of goodwill)
- Pricing power
- Impairment history (have writedowns been timely or delayed?)
- Post-acquisition performance vs the deal model

Buffett's 1983 appendix [LT 5660–5797] is the foundational text. Key distinctions:
- **Economic goodwill:** the capitalized value of excess returns on tangible capital (See's). Tends to INCREASE over time even as accounting goodwill is amortized. Add back any amortization on this category (M5 handles it).
- **Spurious goodwill ("No-Will"):** management overpaid; the difference plugs to the goodwill account. Should impair eventually; if it does NOT, that's an audit-trail signal (D8).
- **Unresolved:** insufficient evidence; flag for investor judgment.

Buffett 1999 [TX 21781]: *"If I were setting the accounting rules, I would treat all acquisitions as purchases… I would set up the economic goodwill… I believe it should stay on the balance sheet as reflective of the money you've laid out to buy it. But I don't think it should be amortized."* (SFAS 142 implemented this in 2001.)

Primary sources: 1983 [LT 5626–5797] (full appendix); 1994 [TX 892–927]; 2014 [LT 33819]; 2018 [LT 37831]; 1999 [TX 21781].

### D2 — Synergy as accounting fiction

Buffett 1990 [LT 15416]: synergy is *"the last refuge of scoundrels defending foolish acquisitions."*

For serial acquirers, examine:
- Announced synergy targets vs realized synergies (gap is the signal)
- Whether realized synergies are even disclosed in subsequent earnings reports
- "Integration costs" that recur year over year (cross-reference M7)

Operational fires:
- Serial acquirer with no disclosed synergy realization → flag
- "Adjusted EBITDA" that excludes integration costs that have recurred 3+ years → flag (compound with M3)

Primary sources: 1990 [LT 15416]; 1997 [LT 23489–23492].

### D3 — Segmentation signal

Count distinct reportable segments vs distinct business lines described in 10-K Item 1.

Aggregation that obscures economics = transparency flag. Examples:
- A diversified conglomerate reporting only 1-2 segments when Item 1 describes 5+ distinct business types
- Segment changes (consolidation) timed to obscure a declining business inside a growing aggregate
- Segment changes that align suspiciously with management compensation triggers

Buffett 1988 [LT 12253–12277] is the foundational source on management's responsibility to provide segment-level economic clarity.

### D4 — Footnote opacity test

Per-footnote rating: **Clear / Translatable-with-effort / Opaque.** Any Opaque rating touching a material balance-sheet item is a flag.

Specifically scrutinize:
- VIEs (variable-interest entities)
- Structured-finance vehicles
- Related-party transactions
- Derivative footnotes (also D10)
- Complex tax structures
- Off-balance-sheet commitments
- Material customer-concentration that isn't quantified

Buffett 2006 [LT 25819]: *"We sometimes encounter accounting footnotes about important transactions that leave us baffled, and we go away suspicious that the reporting company wished it that way. (For example, try comprehending transactions 'described' in the old 10-Ks of Enron, even after you know how the movie ended.)"*

Operational rule: if a competent reader cannot explain the transaction in plain English from the footnote, the rating is Opaque.

### D5 — Long-tail liability / reserve estimate risk

For insurers, banks, and any firm with material long-tail reserves, examine:
- Loss-reserve roll-forward for "favorable development" vs "unfavorable development" pattern (the favorable-only pattern is the abusive one — cross-reference M7 release pattern)
- Loan-loss-provision history vs subsequent charge-offs
- Warranty reserves vs claim activity
- Environmental reserves (often understated; check 10-K Item 3 legal proceedings + Item 1A risk factors)
- Litigation reserves (often understated until just before settlement)
- Deferred-tax-asset valuation allowance changes

Buffett 1997 [LT 23215]: *"Because loss costs must be estimated, insurers have enormous latitude in figuring their underwriting results, and that makes it very difficult for investors to calculate a company's true cost of float. Estimating errors, usually innocent but sometimes not, can be huge."*

Auditor opinion is necessary but insufficient — AIG/Fannie/Freddie/MBIA all had big-name auditors before their restatements (see D8).

Primary sources: 1984 [LT 6688]; 1990 [LT 11188–11230]; 1997 [LT 23215]; 2005 [TX 47903]; 2009 [TX 62826]; 2016 [TX 92638 Munger on bank loan-loss provisions].

### D6 — Float taxonomy (broad)

Apply across all float-like liabilities, not just insurance:
- Insurance float
- Deferred revenue (SaaS, subscriptions, gift cards)
- Customer advances / prepayments
- Structurally-negative working capital (retailers with fast inventory turn)

Classify each by:
- **Cost:** negative (you get paid to hold it) / near-zero / positive (you pay for it)
- **Stickiness:** durable (renews under reasonable assumptions) / fragile (could reverse quickly)

Not all float is valuable. Bad underwriting makes insurance float expensive (combined ratio > 100). Future service obligations make deferred-revenue float costly (you owe service, not cash). Gift-card float reverses on breakage/redemption.

Buffett 1986 [LT 9642]: *"The most important thing to understand about the insurance business is the cost of funds that an insurer earns from holding on to policyholders' funds ('the float')."*

The 2007 letter [LT 26680] two-pillar framework extends to holding companies generally.

Primary sources: 1986 [LT 9642]; 2007 [LT 26680]; 1995 [TX 4673]; 1996 [TX 8750]; 1997 [TX 9936]; 1997 [LT 23116].

### D7 — Black-box "always satisfactory" tooth-fairy flag

Compute earnings volatility (coefficient of variation) of segment earnings vs underlying market or peer volatility. Suspiciously low ratio = flag.

AIGFP as canonical case. Buffett 2009 [TX 62830]: *"a black box like that can produce numbers… they don't necessarily produce cash."*

Operational fires:
- A complex/illiquid trading or derivatives segment with smoother earnings than peer segments → flag
- Segment earnings with CV < 0.5× the broader business CV when underlying market volatility is high → flag

Munger 2008 [TX 58966]: *"On Wall Street, they start believing in the tooth fairy, and if one guy is reporting a lot of money, why, everybody else is asking, 'Why aren't we betting on the tooth fairy?'"* — peer-pressure heuristic for credit-cycle peaks.

### D8 — Audit-trail deltas

The certification is not the signal; the deltas are. Big-name auditors gave clean opinions on AIG, Fannie, Freddie, MBIA before they restated (Buffett 2005 [TX 47946]).

Operational fires (any of these = flag):
- Auditor change (8-K Item 4.01)
- Non-reliance disclosure (8-K Item 4.02 — prior financials cannot be relied upon)
- Audit-committee turnover (8-K Item 5.02 — especially the chair)
- Restatements (any size)
- Material weaknesses or significant deficiencies (10-K Item 9A internal controls)
- Going-concern language in auditor opinion
- Late filings (10-K or 10-Q)
- Audit-fee jumps > 30% YoY without an acquisition explanation

Primary sources: 1987 [LT 11188]; 1990 [LT 15304–15313]; 2006 [LT 25819]; 2002 [TX 36757]; 2004 [TX 41499, 41509]; 2005 [TX 47903, 47946]; 2008 [TX 58969 Munger: "the accounting profession utterly failed us"].

### D9 — Buyback optics (PRE-VALUATION indicators only)

⚠ Phase-order constraint: accounting runs in Phase 3, valuation in Phase 5. The final "buyback price vs intrinsic value" comparison CANNOT live in accounting — IV doesn't exist yet. That final comparison moves to Phase 5C Step 1.5 (post-valuation). See `phases/step1e_pipeline.md` and `underwriteability_gate.md`.

Accounting flags buyback OPTICS using pre-valuation indicators:
- Avg buyback price last 5y vs **book value per share** (persistent premium = optics signal)
- Avg buyback price vs **trailing 5y trading range** (concentration at range highs = optics signal)
- **EPS-optics language** in management commentary tying buybacks to "EPS growth" or "EPS accretion" as primary justification
- Buybacks **coincident with insider selling** (capital-allocation flag — management exiting while company buys)
- Buybacks **funded by debt issuance** during expansion (leverage-up to buy-back at peak multiples)
- Buybacks **accelerating during obvious overvaluation signals** (e.g., peak multiples vs the company's own 10y history)

Buffett 1984 [LT 5989]: *"major repurchases at prices well below per-share intrinsic business value immediately increase, in a highly significant way, that value… By making repurchases when a company's market value is well below its business value, management clearly demonstrates that it is given to actions that enhance the wealth of shareholders."*

Buffett 1984 [LT 6019]: *"A manager who consistently turns his back on repurchases, when these clearly are in the interests of owners, reveals more than he knows of his motivations… His heart is not listening to his mouth – and, after a while, neither will the market."*

### D10 — Derivatives / mark-to-model / long-dated Black-Scholes critique

For companies with Level 3 books, derivative-heavy financials, or material long-dated option SBC:

- Black-Scholes is a "know-nothing value system" for long-dated options (Munger 2003 [TX 37923])
- Mark-to-model is "a sewer" (Munger 2002 [TX 34985])
- Front-ended derivatives profits produce earnings without cash (Buffett 1999 [TX 21033])

Compound flag: Level 3 + long-dated derivatives book + smooth segment earnings (D7) = high-confidence flag.

Buffett 2008 [LT 28351]: *"We endorse mark-to-market accounting. I will explain later, however, why I believe the Black-Scholes formula, even though it is the standard for establishing the dollar liability for options, produces strange results when the long-term variety are being valued."*

Buffett 2010 [LT 30133]: *"Black-Scholes produces wildly inappropriate values when applied to long-dated options… Part of the appeal of Black-Scholes to auditors and regulators is that it produces a precise number… We would rather be approximately right than precisely wrong."*

Primary sources: 1995 [TX 4174] (Carol Loomis Fortune article); 1999 [TX 21024, 21033] Munger/Buffett on derivative accounting; 2001 [TX 31650 Munger]; 2002 [TX 34985 Munger "sewer"]; 2002 [TX 35008] (Enron mark-to-model); 2003 [TX 37923 Munger]; 2004 [TX 42316] (counterparties both reporting profits — zero-sum game); 2004 [TX 42354 Munger]; 2007 [LT 28259]; 2008 [LT 28351]; 2010 [LT 30133].

---

## Tier III — Governance (3 principles; route to management agent)

The accounting agent surfaces Tier-III evidence under `=== TIER-III CULTURE/GOVERNANCE EVIDENCE (routes to management agent) ===`. The management agent owns the candor verdict; accounting does NOT issue the management judgment.

### G1 — Audit-committee orientation (Buffett's four questions)

Buffett 2004 [TX 41499]: *"the trick, as I've said, is really to have the auditors more worried about the audit committee than they are worried about the management."*

Indicators of audit-committee independence:
- Committee meets separately with auditors WITHOUT management present
- Written-record questions to auditors (audit-committee report in proxy may disclose these)
- Auditor turnover driven by committee dissatisfaction, NOT management preference (cross-reference D8)
- Committee chair's industry expertise + financial-services background

Buffett's four questions an audit committee should ask the auditors [TX 41509]:
1. Would the auditors have prepared the statements materially differently if they had sole responsibility?
2. Do the disclosures fully convey material information to a reasonable investor?
3. Would the auditor be comfortable serving as CEO of the audit committee (would they sign the statements)?
4. Are they aware of any income/expense timing shifting to make this period look better or worse than next?

Operational rule: read the audit-committee report in the DEF 14A. Flag if it does not address Buffett's four-question equivalents in substance.

### G2 — Comp-committee composition + grant structure

Buffett 2009 [TX 63739]: *"people are not looking for Dobermans. They're looking for Cocker Spaniels… and they're looking for Cocker Spaniels that are waving — wagging their tails, very friendly."*

Indicators of pro-shareholder comp committee:
- Performance-hurdled options (vesting tied to ROIC or shareholder value, not stock price)
- Restricted stock with cost-of-capital adjustments
- Multi-year vesting tied to long-term metrics
- Clawback provisions

Indicators of cocker-spaniel comp committee:
- Fixed-strike options with no hurdles
- Long-tenured wealthy executives receiving large new option grants
- Re-pricing of underwater options
- Performance metrics measured against benchmarks the company can game (revenue without ROIC; "adjusted EBITDA" — cross-reference M3)

Primary sources: 2003 [TX 35323]; 2009 [TX 63739].

### G3 — Accounting optics as management candor signal (routes to management agent)

When management chooses transactions, financing, metrics, or presentation to improve accounting optics rather than economics, surface as evidence. Examples:
- Acquisition structure designed to maximize "adjusted EBITDA" growth despite negative owner-earnings impact
- Lease vs purchase decision driven by balance-sheet optics (off-balance-sheet treatment) rather than economics
- Receivables securitization to move debt off-balance-sheet
- Revenue recognition methods chosen at the aggressive end of ASC 606 range
- "Adjusted" earnings reconciliations that expand over time (more line items added)
- Buyback programs announced just before earnings reports to support stock price

Buffett's framing (1984 [LT 4568], 1988 [LT 12206 cooperative-accountant joke]): management's accounting choices reveal their character independent of operating results.

The accounting agent surfaces the EVIDENCE; the management agent owns the candor VERDICT.

Primary sources: 1984 [LT 4568]; 1988 [LT 12206]; 1994 [TX 892–927]; multiple [TX 3532–3543, 10640].

---

## Tier IV — Disposition (3 principles)

### X1 — Cultural correlation

Buffett 2016 [LT 36594]: *"bad behavior is contagious: CEOs who overtly look for ways to report high numbers tend to foster a culture in which subordinates strive to be 'helpful' as well. Goals like that can lead, for example, to insurers underestimating their loss reserves."*

Operational rule: if Tier-II flags fire in **multiple separate accounting domains** (e.g., aggressive non-GAAP AND opaque footnotes AND audit-trail deltas), the verdict downgrades to **Concerning** regardless of any individual flag's severity. The accounting culture is one culture; correlated fires across domains are stronger evidence than a single high-severity fire.

### X2 — Avoidance > detection (judgment-anchored)

Munger 2003 [TX 34049–34076]:

> *"if you set out to con somebody, after a while you con yourself."*

Some industries have base rates of accounting opacity high enough that the right move is to opt out of underwriting rather than forensically clear each individual flag. The accounting agent surfaces inputs; the **opt-out flag** (see verdict design below) carries the propagation signal.

**X2 is judgment-anchored, not mechanically defined.** Three worked examples to anchor adjudication (see also the X2 worked-examples block below).

### X3 — Opt-out propagation to Stage-0

Per Buffett 2008 [TX 53670]:

> *"if a business gets to the point where we think the industry in which it operates, the competitive position or anything is so chancy that we can't really come up with a figure, we don't really try to compensate for that sort of thing by having some extra large margin of safety. We really want to try to go on to something that we understand better."*

Wider MoS does not rescue unanalyzability. The opt-out flag (NOT the verdict tier) carries the gate-propagation signal — see verdict design block.

---

## Verdict design (4-tier verdict + separate opt-out flag)

The accounting agent emits TWO orthogonal outputs, not one. Conflating them was rejected during the v2 review.

### Field 1 — Accounting quality verdict (4 tiers)

| Verdict | Criteria |
|---|---|
| **Clean** | 0 Tier-I material adjustments, 0 Tier-II flags, 0 Tier-III fails |
| **Acceptable with caveats** | Minor Tier-I adjustments, ≤ 1 Tier-II flag, 0 Tier-III fails |
| **Concerning** | Material Tier-I adjustments, OR ≥ 2 Tier-II flags, OR any Tier-III fail, OR X1 cultural-correlation fire |
| **Conservative** | Tier-I adjustments UNDERSTATE rather than overstate; evidence of hidden value (over-reserved insurance, R&D fully expensed at capital-generative firm, over-depreciated PP&E with replacement cost > book) |

### Field 2 — Opt-out flag (separate dimension)

| Flag | Trigger |
|---|---|
| **NONE** | Standard case; no Stage-0 propagation pressure |
| **WATCH** | Specific Tier-II flags fired but bridge still computes; surface in Stage-0 confidence prose only |
| **RECOMMEND PARTIAL** | Estimates dominate a material line item; cannot fully bridge to economic earnings; X2/X3 evidence accumulated |
| **RECOMMEND TOO HARD** | Statements too opaque / promotional / fraud-pattern-laden to underwrite; X2 avoidance threshold met |

### Why the separation matters

A 5-tier scale with "Walk-away" as a 5th level forces one dimension to do two jobs: judge quality AND signal gate propagation. A business can have **Acceptable quality** (the bridge computes, no individual flag is severe) AND a **RECOMMEND PARTIAL** opt-out flag (one specific estimate is structurally unanalyzable). The separation lets the analyst express that.

### Stage-0 cascade (binding unless explicitly escalated)

The Stage-0 underwriteability cascade reads the **opt-out flag**, not the verdict tier. The cascade is **binding unless explicitly escalated to Phase 5C reconciliation** — silent override is forbidden; escalation requires source-backed written documentation. See `references/underwriteability_gate.md` for the cascade rules.

```
Opt-out flag = RECOMMEND TOO HARD    → Stage 0 forced TOO HARD.
Opt-out flag = RECOMMEND PARTIAL     → UNDERWRITABLE downgrades to PARTIAL; PARTIAL stays PARTIAL.
Opt-out flag = WATCH                 → caveats surfaced in Stage-0 confidence prose; no automatic downgrade.
Opt-out flag = NONE                  → no Stage-0 effect from accounting.
```

The verdict tier separately feeds:
- `agents/management.md` (Concerning + G3 evidence → management agent owns candor verdict)
- `agents/final_memo.md` Section 4 (verdict + bridge magnitude reported in three-questions structure)
- Phase 5C reconciliation propagation check (Step 1.5 — see `phases/step1e_pipeline.md`)

---

## Skill-policy defaults block

These operational thresholds are **skill policy derived from Buffett evidence, NOT literal Buffett formulas**. Verify per-company; escalate to user if the policy default conflicts with company-specific evidence.

| Threshold | Value | Skill-policy anchor |
|---|---|---|
| M4 maintenance capex (capital-intensive) | 60–80% of total capex | BNSF 2016 [TX 92685]: "the true maintenance capex… is higher than 60 percent of that number" |
| M5 amortization split | ~20% real / ~80% non-real | Berkshire 2014 [LT 33819]: "We would call about 20% of these 'real,' the rest not" |
| M6 pension gap flag | Gap > 2pp vs long-Treasury | Buffett 2007 [LT 27354]: S&P 363 avg 8% assumption vs <5% long-Treasury (~3pp gap qualitatively flagged) |
| M7 recurring "non-recurring" count | ≥ 3 of 10y, similar-in-nature | Buffett 1992 [LT 17466] + 2016 [LT 36589–36597] qualitative framings |
| M7 recurring "non-recurring" magnitude | > 20% of cumulative NI | Skill-policy threshold; magnitude alone fires regardless of count |
| M8 MTM separation trigger | Marketable securities > 20% of total assets | Skill-policy threshold derived from 2017–2019 [LT 37164, 37766, 38185] framings |
| Phase 5C Step 1.5 propagation threshold | sign-flip OR \|bridge magnitude\| > 25% of \|GAAP NI\| | Skill-policy threshold; sign-flip alone always fires |
| Phase 5C bridge-% denominator floor | $50M on \|GAAP NI\| | Skill-policy floor to avoid explosive ratios near zero GAAP NI (modern SaaS often near-zero or negative) |
| M2 SBC dilution flag | 5y FDS growth > 3%/yr after buyback offset | Skill-policy threshold |
| D8 audit-fee jump flag | > 30% YoY without acquisition explanation | Skill-policy threshold |

When in doubt, lean conservative (a flag that turns out spurious costs a footnote; a missed flag costs decision integrity).

---

## X2 worked-examples block (judgment anchors)

X2 is judgment-anchored. These three worked examples anchor adjudication — they are NOT exhaustive criteria.

### Example 1 — SPAC-vintage rollup

Profile:
- 5+ acquisitions in 3 years
- Opaque PPA footnotes (intangibles roll-forward not clearly mapped to acquisitions)
- Recurring "integration" charges that have NOT abated by year 3
- Acquisition-accretive presentation language (every acquisition "accretive to EPS in year 1")
- "Adjusted EBITDA" growth dominating IR communication
- Goodwill > 30% of total assets with no impairment history

Expected fires: M3 (EBITDA lead-KPI); M5 (large non-real amortization); M7 (recurring integration); D1 (goodwill spurious — possibly); D2 (synergy fiction); D3 (segmentation possibly aggregating to obscure acquisition-specific economics); X1 (cultural correlation).

Expected verdict: **Concerning** with opt-out flag **RECOMMEND PARTIAL** (estimates dominate; specific acquisition-deal economics not separately verifiable).

### Example 2 — Chinese reverse merger / cross-jurisdiction holdco

Profile:
- Related-party transactions in 10-K footnotes (loans to controlling shareholder; sales to related entities)
- Auditor change within 18 months (D8 fires)
- Segment earnings smoother than peer-segment volatility (D7 fires)
- VIE structure with cross-border ownership (D4 opacity)
- Cash held at multiple unaudited Chinese subsidiaries
- Restatement or non-reliance 8-K within 24 months

Expected fires: D4 (footnote opacity); D7 (smooth-earnings tooth-fairy); D8 (audit-trail deltas); G1 (audit committee likely fails Buffett's four-questions test); X1 (cultural correlation across all of these).

Expected verdict: **Concerning** with opt-out flag **RECOMMEND TOO HARD** (statements too opaque / fraud-pattern-laden to underwrite; X2 avoidance threshold met).

### Example 3 — High-Level-3 derivatives-trading financial

Profile:
- Material Level 3 fair-value book on balance sheet (> 20% of total assets)
- Segment with smooth quarterly earnings inside a complex/illiquid derivatives book (D7 + D10 compound)
- Long-dated option positions valued via Black-Scholes despite Munger's known critique
- "Risk-management" footnotes that don't quantify VaR or scenario sensitivities
- Front-ended trading profits with cash conversion < 50% of GAAP NI

Expected fires: D4 (footnote opacity on Level 3); D7 (smooth segment earnings vs underlying volatility); D10 (Black-Scholes long-dated + mark-to-model); X1 (cultural correlation: smooth earnings + opaque marks + Black-Scholes choice).

Expected verdict: **Concerning** with opt-out flag **RECOMMEND TOO HARD** (the entire book is a mark-to-model exercise; bridge cannot be verified).

### When in doubt

Lean toward opt-out flag = **WATCH** rather than **NONE**. The cost of WATCH is a caveat in Stage-0 confidence prose; the cost of missing X2 is a propagated bad valuation.

---

## Sources block

Dense corpus regions used in derivation:

**Letters (`Berkshire-Hathaway-Letters-to-Shareholders_to2024.md`):**
- 1977 [LT 21–44] — earliest accounting principle (ROE > EPS framing)
- 1979 [LT 925–946] — EPS stopped-clock + "primary test" of managerial performance
- 1983 [LT 5626–5797] — Goodwill and Its Amortization appendix (foundational for D1, M5)
- 1984 [LT 6688] — auditor limits on long-tail reserves (D5)
- 1985 [LT 5989, 6019, 8085] — buyback discipline (D9), SBC framing (M2)
- 1986 [LT 9642, 10467–10557, 10513, 10535] — owner-earnings foundational, EBITDA "absurdity" (M3), float concept (D6)
- 1987–1988 [LT 11188, 12184–12195, 12202–12232, 12253–12277] — three-questions frame (F2), two-plus-two (F3), segmentation (D3), cooperative-accountant joke
- 1989 [LT 14725] — EBITDA "abomination"
- 1990–1992 [LT 15304–15416, 17466, 18208] — synergy fiction (D2), big-bath restructuring (M7), SBC compensation (M2)
- 1997 [LT 23116, 23215, 23489–23492] — float + reserve framings, synergy
- 2006–2007 [LT 25819, 26376, 26680, 27353–27410] — Enron-footnote precedent (D4), pension normalization (M6), two-pillar valuation (D6)
- 2012 [LT 31830, 31841] — amortization category framing (M5), Wells Fargo core-deposit fiction (M5)
- 2014–2015 [LT 33819, 33826, 35528, 35536, 35540] — 20/80 split (M5), BNSF maint capex (M4), SBC "most egregious"
- 2016 [LT 36122, 36589–36597, 36612, 36594] — recurring non-recurring (M7), cultural correlation (X1)
- 2017–2019 [LT 37164, 37766, 37817, 37831, 37834, 38185] — MTM separation (M8), non-real amort add-back (M5), maint capex (M4)
- 2024 [LT 41099] — EBITDA "banned measurement"

**Transcripts (`Berkshire Meeting Transcripts - 1994 - 2022 (1).md`):**
- 1994–1996 [TX 892–927, 4174, 4673, 8750, 8956] — early goodwill, derivatives precursor, float
- 1997–1999 [TX 9936, 13386, 17321, 18522, 21024, 21033, 21461, 21472, 21781, 22180] — SBC handling, EBITDA "utter nonsense", derivative accounting, warrant-method, big-bath
- 2001–2004 [TX 28543, 30050, 30095, 30104, 31650, 34049–34076, 34985, 35008, 35323, 35653, 36757, 37923, 40193, 40210, 40227, 40239, 40242, 41499, 41509, 41568, 42316, 42354] — GEICO maintenance split, pension assumption, derivative "sewer", Black-Scholes critique, audit-committee four questions, big-bath, optics-feeds-management
- 2005–2009 [TX 47903, 47946, 53670, 53672, 58366, 58969, 62803, 62826, 62830, 63739] — long-tail reserves, GFC framings, walk-away discipline (X3), Wells Fargo core-deposit, AIGFP tooth-fairy (D7), comp committee Dobermans
- 2011–2017 [TX 71298, 74445, 92638, 92685, 95846, 95867, 97507, 97523, 97542, 99004, 102266] — two-step economics-vs-management, EBITDA "bullshit earnings", bank loan-loss provisioning, BNSF maint anchor (M4), post-2018 MTM frustration

This sources block intentionally clusters lines by topic — the agent does NOT need to re-quote these in every output. Cite by [LT n] or [TX n] when a specific principle fires.
