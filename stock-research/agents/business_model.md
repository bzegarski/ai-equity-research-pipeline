# Agent A — Business Model

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS:
- `{BASE}/raw/_chunks/item1.txt` (10-K Item 1 — Business)
- `{BASE}/raw/_chunks/item7.txt` (10-K Item 7 — MD&A)
- `{BASE}/raw/transcripts.md` (canonical, includes TRANSCRIPT_SOURCE_QUALITY header)

If `transcripts.md` starts with `TRANSCRIPT_SOURCE_QUALITY: unavailable`, skip transcript-dependent claims rather than guessing.
If it starts with `TRANSCRIPT_SOURCE_QUALITY: structured_summary`, downgrade transcript-derived claims to Medium confidence at most.

RESEARCH DEPTH — SHALLOW: 1-3 targeted WebSearches maximum. The answer to your question lives primarily in the 10-K.

## TASK

Analyze the business model for {TICKER} from first principles. Do not discuss valuation or stock price.

1. **WHAT DOES IT SELL?** Specific products/services, who pays, how pricing works. Revenue streams with approximate relative size.
2. **WHO ARE THE CUSTOMERS?** Consumer vs. enterprise vs. government? Concentration? Buying process and decision drivers?
3. **WHY DO CUSTOMERS CHOOSE THIS COMPANY?** Specific mechanism — not "great brand" but the concrete reason. "18-month implementation cost to switch" or "20% cost advantage from X."
4. **HOW DOES $1 REVENUE BECOME CASH?** Major cost buckets, what drives them. What reinvestment is required just to maintain current earnings? Does the company collect cash before or after paying suppliers?
5. **WHAT 2-4 VARIABLES MOST AFFECT THIS BUSINESS?** Which are within management control? Which are external?
6. **WHAT IS STILL UNCLEAR?** What would you ask management?

## OUTPUT FORMAT — label exactly:

```
=== BUSINESS MODEL SUMMARY ===
=== ECONOMIC ENGINE MAP ===
=== KEY VALUE DRIVERS ===
=== MAIN UNKNOWNS ===
=== IMPORTANT DISCLOSURES TO REVISIT ===
```

Apply claim labeling to every paragraph.

OUTPUT FILE: `{BASE}/steps/step3_business_model.md`
