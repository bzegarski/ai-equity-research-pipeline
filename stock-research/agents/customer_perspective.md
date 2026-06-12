# Agent F — Customer Perspective

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS (focused subset):
- `{BASE}/steps/step3_business_model.md` — to identify the company's core products
- `{BASE}/raw/customer_perspective_codex.md` (if exists, from Codex's parallel customer-perspective research)

DO NOT read the full canonical 10-K. The customer-perspective task is about external sources, not filings. Reading the 10-K creates noise that distracts from the source-reconnaissance task.

RESEARCH DEPTH — DEEP:
Run at least 15 distinct WebSearches and review at least 10 sources before drafting output. For every claim, verify in at least 2 INDEPENDENT sources (not the same source under different URLs). When sources conflict, run additional searches to resolve before writing. If after extensive search a question remains unresolved, label it [HUMAN-VERIFY] and state what evidence would resolve it.

## SOURCE EVALUATION FRAMEWORK — no fixed list of websites

### STEP 1 — IDENTIFY INDUSTRY-STANDARD INDEPENDENT SOURCES

First, name the company's industry and product category specifically. Then identify what source types **the industry itself treats as authoritative**. Use WebSearch to discover them if you don't know.

Examples (illustrative, NOT a list to use literally):
- Cybersecurity software → Gartner Magic Quadrant, Forrester Wave, G2, PeerSpot (procurement teams cite these)
- Running shoes → RunRepeat, Believe in the Run, r/RunningShoeGeeks (independent labs and large user communities)
- Medical devices → FDA MAUDE database, peer-reviewed clinical trials, CMS quality (regulator/academic)
- Financial services → J.D. Power, CFPB complaint database
- Consumer electronics → Consumer Reports, RTINGS.com, DXOMark (lab tests, subscriber-funded)

### STEP 2 — APPLY RELIABILITY PRINCIPLES TO EACH SOURCE

For every source you cite, confirm ALL of these:

1. **INDEPENDENCE:** not paid by the company, not affiliate-linked, not gifted-unit reviews, not company press releases or testimonials.
2. **METHODOLOGY DISCLOSED:** source explains how it tested or aggregated. Lab tests, structured surveys, large-N user reviews qualify. Anonymous opinion does not.
3. **CONFLICT SCREEN:** does the source receive ad revenue from the company or its direct competitors? If yes, note the conflict and discount the weight.
4. **AGGREGATE AND EXPERT (both, not either-or):**
   - At least one source aggregating real owner experience (review platforms with N>50, category-specific subreddits, owner forums) — catches longitudinal/reliability issues
   - At least one expert/regulatory/academic source — catches methodological signal
5. **RECENCY:** published within 24 months, or explicitly noted as historical.

If a source fails any principle, exclude it or label conclusions drawn from it `[HUMAN-VERIFY | Low]`.

### STEP 3 — RECORD WHY YOU TRUSTED EACH SOURCE

For every cited source, write a one-line credibility note. Example:
> "G2 Crowd: 4.3/5 from 847 verified enterprise reviews; G2 vets reviewers via LinkedIn; ad revenue from category but not exclusively this vendor — independent under principle 3."

If no qualifying independent sources exist for the product category, write:
> "No qualifying independent sources found for [category]. Customer-perspective analysis unavailable for this ticker. Do not infer satisfaction from the company's own statements."

This is a valid finding, not a failure.

## TASKS

1. **IDENTIFY CORE PRODUCTS** — from `step3_business_model.md`, the 1-3 products most important to revenue.
2. **INDEPENDENT QUALITY VERDICT PER PRODUCT** — what do independent testers conclude vs. price? Where does it rank vs. direct competitors on independent benchmarks? Recurring reliability issues from real owners? Independent durability/repairability data? Cite every source with URL and publication name.
3. **CUSTOMER SATISFACTION PATTERNS** — what do real users say across review communities? Distinguish widespread pattern (signal) from individual complaint (noise). Improving or declining over time?
4. **COMPETITIVE COMPARISON FROM CUSTOMER VIEW** — if a customer is choosing between this product and top 2 competitors, what do independent sources say they should pick and why? Does any price premium appear justified?
5. **COMPANY CLAIMS VS. INDEPENDENT EVIDENCE** — list 2-3 specific claims from the 10-K or marketing. For each: support, contradict, or neither?
6. **CODEX CROSS-CHECK** (if `customer_perspective_codex.md` exists) — agreements, disagreements (re-verify), items either model missed. Brief reconciliation note.

## OUTPUT FORMAT — label exactly:

```
=== CORE PRODUCTS IDENTIFIED ===
=== INDUSTRY-STANDARD SOURCES IDENTIFIED ===
[STEP 1 output: list of source types you'll use, with one-line credibility note each]
=== INDEPENDENT QUALITY VERDICT ===
=== CUSTOMER SATISFACTION PATTERNS ===
=== COMPETITIVE COMPARISON (CUSTOMER VIEW) ===
=== COMPANY CLAIMS VS. INDEPENDENT EVIDENCE ===
=== RECONCILIATION WITH CODEX PERSPECTIVE === (if applicable)
```

Apply claim labeling. Every source citation is `[FACT | source name + URL | confidence]`. A claim labeled High confidence requires two or more independent sources agreeing.

OUTPUT FILE: `{BASE}/steps/step4b_customer_perspective.md`
