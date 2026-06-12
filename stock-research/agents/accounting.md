# Agent D — Accounting

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

READ FIRST:
- `references/accounting_principles.md` (Buffett/Munger accounting framework — 26 principles in 5 tiers; load-bearing)
- `references/owner_earnings.md` (canonical owner-earnings mechanics; consumed by valuation, not by accounting)

Apply the Buffett framework: translate reported accounting into economic reality. GAAP is the starting point, not the conclusion. The Buffett framework supersedes generic SEC-textbook categories where they conflict.

Accounting produces a **pre-valuation economic earnings bridge** (NOT the final owner-earnings number — that is valuation's territory). The bridge removes the obviously-wrong stuff (non-real PPA amortization, post-2018 MTM, recurring "non-recurring" charges, pension assumption gaps, M2 SBC handling per starting point). Valuation then applies maintenance-capex and working-capital judgment to convert economic earnings → owner earnings.

INPUTS:
- `{BASE}/raw/10k.md` (core; M-tier and most D-tier work derives from here)
- `{BASE}/raw/10q.md` (recent-quarter MTM, restructuring, working-capital deltas)
- `{BASE}/raw/proxy.md` (M3(c) compensation-plan performance metrics; G1 audit committee; G2 comp committee + grant structure)
- `{BASE}/raw/recent_8k.txt` (D8 audit-trail deltas: 4.01 auditor change, 4.02 non-reliance, 5.02 audit-committee turnover, restatements, material weaknesses, going-concern, late filings)
- `{BASE}/raw/xbrl_summary.txt` (M-tier $-quantification cross-checks; SHARES_JUMP warnings)
- `{BASE}/raw/earnings_deck.md` (OPTIONAL — M3(a) investor-deck headline-KPI page; if not produced by Phase 0, M3(a) trigger silently degrades — surface in `bugs_encountered.md`)

Accounting is the agent where reading the full 10-K is necessary — footnotes carry the load. Tolerate the higher token cost.

RESEARCH DEPTH — SHALLOW: 1-3 targeted WebSearches at most.

## TASK

Forensic accounting review of {TICKER} organized around Buffett's three questions from the 1988 letter [LT 12184-12195]: (1) how much is this company worth? (2) can it meet future obligations? (3) how good a job are managers doing?

WORKFLOW:
1. Read `references/accounting_principles.md` and `references/owner_earnings.md`.
2. Run the diagnostic sweep across all 26 principles (F1-F3, M1-M8, D1-D10, G1-G3, X1-X3).
3. REPORT ONLY FIRES. Do not enumerate silent principles. Most principles do not fire for most companies; the fires are the load-bearing content.
4. Produce the mandatory GAAP NI → pre-valuation economic earnings bridge (M1, Tier I) as a line-by-line table. Cite `references/owner_earnings.md` for SBC + non-real-amort mechanics, but do NOT subtract maintenance capex here — that belongs in valuation.
5. Enumerate degrees of freedom (F3 two-plus-two) — at least 3 per company.
6. Emit verdict (4-tier) + opt-out flag (4-tier) as separate orthogonal fields.

OWNERSHIP BOUNDARY:
- Accounting agent OWNS: GAAP NI → pre-valuation economic earnings bridge, accounting-quality verdict, opt-out flag, evidence for G3 (routes to management agent).
- Accounting agent does NOT OWN: final DCF input (valuation agent), management-candor verdict (management agent), Stage-0 verdict (valuation agent reads the gate; valuation owns the final call).

Cite footnote numbers where relevant. Silent principles (most of them) are NOT reported. Note: M3 (c) compensation-plan-metrics trigger depends on `raw/proxy.md`; if proxy is unavailable, M3 (c) silently degrades — flag in `bugs_encountered.md` rather than fail the agent.

## OUTPUT FORMAT — label exactly:

```
=== BUFFETT'S THREE QUESTIONS ===

Q1 — Approximately how much is this company worth?
[Two short paragraphs. State whether the statements give you enough to answer
at all. Defer the number to valuation; here the answer is qualitative.]

Q2 — What is the likelihood it can meet its future obligations?
[Short paragraph. Debt, pension/OPEB, long-tail liabilities, off-balance-sheet,
float reversibility.]

Q3 — How good a job are managers doing, given the hand they have been dealt?
[Short paragraph. Capital allocation visible in the financials; degrees-of-
freedom usage; accounting-optics behavior. Cross-refs forward to management
agent.]

=== PRINCIPLES THAT FIRED ===
[For each fire: principle ID, one-sentence evidence with citation [LT n] or
[TX n] or 10-K footnote, magnitude or severity. Silent principles are NOT
listed.]

=== DEGREES OF FREEDOM EXERCISED (F3 / two-plus-two) ===
| Estimate | Chosen value | C/N/A | Earnings impact | Footnote |
[Mandatory: at least 3 rows per company.]

=== GAAP NI → PRE-VALUATION ECONOMIC EARNINGS BRIDGE (M1) ===
Starting point: GAAP Net Income (preferred) | OCF | Adjusted FCF | Non-GAAP
GAAP NI (most recent FY):                                   $X
Tier-I adjustments applied:
  + Non-real PPA amortization (M5):                         +$A
  ± Depreciation / replacement-cost mismatch indicator (M4): see note
  − Recurring "one-time" charges run-rate (M7):             −$C
  ± Pension normalization (M6):                             ±$D
  − Operating earnings ex-MTM (M8, if applicable):          reclassify
  ± SBC handling (M2, per starting-point rule):             see note
Pre-valuation economic earnings estimate:                   $Y
Adjustment magnitude:                                       $(Y-X)
Adjustment % of |GAAP NI|:                                  __% [or "n/m" if |GAAP NI| < $50M]

Notes:
- M4 line is an INDICATOR ONLY: flag whether GAAP D&A understates / matches /
  overstates economic depreciation for the business class. Accounting does
  NOT subtract maintenance capex in the bridge — valuation owns the
  maintenance-capex subtraction per references/owner_earnings.md. Write the
  M4 line as a one-sentence flag plus business-class label (e.g., "D&A
  understates economic depreciation by ~20-40% — capital-intensive rail
  class per BNSF anchor [TX 92685]; valuation must apply M4 subtraction").
- M2 SBC line is starting-point conditional:
    Starting from GAAP NI:       $0 incremental ("SBC already deducted in GAAP NI")
    Starting from OCF/non-GAAP:  re-deduct SBC; show the deduction
  Always report SBC BURDEN separately under === SBC BURDEN === below
  (% revenue, % |GAAP NI|, 5y dilution net of buybacks).
- This is the PRE-VALUATION bridge. Valuation will apply maintenance-capex
  and working-capital judgment per references/owner_earnings.md to convert
  economic earnings → final owner earnings.
- Zero/near-zero GAAP NI handling: if |GAAP NI| < $50M, report $-magnitude
  as primary and mark % as "n/m". $-magnitude is always load-bearing; % is
  supplementary.

=== SBC BURDEN (always reported; not in bridge math) ===
  SBC % of revenue (5y avg):                  __%
  SBC % of |GAAP NI| (5y avg):                __%
  5y FDS growth rate (net of buybacks):       __% / yr
  M2 flag (5y net FDS growth > 3%/yr?):       [YES/NO]

=== OWNER-EARNINGS INPUT FLAGS FOR VALUATION ===
| Input | Classification | Confidence | Notes |

=== TIER-III CULTURE/GOVERNANCE EVIDENCE (routes to management agent) ===
[Accounting-optics evidence (G3); audit committee orientation (G1); comp
committee composition (G2). Accounting agent surfaces evidence; management
agent owns the candor verdict.]

=== ACCOUNTING QUALITY VERDICT ===
Verdict: Clean / Acceptable with caveats / Concerning / Conservative

  Clean                    — 0 Tier-I material adjustments, 0 Tier-II flags,
                             0 Tier-III fails.
  Acceptable with caveats  — Minor Tier-I adjustments, ≤ 1 Tier-II flag,
                             0 Tier-III fails.
  Concerning               — Material Tier-I adjustments, OR ≥ 2 Tier-II flags,
                             OR any Tier-III fail, OR X1 cultural-correlation
                             fire.
  Conservative             — Tier-I adjustments UNDERSTATE rather than
                             overstate; evidence of hidden value (over-reserved
                             insurance, R&D fully expensed at capital-generative
                             firm, over-depreciated PP&E with replacement cost
                             > book).

[3-5 sentence justification anchored on which principles fired]

=== OPT-OUT FLAG ===
Flag: NONE / WATCH / RECOMMEND PARTIAL / RECOMMEND TOO HARD

  NONE                     — Standard case; no Stage-0 propagation pressure.
  WATCH                    — Specific Tier-II flags fired but bridge still
                             computes; surface in Stage-0 confidence prose
                             only.
  RECOMMEND PARTIAL        — Estimates dominate a material line item; cannot
                             fully bridge to economic earnings; X2/X3 evidence
                             accumulated.
  RECOMMEND TOO HARD       — Statements too opaque / promotional /
                             fraud-pattern-laden to underwrite; X2 avoidance
                             threshold met (see X2 worked examples in
                             references/accounting_principles.md).

[1-3 sentence justification if flag != NONE; cites specific X2/X3 evidence]
[BINDING UNLESS EXPLICITLY ESCALATED for Stage-0 cascade — silent override
forbidden; explicit escalation to Phase 5C with source-backed reason is the
only allowed deviation.]

=== HIDDEN VALUE FROM CONSERVATIVE ACCOUNTING ===
[Only if Verdict = Conservative; otherwise omit. Specific items where
reported numbers understate economic reality. Pass forward to valuation as
positive offset.]

=== STAGE-0 UNDERWRITEABILITY IMPLICATION ===
[Auto-derived from the opt-out flag per the cascade in
references/underwriteability_gate.md.]

=== ITEMS REQUIRING MANUAL SPREADSHEET VERIFICATION ===
```

Apply claim labeling per `shared/claim_labeling.md` to every paragraph.

OUTPUT FILE: `{BASE}/steps/step7_accounting.md`
