# Agent B — Industry

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS (focused subset to keep agent within context window):
- `{BASE}/raw/_chunks/item1.txt` (10-K Item 1 — for the company's own industry framing)
- `{BASE}/raw/competitors.md` (canonical, includes financial-scale data per competitor)
- `{BASE}/raw/recent_8k.txt` (recent material events)

DO NOT read the full canonical 10-K, proxy, or other agents' outputs. The industry-mapping task does not need them and they crowd out the deep-research budget.

RESEARCH DEPTH — DEEP:
Run at least 15 distinct WebSearches and review at least 10 sources before drafting output. For every claim, verify in at least 2 INDEPENDENT sources (not the same source under different URLs). When sources conflict, run additional searches to resolve before writing. If after extensive search a question remains unresolved, label it [HUMAN-VERIFY] and state what evidence would resolve it.

INDUSTRY-DATA SOURCING GUIDANCE:
- Gartner / IDC / Forrester press releases (free; appear at vendor.com/newsroom or vendor sites)
  - Pattern: `"[industry] market size Gartner 2025 press release"`
  - Pattern: `"[company] Gartner Magic Quadrant [year] leader"`
- Government / trade data:
  - BLS (Bureau of Labor Statistics): industry employment and productivity
  - Census Bureau: industry revenue benchmarks
  - Industry trade associations often publish state-of-industry reports
- Always cite the specific source URL, publication date, and the specific number. "Industry grew 11% per Gartner July 2025 press release" not "industry grew ~10%." Undated or unsourced statistics are [HUMAN-VERIFY | Low].

## TASK

Map the industry structure for {TICKER}'s sector before forming any company-level view. Start from the industry.

1. **VALUE CHAIN AND PROFIT POOLS:** Where do profits concentrate? Which parts are structurally attractive?
2. **HOW CUSTOMERS CHOOSE:** Price vs. quality vs. switching costs vs. relationships?
3. **COMPETITIVE LANDSCAPE:** Major competitors? Basis of competition? Consolidating or fragmenting? Use the financial-scale data in `competitors.md` to anchor relative sizing.
4. **SUPPLIER AND CUSTOMER POWER:** Bargaining dynamics? Intermediaries extracting value?
5. **GROWTH DRIVERS:** Secular or cyclical? Reasonable 5-10 year base rate?
6. **REGULATORY ENVIRONMENT:** What regulations matter? Pending changes?
7. **STRUCTURAL CHANGES (3-5 year outlook):** Technology shifts, disruption, consolidation?
8. **COMMON OUTSIDER MISUNDERSTANDING:** Where might the market's view of this industry be incomplete — in either direction (overestimating or underestimating)? State both possibilities and indicate which (if either) the evidence currently supports.

## OUTPUT FORMAT — label exactly:

```
=== INDUSTRY MAP ===
=== PROFIT-POOL MAP ===
=== COMPETITIVE LANDSCAPE ===
=== MAIN STRUCTURAL CHANGES UNDERWAY ===
=== REMAINING UNKNOWNS ===
```

Apply claim labeling. Cite all sources with URLs and dates.

OUTPUT FILE: `{BASE}/steps/step4_industry.md`
