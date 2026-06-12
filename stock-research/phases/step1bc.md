# Step 1B + 1C — CC independent summarization and cross-check of Codex

Run when: `--step1b` flag.

Substitute `{TICKER}` and `{BASE}` throughout.

First: append to `{BASE}/bugs_encountered.md`:
```
## Step 1B+1C
```

**IMPORTANT:** Do not read any Codex output files (`*_codex.md`) before completing Step 1B. Independence is the entire point. Read only the raw source files.

(Note: This intra-CC discipline complements the genuine inter-terminal independence: Codex is a different model running in a different terminal on Step 1A. The instruction below ensures CC's reading isn't anchored to Codex's framing.)

## Step 1B — Summarize independently

Read these files:
- `{BASE}/raw/10k_raw.txt` (or `_chunks/item1.txt` etc. if chunked) + `10k_xbrl.json` + `xbrl_summary.txt`
- `{BASE}/raw/10q_raw.txt`
- `{BASE}/raw/proxy_raw.txt`
- `{BASE}/raw/competitors_raw.txt`
- `{BASE}/raw/insider_raw.txt`
- `{BASE}/raw/transcripts_raw.txt` (read its TRANSCRIPT_SOURCE_QUALITY header first)
- `{BASE}/raw/recent_8k.txt`

Apply `shared/claim_labeling.md` and `shared/writing_style.md` throughout. Tag every numerical claim with its source. If `transcripts_raw.txt` has `TRANSCRIPT_SOURCE_QUALITY: structured_summary`, downgrade transcript-derived claims to Medium confidence at most.

**Non-standard metric discipline (symmetric with Codex Step 1A):** preserve the issuer's exact wording for "ARR", "annual revenue run rate", "annualized revenue", "bookings", "backlog", "RPO", and similar non-standard operating metrics. Do **not** expand "ARR" as "annual recurring revenue" unless the source itself says "recurring" or "annualized recurring revenue". Label point-in-time annualizations as `run-rate, not proven recurring` unless contracts or management wording prove recurrence. If the source uses conflicting shorthand and long-form wording, quote both and prefer the long-form issuer wording in the summary. This rule applies to every `*_cc.md` summary and every xcheck file.

### Write `{BASE}/raw/10k_cc.md` covering:

- Business description: what it sells, segments, revenue breakdown by segment, geography
- Every revenue figure from `xbrl_summary.txt` for the most recent 3 fiscal years
- Gross margin, operating margin, net margin (from XBRL)
- Balance sheet: cash, long-term debt, goodwill (from XBRL)
- Cash flow: operating, capex, free cash flow (from XBRL)
- Key operational metrics from MD&A (store counts, units, active customers — quote verbatim)
- Brand portfolio: list each brand with its ownership status. Quote Item 1 verbatim for any brand described as sold, divested, or in wind-down. Do not infer status.
- Manufacturing geography: quote the exact words from the 10-K. If the filing says "predominantly Vietnam," write that. Do not convert to a percentage.
- Top 5 risk factors from Item 1A (1-2 sentences each)
- Auditor name and any disclosed material weaknesses
- **Forward-contracted disclosures (MANDATORY when disclosed; symmetric with Codex Step 1A):** capture each of these from the 10-K body, MD&A, or notes — quote source verbatim with `[FACT|10-K Item N|High]` tags:
  - RPO, backlog, remaining performance obligations, order book, bookings, or contracted revenue: total size, year-over-year change, duration, and expected conversion timing (e.g. "expected to recognize X% within 12 months")
  - Deferred revenue, contract liabilities, unearned revenue, billings, or customer advances, split current vs long-term when disclosed
  - Lease commitments, purchase obligations, take-or-pay commitments, capacity commitments, and leases not yet commenced — especially off-balance-sheet data-center, manufacturing, fleet, store, or infrastructure capacity
  - Material partnership, supplier, customer, joint-venture, or strategic-agreement terms: amendment dates, extension dates, exclusivity windows, IP-licensing rights, revenue-share caps, minimum commitments, termination rights, and amendment mechanics
  - Segment-level gross margin and operating margin percentages when disclosed (% form, not just $ revenue and operating income)
  - Forward effective tax rate guidance, known tax-law changes, tax-settlement mechanics, and normalized tax-rate commentary, distinct from historical ETR

  If the issuer does not disclose a given item, write `[NOT DISCLOSED IN 10-K]` for that line — do not omit silently. Rationale: at n=6 these forward-contracted disclosures are load-bearing for multi-year theses and are exactly what the cc/codex cross-check is designed to surface. (CC's [NOT DISCLOSED] is unconditional — Codex's equivalent rule is conditional on materiality; CC chooses unconditional to make absences visible to the xcheck.)

### Write `{BASE}/raw/10q_cc.md` covering:

- Most recent quarter revenue vs. prior year (from XBRL or MD&A — tag source)
- Most recent quarter gross and operating margins vs. prior year
- Any guidance changes or revised outlook statements (quote verbatim)
- **Item 5 disclosures:** (NEW — IMP-1 fix) share repurchase program (authorization amount, shares repurchased in the quarter, average price, remaining authorization); insider trading policy; any Rule 10b5-1 plan adoptions or terminations disclosed for named executives. Quote the exact plan adoption dates verbatim — these determine whether insider sales are discretionary or pre-scheduled.
- **Forward-contracted updates (MANDATORY; symmetric with Codex Step 1A):** any change vs the most recent 10-K in RPO/backlog, deferred revenue or contract liabilities, leases not yet commenced, partnership-agreement terms, segment GM% or OpInc% guidance, or forward ETR. Quote verbatim with source tags. If unchanged or not addressed in the quarter, state so explicitly.

### Write `{BASE}/raw/proxy_cc.md` covering:

- CEO name, title, compensation total + components (base, bonus, equity)
- CFO and other named executive officers: same
- Director ownership table: name, role, shares held, % of outstanding
- Executive tenure: year each joined the company (quote exact language)
- Compensation metrics for annual bonus and LTI
- Any related-party transactions

### Write `{BASE}/raw/competitors_cc.md` covering:

- For each competitor: company name, ticker, key revenue scale (from competitor XBRL block in `competitors_raw.txt`), gross margin, operating margin, and how they describe their competitive positioning in Item 1.

### Write `{BASE}/raw/insider_cc.md` covering:

- Table of insider transactions: who, title, transaction type, shares, value, date
- Net buying/selling summary
- Distinguish open-market purchases (strongest signal) from routine 10b5-1 sales (cross-reference 10-Q Item 5 plan dates)

### Write `{BASE}/raw/transcripts_cc.md`:

- If raw file's first non-header line says `TRANSCRIPT_UNAVAILABLE`, write that and stop.
- Otherwise: key management themes repeated across calls, specific guidance statements with dates, promises made and whether they match later filing outcomes.

**Promises-vs-outcomes table** (NEW — A1 from plan):

For EACH earnings call available in the transcript data:

| Call date | Metric | Guidance given | Actual outcome | Source | Beat/Miss/Met |

Required to include at minimum: revenue guidance for next quarter/year; specific growth rate targets; margin expansion targets; product launch / market entry timeline promises.

After building, compute:
- **BEAT RATE:** calls where actuals ≥ guidance / total calls with verifiable guidance
- **SANDBAGGING SIGNAL:** if beat rate > 75% and avg beat > 5%, management consistently underpromises
- **MISS SIGNAL:** if miss rate > 25%, management is systematically overoptimistic

Cross-check actuals against `xbrl_summary.txt` and 10-K/10-Q MD&A. Flag any promise that was given then quietly abandoned without explanation.

**Gating rules:**
- If only 1 quarter of transcript available, table is single-row and beat-rate computation skipped (note: "insufficient quarters for trend").
- If `TRANSCRIPT_SOURCE_QUALITY: structured_summary`, tag entire table Medium confidence.

## Step 1C — Cross-check Codex's summaries

Now read the Codex summaries:
- `{BASE}/raw/10k_codex.md`, `10q_codex.md`, `proxy_codex.md`, `insider_codex.md`, `transcripts_codex.md`, `customer_perspective_codex.md`

(Note: per the n=6 PAYX/MSFT/NVO/SNOW/DECK iteration, Codex does not produce `competitors_codex.md` — competitor analysis is single-source CC by design because the dual-pass on competitor summaries produced redundant broad summaries with no high-yield catches. If a `competitors_codex.md` file appears, ignore it; do not log a missing-file warning.)

For each document pair (`*_cc.md` vs `*_codex.md`), write a cross-check file (`10k_cc_xcheck.md`, `10q_cc_xcheck.md`, `proxy_cc_xcheck.md`, `insider_cc_xcheck.md`, `transcripts_cc_xcheck.md`).

Format:

```
=== AGREEMENTS ===
[Each claim where both summaries agree. Confidence: High.]

=== DISCREPANCIES ===
[For each:]
CC said: [exact quote]
Codex said: [exact quote]
Raw source says: [what raw txt or xbrl_summary actually says]
Verdict: [which is correct / both wrong / genuinely ambiguous]
Confidence after verification: [High / Medium / Low]

=== CODEX FOUND, CC MISSED ===
[Items Codex captured that CC did not. Decision: include or exclude. Reason.]

=== CC FOUND, CODEX MISSED ===
[Items CC captured that Codex did not. Decision: include or exclude. Reason.]

=== METRIC EXPANSION ===
[Any case where one summary expanded a non-standard metric (e.g. ARR -> "annual recurring revenue", "annualized revenue" -> "ARR") that the other preserved verbatim. Verdict resolution: the side preserving issuer wording is correct unless the source explicitly defines the recurrence or annualization claim.]
```

A cross-check file with zero discrepancies is a warning sign — flag in `bugs_encountered.md` for re-examination.

## Instruct the user

Append to `{BASE}/bugs_encountered.md`:
- Files that could not be read
- Cross-checks with zero discrepancies
- If clean: `[Step 1B+1C] OK`

Output:

```
==================================================
STEP 1B+1C COMPLETE -- {TICKER}
==================================================

CC summaries written:
  [done] 10k_cc.md
  [done] 10q_cc.md (with Item 5 / 10b5-1 plan coverage)
  [done] proxy_cc.md
  [done] competitors_cc.md
  [done] insider_cc.md
  [done] transcripts_cc.md (with promises-vs-outcomes table)

CC cross-checks of Codex output written (5 files; no competitors_xcheck):
  [done] 10k_cc_xcheck.md
  [done] 10q_cc_xcheck.md
  [done] proxy_cc_xcheck.md
  [done] insider_cc_xcheck.md
  [done] transcripts_cc_xcheck.md

Discrepancies flagged: [list count per document]

==================================================
NEXT -> Switch to your Codex terminal and run:

  $stock-research-codex {TICKER} --step1d

(Note the `$` prefix — Codex activation syntax is `$`, not `/`.)

Codex will cross-check CC's summaries (4 docs; competitors are CC-only). When done,
return here and run:

  /stock-research {TICKER} --step1e

→ /clear before running the next flag (preserves your context window).
==================================================
```

Stop here.
