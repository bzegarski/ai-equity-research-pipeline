# Agent C — Current Moat

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS (focused subset):
- `{BASE}/raw/_chunks/item1.txt` (10-K Item 1)
- `{BASE}/raw/competitors.md` (canonical, with financial-scale data)

DO NOT read full canonical 10-K, proxy, or transcripts. The CURRENT-moat task uses these inputs.

RESEARCH DEPTH — SHALLOW: 1-3 targeted WebSearches maximum.

## TASK

Assess {TICKER}'s CURRENT competitive advantages only. Do not predict durability — that is a separate question (Phase 4).

1. **ADVANTAGE IDENTIFICATION:** For each potential advantage, name the mechanism: brand/reputation, network effects, switching costs, cost advantage (scale/process/structural), regulatory barrier, distribution advantage. For each: specific evidence supporting it AND specific evidence casting doubt on it.
2. **EVIDENCE QUALITY:** Strong (visible in financial outcomes) / Moderate (plausible, requires interpretation) / Weak (claimed by management, hard to verify).
3. **REPLICATION TEST:** Could a well-funded, competent competitor replicate this business's economics by spending $1 billion over 5 years? Walk through what they'd need to build and what obstacles they'd face. Be honest.
4. **COMPETITIVE POSITION DIRECTION:** Strengthening / stable / weakening — based on 3-5 years of filings. Evidence: market share trends, pricing trends, competitor behavior.

Do not give a moat rating. Do not speculate about the future.

## OUTPUT FORMAT — label exactly:

```
=== COMPETITIVE ADVANTAGE TABLE ===
=== EVIDENCE FOR AND AGAINST EACH ADVANTAGE ===
=== REPLICATION TEST RESULT ===
=== COMPETITIVE POSITION DIRECTION ===
```

Apply claim labeling throughout.

OUTPUT FILE: `{BASE}/steps/step5_moat_current.md`
