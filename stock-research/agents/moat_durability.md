# Phase 4 — Moat Durability

PREPEND TO PROMPT: contents of `shared/mission_frame.md`, `shared/claim_labeling.md`, `shared/writing_style.md`.

INPUTS:
- `{BASE}/raw/10k.md` (canonical)
- `{BASE}/raw/competitors.md` (canonical)
- `{BASE}/steps/step5_moat_current.md` (current moat assessment from Agent C)

This step assesses DURABILITY. The prior step assessed CURRENT advantages.

RESEARCH DEPTH — DEEP:
Run at least 15 distinct WebSearches and review at least 10 sources before drafting output. For every claim, verify in at least 2 INDEPENDENT sources. When sources conflict, run additional searches to resolve.

## ANTI-CONFABULATION RULES

Every disruption vector requires a NAMED HISTORICAL ANALOG — a real company that lost a similar advantage. **Confabulation prohibited:** if you cannot WebSearch your way to a verifiable case, write `"no verified analog found"` rather than invent one. Cite the analog's company name, year, advantage type, and mechanism of erosion.

**Two-sentence analog rule (NEW per n=6 evidence):** when you name a historical analog, you MUST produce TWO sentences:
1. **What's similar** — the load-bearing analogy (the specific element that maps).
2. **What's specifically different** — one concrete way the analog fails to map perfectly.

Without sentence (2), the analog SHOULD NOT be cited. Removes over-clean framing (NVO Phase 6: Sovaldi/Harvoni framed as "patent-cliff analog" when it was actually price + volume + competition collapse). The asymmetry sentence is required even when it weakens the analogy. Verification D will reject Phase 4 / 6 analogs that lack the asymmetry sentence.

Every disruption vector must include a CONCRETE MECHANISM — not "competition intensifies" but the specific pathway by which it damages the company's economics.

## TASK

1. **DURABILITY PER ADVANTAGE:** For each advantage in `step5_moat_current.md` — what could weaken or destroy it? Has this type of advantage been historically durable in this industry? Name a real company that lost a similar advantage (or write "no verified analog found").

2. **DISRUPTION VECTORS:** 3-5 most realistic threats over 10 years. For each:
   - Concrete mechanism (specific damage pathway)
   - Historical precedent (named company, year, what happened)
   - Probability bucket: <5% / 5-15% / 15-30% / >30%
   - Early warning signs visible today
   - Whether the disruption is already underway

3. **CONFIDENCE TABLE:**
   - Current advantage exists: High / Moderate / Low
   - Advantage survives 3 years: High / Moderate / Low
   - Advantage survives 10 years: High / Moderate / Low

   If confidence drops steeply between timeframes, that gap IS the key risk.

4. **ATTACK TEST** (different from the replication test in step5):
   Adopt the perspective of the CEO of {TICKER}'s most dangerous competitor. You have $5B and have decided to destroy {TICKER}'s competitive position.

   Answer:
   - What is your optimal attack strategy? Not generic competitive moves — the specific lever, specific pricing, specific customer segment, specific time horizon.
   - What is the exact pitch to {TICKER}'s customers that might make them switch? Write 2-3 sentences as the competitor's salesperson.
   - What is {TICKER}'s likely response? Does it make your attack better or worse?
   - What is the 1 thing that makes your attack most likely to fail?

   The replication test asks "could someone build {TICKER} from scratch?" The attack test asks "how would a rational, motivated adversary actually fight?" Incumbents rarely get displaced by a better version of themselves — they get attacked at the edges.

5. **WHAT WOULD CHANGE THE ASSESSMENT:** Evidence that would raise or lower confidence in any direction.

## OUTPUT FORMAT — label exactly:

```
=== DURABILITY RISK ANALYSIS ===
=== DISRUPTION VECTORS ===
[Each with mechanism, named historical analog, probability, warning signs]

=== CONFIDENCE TABLE ===
| Horizon | Confidence |
| Now     | ... |
| 3 years | ... |
| 10 years| ... |

=== ATTACK TEST ===
[Strategy + pitch + likely response + most-likely failure]

=== WHAT WOULD CHANGE THE ASSESSMENT ===
```

OUTPUT FILE: `{BASE}/steps/step6_moat_durability.md`
