# Phase 6 — Counter-Attack

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS:
- All files in `{BASE}/steps/` (read everything)
- Optionally: `{BASE}/steps/step10_codex_attack.md` if Codex's adversarial pass was run (--step11e flag indicates this)

## TASK

Your job is to attack this thesis. You are the prosecution. Make the strongest possible case AGAINST the investment. Be adversarial but evidence-based. Focus on how intelligent investors fool themselves.

### ATTACK 1 — FALSE-QUALITY ATTACK
Is this business less attractive than the research suggests? Could current economics be cyclical, temporary, or accounting-inflated?

### ATTACK 2 — FALSE-MOAT ATTACK
What appears durable but may not be? Cite a specific historical precedent of a similar moat failing in this or an adjacent industry.

### ATTACK 3 — FALSE-MANAGEMENT ATTACK
Where could incentives, empire-building, or capital allocation behavior disappoint in ways the analysis didn't capture?

### ATTACK 4 — FALSE-VALUATION ATTACK
Which assumptions carry too much weight? What if normalized earnings are lower? Growth runway shorter? Compare against the reverse-DCF in `step9_valuation.md`.

### ATTACK 5 — NARRATIVE LOCK-IN ATTACK
Where is the research most vulnerable to confirmation bias? Where was a conclusion likely formed early with evidence selected to support it?

### ATTACK 6 — CONTRADICTION SCAN
Contradictions between research outputs? Does the business model imply something that the accounting contradicts? Does the management assessment conflict with the competitive advantage assessment?

### ATTACK 7 — PRE-MORTEM (deep research required)

5 years from now, this investment has lost 50%+ permanently. Write 3 plausible scenarios. For each: what went wrong, what warning signs are visible today, probability estimate, AND a NAMED real comparable that suffered a similar loss.

**Anti-confabulation:** If you cannot WebSearch your way to a verifiable case, write `"no verified analog found"` rather than invent one. Cite the analog's company name, year, and mechanism.

**Two-sentence analog rule (NEW per n=6 evidence):** when you name a historical analog, produce TWO sentences:
1. What's similar — the load-bearing analogy.
2. What's specifically different — one concrete way the analog fails to map perfectly.

Without sentence (2), the analog SHOULD NOT be cited. NVO Phase 6 named Sovaldi/Harvoni as a "patent cliff analog"; it was price + volume + competition, not a clean patent expiry. The asymmetry sentence prevents over-clean framing. Verification D enforces this rule.

RESEARCH DEPTH for this attack — DEEP: at least 10 WebSearches, multiple sources per cited analog.

### ATTACK 8 — BASE RATE / OUTSIDE VIEW (deep research required)

**Anti-confabulation: anchor base rates to EXTERNAL PUBLISHED DISTRIBUTIONS.**

Step 1 — Define the reference class precisely: "Companies with [growth rate X%, industry Y, FCF margin Z%, valuation multiple W×]." The reference class must be defined based on observable characteristics of {TICKER} TODAY — not its ideal future state.

Step 2 — Find the base rate using EXTERNAL SOURCES:
- Aswath Damodaran data sets (pages.stern.nyu.edu/~adamodar/) — sector return / growth distributions
- Kenneth French data library (mba.tuck.dartmouth.edu/pages/faculty/ken.french/) — factor portfolios
- S&P / MSCI sector return tables
- Peer-reviewed academic papers on equity returns by category
- Cite the external source with URL.

**Do NOT generate "5-10 historical analogs" from your own training data — that produces confabulation.** Anchor base rates to externally published distributions.

Step 3 — TICKER vs. the reference class:
- State explicitly the one or two reasons {TICKER} might outperform its reference class.
- Apply the discipline: is this a genuine differentiation or a "this time is different" rationalization?
- If you cannot articulate a specific, verifiable structural difference from the reference class, the base rate governs.

REQUIRED OUTPUT:
```
Reference class:               [definition]
External base-rate source:     [URL + citation]
Base-rate 5-year S&P beat rate: X% (per cited source)
TICKER's claimed differentiation: [1-2 sentences]
Is differentiation verifiable today or dependent on future execution? [verify/future]
Outside-view verdict: [Base rate governs / Differentiation is verifiable / Differentiation is claimed but unverifiable]
```

## INTEGRATING CODEX'S ATTACK (if present)

If `step10_codex_attack.md` exists, integrate its findings:
- Per attack: which points did Codex make that you didn't? Add them.
- Where Codex disagreed with you, re-examine the evidence and write the more correct version.
- A combined attack is stronger than either alone.

## OUTPUT FORMAT — label exactly:

```
=== STRONGEST ANTI-THESIS ===
=== FALSE-POSITIVE RISK MAP ===
=== MOST FRAGILE ASSUMPTIONS ===
=== CONTRADICTIONS FOUND ===
=== PRE-MORTEM SCENARIOS ===
[3 scenarios, each with named analog or "no verified analog found"]

=== BASE RATE ANCHOR ===
[per the format above; with external source URL]

=== FALSIFYING EVIDENCE LIST ===
[specific, measurable things that would kill the thesis]
```

OUTPUT FILE: `{BASE}/steps/step10_counter_attack.md`
