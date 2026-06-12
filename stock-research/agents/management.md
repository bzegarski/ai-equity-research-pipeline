# Agent E — Management

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS:
- `{BASE}/raw/proxy.md` (canonical)
- `{BASE}/raw/insider.md` (canonical)
- `{BASE}/raw/transcripts.md` (canonical, includes TRANSCRIPT_SOURCE_QUALITY header)
- `{BASE}/raw/recent_8k.txt` (recent material events — executive changes, guidance revisions, departures)
- `{BASE}/raw/_chunks/item7.txt` (10-K Item 7 / MD&A — needed for capital-allocation table: acquisitions, buyback history, capex breakdown)
- `{BASE}/steps/step7_accounting.md` (specifically the `=== TIER-III CULTURE/GOVERNANCE EVIDENCE ===` block and the accounting verdict; consume as management-candor signals separate from operational track record. Management agent OWNS the candor verdict; accounting agent provides evidence, not the verdict.)

If `transcripts.md` starts with `TRANSCRIPT_SOURCE_QUALITY: unavailable`, skip transcript-dependent claims.
If it starts with `TRANSCRIPT_SOURCE_QUALITY: structured_summary`, downgrade transcript-derived claims to Medium confidence at most.

DO NOT read the full canonical 10-K. The proxy + insider + transcripts + recent 8-Ks + Item 7 chunk are the management-quality inputs.

RESEARCH DEPTH — SHALLOW: 1-3 targeted WebSearches at most (e.g. verify executive tenure dates).

## TASK

Evaluate {TICKER} management by what they DID, not what they SAID — except where comparing promises to outcomes.

1. **INSIDER OWNERSHIP AND SKIN IN THE GAME:** CEO/CFO ownership %? Open-market personal purchases (strongest signal)? Notable selling patterns — distinguish routine 10b5-1 plan sales from discretionary. Cross-reference 10-Q Item 5 plan adoption dates (in proxy.md or insider.md). Cluster buying or selling by multiple insiders?
2. **COMPENSATION DESIGN:** What metrics determine pay? Are they the right metrics for long-term value creation? Problematic features: guaranteed bonuses, low hurdles, repriced options, excessive SBC?
3. **OPERATING COMPETENCE:** Evidence from execution on stated initiatives, market share gains or losses, operational improvements. Are they operators, capital allocators, or both? Both modes can create value — describe what this management team is and where the evidence supports the assessment.

4. **CAPITAL ALLOCATION COMPETENCE — REQUIRED TABLE:**
   Build this table for the last 5 years (use proxy + 10-K + transcripts as available):

   | Year | Acquisitions ($M) | Buybacks ($M, avg price) | Dividends ($M) | CapEx ($M) | Net FCF ($M) |

   Then assess:
   - **ACQUISITIONS:** For each major acquisition >$100M, what was paid? Subsequent performance? Any write-downs? Are acquisition multiples (EV/Revenue, EV/EBITDA) higher or lower than current company valuation? (Paying more for targets than own stock = poor discipline.)
   - **BUYBACK TIMING:** Compare average buyback price to current price. Avg > current = bought high (poor). Avg < current = bought at value (good). Was authorization actually used or repeatedly authorized but not executed?
   - **ORGANIC INVESTMENT:** R&D as % of revenue vs. peers. Growing or shrinking? 5-year-lag ROI on R&D if disclosed.
   - **DIVIDENDS:** Initiated, grown, or cut? What does this signal about reinvestment opportunities?
   - **VERDICT:** Strong / Adequate / Weak with one-sentence evidence per verdict.

5. **CANDOR AND CREDIBILITY:** Compare stated priorities from 3-5 years ago to actual outcomes — both directions. Targets met or exceeded? Conservative guidance that proved sandbagging? Targets quietly dropped or missed? Did management acknowledge failures candidly? (Candor is a strong positive signal in either direction; sandbagging beat-and-raise patterns are also worth flagging.) Use the promises-vs-outcomes table from `transcripts.md` if present.

6. **BOARD QUALITY:** Independent? Relevant expertise? Director ownership? Anti-takeover provisions or dual-class shares?

7. **RECENT MATERIAL EVENTS:** Read `recent_8k.txt`. Any executive departures, guidance revisions, restatements, or SEC inquiries since the most recent 10-K? Material events change the management assessment.

8. **ACCOUNTING-CANDOR CROSS-READ:** Read the Tier-III evidence from `step7_accounting.md`. If management has:
   - chosen acquisitions, metrics, or presentation to improve accounting optics rather than economics (G3)
   - promoted compensation-ignoring earnings or EBITDA-led narratives (M3, M2)
   - composed a comp committee that pays fixed-strike unhurdled options to long-tenured wealthy executives (G2)
   - operated under an audit committee that fails Buffett's four-question test (G1)
   ...these are management-candor signals separate from operational results. Cite the specific accounting-agent finding. If the accounting verdict is Concerning AND at least one G-tier flag fired, this is a material capital-allocation / character risk.

   Management agent owns the final candor verdict. Accounting agent surfaces evidence, but does not issue the management-candor judgment.

## OUTPUT FORMAT — label exactly:

```
=== OPERATING COMPETENCE VERDICT ===
[strong / adequate / weak — with evidence]

=== CAPITAL ALLOCATION VERDICT ===
[strong / adequate / weak — with evidence + the table from item 4]

=== CANDOR AND ALIGNMENT VERDICT ===
[strong / adequate / weak — with evidence]

=== RECENT MATERIAL EVENTS ===
[any 8-K-disclosed events since most recent 10-K, or "none material"]

=== FINAL MANAGEMENT VERDICT ===
Strengthens case / Neutral / Material risk
[3-5 sentence justification citing all four verdicts above]
```

Apply claim labeling.

OUTPUT FILE: `{BASE}/steps/step8_management.md`
