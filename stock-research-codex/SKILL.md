---
name: stock-research-codex
description: Run Codex's assigned verification gates in a dual-model stock research pipeline. Use when the user invokes $stock-research-codex TICKER for Step 1A independent summaries, including resumable Step 1A substeps (--step1a-10k, --step1a-10q, --step1a-proxy, --step1a-insider, --step1a-transcripts, --step1a-customer, --step1a-status), $stock-research-codex TICKER --step1d for Step 1D cross-checks, $stock-research-codex TICKER --audit for Phase 0 audit, $stock-research-codex TICKER --consistency for cross-step thesis consistency, $stock-research-codex TICKER --valuation for independent Buffett-style owner-earnings valuation, $stock-research-codex TICKER --attack for optional adversarial counter-attack, $stock-research-codex TICKER --deep-customer for opt-in customer outside-source deep research, or $stock-research-codex TICKER --deep-attack-research for opt-in adversarial/base-rate deep research.
---

# Stock Research Codex

## Role

Act only as the Codex side of the stock research pipeline. The companion CC-side skill orchestrates the full pipeline.

- Phase 0 audit (`--audit`): verify CC's raw-file collection before Codex Step 1A.
- Step 1A (no flag): independently summarize selected raw sources, including the 10-K/annual filing, into six `*_codex.md` files. Use this all-in-one mode only when the raw files are compact enough to fit comfortably in context.
- Step 1A resumable substeps (`--step1a-10k`, `--step1a-10q`, `--step1a-proxy`, `--step1a-insider`, `--step1a-transcripts`, `--step1a-customer`, `--step1a-status`): write or check one Step 1A output at a time. Prefer these flags for large issuers, failed/resumed Step 1A runs, or any run that risks context overflow.
- Step 1D (`--step1d`): cross-check CC summaries against Codex summaries and raw sources.
- Cross-step consistency (`--consistency`): check CC's Phase 3 agents before Phase 4.
- Independent valuation (`--valuation`): compute Codex's independent Phase 5B Buffett-style owner-earnings valuation after CC writes `STEPS/step9_valuation_cc.md`, without reading CC's valuation output.
- Optional adversarial counter-attack (`--attack`): independently attack the thesis before final memo integration.
- Optional deep customer research (`--deep-customer`): create or ingest a manual ChatGPT.com Deep Research handoff for messy customer/review evidence.
- Optional deep attack research (`--deep-attack-research`): create or ingest a manual ChatGPT.com Deep Research handoff for outside-view base rates, historical analogs, and adversarial precedents.
- Do not produce final investment conclusions unless the `--attack` framework requires adversarial scenario judgments.
- After each step, tell the user exactly what to do next.

## Context Hygiene

After a completed Codex handoff, recommend a fresh Codex conversation before the next Codex phase unless the user is debugging or retrying the same phase. This prevents stale summaries, pasted CC output, old plans, or resolved corrections from contaminating later independent checks.

Use this exact terminal-only alert in completed-phase handoff messages. Do not write it into research output files:

```text
CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Skill Change Coordination

Any change to this Codex skill must be coordinated with the companion CC-side `stock-research` skill before it is treated as final. This includes router flags, file paths, file ownership, section labels, handoff messages, shared-reference usage, phase order, independence rules, validation behavior, and output formats.

Codex may ask CC questions or confirm proposed changes through the user. The user will relay Codex messages to CC and CC messages back to Codex. Do not silently make behavior-affecting skill changes that CC depends on without calling out the coordination need.

## Paths

For ticker `TICKER`:

- `BASE` resolves to a timestamped folder, **never** the bare `Research/TICKER`. CC's Phase 0 creates `Research/TICKER_D.M.YYYY` (e.g., `Research/MSFT_9.5.2026`). Codex must resolve to the same folder by globbing `~/Research/TICKER_*/` and picking the most recent mtime. Fall back to the legacy untimestamped path `~/Research/TICKER/` only if no `TICKER_*` folder exists. If neither exists, abort with: `No CC research folder for TICKER. CC must run Phase 0 first.`
- `RAW = BASE/raw`
- `STEPS = BASE/steps`
- `CODEX_BUGS = BASE/bugs_encountered_codex.md`
- `CODEX_REVIEW = BASE/codex_run_review.md`
- `CC_INBOX = RAW/cc_catches_against_codex.md`

Resolve `BASE` ONCE at the start of dispatch and use that exact path for every substitution downstream. Use uppercase ticker symbols in final handoff messages.

Before running any Codex phase, run this shared-reference preflight check. Verify these six CC-owned methodology files exist:

- `~/.claude/skills/stock-research/references/discount_rate_logic.md`
- `~/.claude/skills/stock-research/references/owner_earnings.md`
- `~/.claude/skills/stock-research/references/moat_durability_tiers.md`
- `~/.claude/skills/stock-research/references/valuation_methods.md`
- `~/.claude/skills/stock-research/references/three_tier_decision.md`
- `~/.claude/skills/stock-research/references/underwriteability_gate.md`

If any are missing, abort immediately with:

```text
REFERENCES MISSING: CC has not built shared references yet. Run CC's Phase C first.
```

Keep the agent-level precondition block in `agents/valuation_codex.md` as defense in depth.

Before starting any Codex phase, if `~/Research/_run_methodology_checklist.md` exists, read it. This is the neutral Round 3 methodology checklist.

Do not read any `*_post_run_checklist.md` files. Those are user-only post-run review files and would compromise independence.

## Codex Run Logging

Maintain Codex's own log. Do not append Codex-side issues to CC's `bugs_encountered.md`.

After every Codex phase, append or update `CODEX_BUGS` with this block:

```text
## [phase name] -- [date]

- Inputs missing or corrupt:
- Instruction ambiguity:
- Tool/search/API failures:
- Source-quality downgrades:
- Codex self-corrections:
- Unresolved handoff risks:
```

If a category has no items, write `none`. Record failures and workarounds even if the final output succeeded.

After `--attack`, write `CODEX_REVIEW` with these top-level sections so CC and Codex reviews are diffable:

```text
# Codex Run Review -- TICKER -- [date]

## Decision / Accuracy Delta From Prior View
## Bug Log Highlights
## Confabulation Check
## Cross-Check Substantive Ratio
## What Broke
## What Surprised
## What Was Generic
## CC Catches Against Codex I Saw Too Late
## Would My Output Have Changed If I Had Seen Them Earlier?
## Codex Catches Adopted / Rejected / Unknown
## Gate Value By Phase
## Skill Edits Recommended
```

The run review must state whether any Codex gate would have changed the final memo conclusion, valuation, or reliability disclosure.

For `--valuation`, log valuation-phase assumption risks in `CODEX_BUGS`, including underwriteability ambiguity, maintenance-capex ambiguity, owner-earnings starting-point ambiguity, SBC handling risk, FCF bridge gaps, discount-rate/cushion source issues, capital-allocation-test uncertainty, missing optional inputs, and possible reconciliation divergences. Do not call anything a CC/Codex divergence until CC reconciliation has compared both valuation files. Do not write to `CC_INBOX` during `--valuation`.

## Required Writing Standards

Apply these standards to every prose paragraph written into output files:

- Start every paragraph with `[FACT | source | confidence]`, `[INTERPRETATION | based on: X; Y | confidence]`, or `[HUMAN-VERIFY | confidence]`.
- Use `High` confidence for XBRL-verified facts or facts confirmed by two independent sources.
- Use `Medium` confidence for a single source.
- Use `Low` confidence for inferred, extrapolated, conflicting, or ambiguous claims.
- Tag every numerical claim with its source: XBRL concept name, or document/section plus approximate location.
- Write short, concrete sentences. Omit filler and vague words.
- Do not use unsupported words such as "significant", "substantial", "material", "robust", "synergies", "ecosystem", or "headwinds/tailwinds" without specific numbers.

## External Source Recency Discipline

Apply this only to external web sources outside SEC filings, XBRL, company filings, and primary transaction documents.

- For current-state customer, competitive, pricing, product, regulatory, market-share, management-title, or software/AI claims, record the source publication/update date when visible. If no date is visible, cite the access date.
- Prefer sources published or updated within 24 months for current-state claims. For fast-moving categories such as software, AI infrastructure, cybersecurity, semiconductors, and consumer electronics, prefer sources within 18 months.
- Do not discard an older source automatically. If it is the best available source for a current-state claim, write `[STALE-RISK]`, state the source date, and state whether a newer source was searched for and not found.
- Historical analogs, base-rate papers, methodology papers, and old events are not stale merely because they are old. Judge them on whether they support a historical or methodological claim rather than a current-state claim.
- Do not add a separate freshness gate. Apply this inside the existing source-quality, cross-check, and fact-check passes.

## Phase 0 Audit

Run Phase 0 audit when the user invokes `$stock-research-codex TICKER --audit`.

This step runs after CC's Phase 0 completes and before Codex's Step 1A.

### Inputs

Read these files:

- `RAW/phase0_log.txt`
- `RAW/filing_track.yml` if present
- `BASE/bugs_encountered.md` if present; otherwise `RAW/bugs_encountered.md` if present
- First 200 lines of `RAW/10k_raw.txt`
- `RAW/xbrl_summary.txt`
- `RAW/competitors_raw.txt` only for collection-presence assurance
- `RAW/insider_raw.txt`
- `RAW/recent_8k.txt` if it exists
- First 500 characters of `RAW/transcripts_raw.txt`

### Audit Checks

Perform these checks:

1. Does `10k_raw.txt` start with actual annual-filing business prose, not table-of-contents content? For domestic 10-K tracks, look for `Item 1.` followed by business description in the first 200 lines. For FPI tracks, tolerate mapped 20-F annual-report starts such as `Item 4` / company-information prose. If the first occurrence is in a TOC-shaped block, mark `CRITICAL`.
2. Does `xbrl_summary.txt` contain Revenue plus at least three other concepts such as NetIncome, GrossProfit, OperatingIncome, OperatingCashFlow, Cash, Debt, or SharesOutstanding?
3. Does `competitors_raw.txt` exist and contain non-whitespace content? Do not audit competitor coverage, XBRL margins, or peer completeness on the Codex side. Codex does not produce `competitors_codex.md`; the absence of a Codex competitor cross-check is expected and must not be treated as a Codex failure.
4. Does `insider_raw.txt` have transaction rows or an explicit no-data marker? Acceptable markers include `NO_INSIDER_DATA_FOUND`, `FPI_NO_FORM_4`, or equivalent FPI/PDMR limitation text. Empty file is `CRITICAL`; explicit FPI no-Form-4 markers are `INFO`, not failure.
5. Does `recent_8k.txt` exist? If yes, scan for `resignation`, `appointed`, `restatement`, `impairment`, `material weakness`, `SEC investigation`, and `going concern`. Flag matches as `MATERIAL_EVENT`.
6. Read the `TRANSCRIPT_SOURCE_QUALITY` header. If it says `structured_summary` or `unavailable`, note the required confidence-tag propagation.
7. Read `xbrl_summary.txt` SharesOutstanding rows. If any year-over-year change is greater than 30%, flag `POSSIBLE_SPLIT`.

### Output

Write `RAW/phase0_audit.md`:

```text
# Phase 0 Audit -- TICKER -- [date]

| Check | Result | Severity | Action |
|---|---|---|---|
| 10k_raw starts with Item 1 prose | YES/NO | OK/CRITICAL | ... |
| xbrl_summary has Revenue + 3 concepts | YES/NO | OK/CRITICAL | ... |
| competitors_raw exists and nonempty | YES/NO | OK/WARNING | Collection-presence check only; no Codex competitor summary is expected. |
| insider_raw has rows or NO_DATA marker | YES/NO | OK/CRITICAL | ... |
| recent_8k.txt exists | YES/NO | OK/WARNING | ... |
| transcript source quality | verbatim/summary/none | OK/INFO | ... |
| shares-outstanding split detection | clean/jumps | OK/INFO | ... |

## Material 8-K events found
[list any 8-Ks matching keywords; quote filing date and snippet]

## Recommendations
[Either: "Phase 0 audit OK with N warnings; proceed to Step 1A."
 Or: "CRITICAL issues found; re-run Phase 0 to fix [list issues] before proceeding to Step 1A."]
```

### Handoff

If any `CRITICAL` issue exists, tell the user:

```text
Phase 0 has CRITICAL issues. See raw/phase0_audit.md. Fix and re-run /stock-research TICKER before proceeding to Step 1A.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

If only `WARNING` or `INFO` issues exist, tell the user:

```text
Phase 0 audit OK with N warnings. Run $stock-research-codex TICKER to proceed to Step 1A, or use $stock-research-codex TICKER --step1a-10k to start the resumable Step 1A path for large/context-risk issuers.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Step 1A

Run Step 1A when the user invokes `$stock-research-codex TICKER` with no flag, or when the user invokes one resumable Step 1A substep:

- `--step1a-10k`: write `RAW/10k_codex.md`.
- `--step1a-10q`: write `RAW/10q_codex.md`.
- `--step1a-proxy`: write `RAW/proxy_codex.md`.
- `--step1a-insider`: write `RAW/insider_codex.md`.
- `--step1a-transcripts`: write `RAW/transcripts_codex.md`.
- `--step1a-customer`: write `RAW/customer_perspective_codex.md`.
- `--step1a-status`: check whether all six Step 1A files exist and are nonempty.

Use the no-flag all-in-one mode only when the raw files are compact enough to fit comfortably in context. For large issuers, failed runs, resumed runs, or any context-risk case, use the resumable substeps and write one output file per Codex conversation.

Resumable substep rules:

- Resolve `BASE`, run the shared-reference preflight, and read the neutral methodology checklist exactly as in every Codex phase.
- Do not read Claude Code output, do not open `*_cc.md`, and do not read any other Step 1A Codex output unless running `--step1a-status`.
- Read only the target-specific inputs listed below, then write the target output immediately and stop. Do not collect notes for other Step 1A files.
- Do not perform customer web research except during `--step1a-customer`.
- Treat each substep as its own Codex phase for `CODEX_BUGS` logging. If a prior all-in-one Step 1A failed from context overflow, log that failure and the resumable workaround.

Target-specific inputs:

- `--step1a-10k`: `filing_track.yml` if present, `10k_raw.txt`, `_chunks/item1.txt`, `_chunks/item1a.txt`, `_chunks/item7.txt`, `_chunks/item8.txt` if present, `xbrl_summary.txt`, and `recent_8k.txt` if present.
- `--step1a-10q`: `10q_raw.txt`, `xbrl_summary.txt` if needed for continuity, and `recent_8k.txt` if present.
- `--step1a-proxy`: `proxy_raw.txt`.
- `--step1a-insider`: `insider_raw.txt` and `10q_raw.txt` for Item 5 Rule 10b5-1 cross-reference.
- `--step1a-transcripts`: `transcripts_raw.txt`; read `10q_raw.txt` or `recent_8k.txt` only if needed to check whether later filings confirm or contradict a transcript-derived promise.
- `--step1a-customer`: use `10k_raw.txt` or `_chunks/item1.txt` only to identify the company's product categories, then qualifying customer-perspective web sources under the customer evidence framework below.
- `--step1a-status`: inspect only the expected six `*_codex.md` files for existence and nonzero length.

Critical independence rule:

- Do not read Claude Code output.
- Do not open any `*_cc.md` files.
- In no-flag all-in-one mode and `--step1a-10k`, summarize the annual filing and write `10k_codex.md`. For FPI tracks, treat the 20-F or mapped annual-report exhibit as the annual filing and still write `10k_codex.md`.
- Do not summarize competitors and do not write `competitors_codex.md`; CC owns competitor-file analysis per empirical scope narrowing.
- Form the summaries only from raw files under `RAW` plus qualifying customer-perspective web sources.

In all-in-one mode, read these raw files:

- `filing_track.yml` if present
- `10k_raw.txt`
- `_chunks/item1.txt`, `_chunks/item1a.txt`, `_chunks/item7.txt`, `_chunks/item8.txt` if present
- `xbrl_summary.txt`
- `10q_raw.txt`
- `proxy_raw.txt`
- `insider_raw.txt`
- `transcripts_raw.txt`
- `recent_8k.txt` if it exists

In all-in-one mode, write these six files to `RAW`:

- `10k_codex.md`
- `10q_codex.md`
- `proxy_codex.md`
- `insider_codex.md`
- `transcripts_codex.md`
- `customer_perspective_codex.md`

Non-standard metric discipline applies to every Step 1A output:

- Preserve the issuer's exact wording for `ARR`, "annual revenue run rate", "annualized revenue", "bookings", backlog, RPO, and similar non-standard operating metrics.
- Do not expand `ARR` as "annual recurring revenue" unless the source explicitly says "recurring" or "annualized recurring revenue".
- Label point-in-time annualizations as `run-rate (point-in-time), not proven recurring` unless contracts or management wording prove recurrence.
- If the source uses conflicting shorthand and long-form wording, quote both and prefer the long-form issuer wording in the summary.

### 10k_codex.md Coverage

Use the annual filing as the company baseline. If `_chunks/` exists, prefer the relevant chunks for focus and use `10k_raw.txt` only to resolve missing context. If no chunks exist, read the relevant annual-filing sections directly from `10k_raw.txt`.

Cover:

- Business description: what the company sells, customer type, segments, and geography.
- Revenue by segment and geography for the most recent three fiscal years when disclosed; use `xbrl_summary.txt` for audited financial totals and annual-filing text for segment/geography detail.
- Gross margin, operating margin, net margin, operating cash flow, capex, free cash flow, cash, long-term debt, goodwill, diluted shares, SBC, R&D, and SG&A when present in `xbrl_summary.txt`.
- Key operating metrics from MD&A, such as stores, units, active customers, ARR, bookings, backlog, retention, capacity, subscribers, or volumes. Quote the filing's wording for non-standard metrics.
- Brand or product-portfolio status. Quote exact annual-filing language for any brand, product, or segment described as sold, divested, discontinued, wound down, impaired, or held for sale.
- Manufacturing, sourcing, supply-chain, data-center, vendor, or geographic concentration. Quote qualitative language exactly; do not convert words like "predominantly" into percentages unless the filing gives the percentage.
- The top five risk factors that are specific enough to affect the thesis. Avoid boilerplate unless the risk links to a concrete business exposure.
- Auditor name, audit opinion issues, material weaknesses, going-concern language, restatements, or critical audit matters.
- Debt maturity, lease, acquisition, litigation, tax, pension, revenue-recognition, impairment, customer-concentration, and subsequent-event footnotes when they could change valuation, risk, or management assessment.

Forward-contracted disclosure search list -- mandatory when disclosed in the annual filing, MD&A, or notes:

- RPO, backlog, remaining performance obligations, order book, bookings, or contracted revenue: total size, year-over-year change, duration, and expected conversion timing.
- Deferred revenue, contract liabilities, unearned revenue, billings, or customer advances, split current versus long-term when disclosed.
- Lease commitments, purchase obligations, take-or-pay commitments, capacity commitments, and leases not yet commenced, especially off-balance-sheet data-center, manufacturing, fleet, store, or infrastructure capacity.
- Material partnership, supplier, customer, joint-venture, or strategic-agreement terms: amendment dates, extension dates, exclusivity windows, IP-licensing rights, revenue-share caps, minimum commitments, termination rights, and amendment mechanics.
- Segment-level gross margin and operating margin percentages when disclosed, not just dollar revenue and operating income.
- Forward effective-tax-rate guidance, known tax-law changes, tax-settlement mechanics, and normalized tax-rate commentary, distinct from historical ETR.

For every listed item, either capture the disclosed fact or write `[NOT DISCLOSED IN 10-K]` for that line rather than omitting it silently.

### 10q_codex.md Coverage

Focus on:

- Item 5 10b5-1 plan adoptions and terminations, with verbatim plan adoption dates.
- Share repurchase activity: authorization amount, shares repurchased in quarter, average price, and remaining authorization.
- Insider trading policy disclosures.
- MD&A guidance changes, quoted verbatim.
- Footnote disclosures that affect dilution, debt, acquisitions, revenue recognition, legal matters, or subsequent events.
- Forward-contracted updates versus the annual filing: RPO/backlog, deferred revenue or contract liabilities, leases not yet commenced, partnership-agreement terms, segment GM% or OpInc% guidance, and forward ETR. If unchanged or not addressed in the quarter, state that explicitly.

### proxy_codex.md Coverage

If `proxy_raw.txt` contains `FPI_NO_PROXY` or an equivalent foreign-private-issuer proxy limitation, write a limitation-only `proxy_codex.md` that states the missing domestic proxy equivalent. Use any remuneration-report or AGM raw file only when it is present in `RAW` and explicitly mapped by CC; do not infer domestic DEF 14A fields.

Cover:

- CEO and CFO compensation totals and components.
- NEO compensation totals and components.
- NEO bios with tenure, including year joined company, quoted verbatim from proxy bios.
- Director ownership table: name, role, shares, and percent outstanding.
- Compensation metrics for annual bonuses and long-term incentives.
- Related-party transactions.
- NGS ARR or other segment-level data if disclosed.

### insider_codex.md Coverage

If `insider_raw.txt` contains `FPI_NO_FORM_4`, `NO_INSIDER_DATA_FOUND`, or an equivalent PDMR/company-announcement limitation, write a limitation-only `insider_codex.md` and do not infer insider buying/selling from proxy holdings, remuneration tables, or management ownership.

Cover:

- Form 4 transaction table: insider name, role, date, transaction code, shares, and price.
- Net buying or selling summary across insiders.
- Open-market purchases, flagged separately.
- Discretionary sales versus Rule 10b5-1 plan sales.
- Cross-reference 10-Q Item 5 plan adoption dates when classifying Rule 10b5-1 plan sales.

### transcripts_codex.md Coverage

Read the `TRANSCRIPT_SOURCE_QUALITY` header at the top of `RAW/transcripts_raw.txt`.

- If the header says `structured_summary` or `unavailable`, propagate `Medium` confidence tags to every transcript-derived claim and state the limitation.
- Extract direct quotes only when verbatim text is confirmed.
- If transcripts are unavailable, write the limitation and stop.
- Otherwise, cover repeated management themes, specific guidance statements with dates, promises made, and whether later filings show the promises were kept.

### customer_perspective_codex.md Coverage

Use this criteria-based framework. Do not rely on a fixed list of websites.

#### Source Evaluation Framework

Step 1 -- Identify industry-standard independent sources:

- Name the company's industry and product category specifically.
- Identify what source types the industry itself treats as authoritative.
- Use WebSearch to discover them if needed.
- Examples are illustrative only: cybersecurity software may use Gartner Magic Quadrant, Forrester Wave, G2, and PeerSpot; running shoes may use RunRepeat, Believe in the Run, and category subreddits; medical devices may use FDA MAUDE, peer-reviewed clinical trials, and CMS quality data.

Step 2 -- Apply reliability principles to each source:

1. Independence: not paid by the company, not affiliate-linked, not gifted-unit reviews, not company press releases or testimonials.
2. Methodology disclosed: source explains how it tested or aggregated. Lab tests, structured surveys, and large-N user reviews qualify. Anonymous opinion does not.
3. Conflict screen: if the source receives ad revenue from the company or its direct competitors, note the conflict and discount the weight.
4. Aggregate and expert: use at least one source aggregating real owner experience, such as review platforms with `N > 50`, category-specific subreddits, or owner forums; and at least one expert, regulatory, or academic source.
5. Recency: published within 24 months for current-state claims, or explicitly noted as historical. For fast-moving categories, prefer sources within 18 months and mark older current-state evidence `[STALE-RISK]` unless a newer source confirms it.

If a source fails any principle, exclude it or label conclusions drawn from it `[HUMAN-VERIFY | Low]`.

#### Customer Evidence Canonical-Use Classifier

Do not use a binary aggregator block. Classify each customer, expert, regulator, review, or market-position source along four axes before deciding canonical use:

1. Authority: official/professional/regulatory body, original review platform, expert publication, user forum, company source, or third-party aggregator.
2. Primary vs derivative: whether the source directly hosts the underlying evidence or republishes/summarizes another source's evidence.
3. Access: whether Codex can read the underlying primary page, methodology, and current number directly.
4. Specificity: exact numeric claim, ranking/award/category position, qualitative pattern, or search lead only.

Canonical-use rules:

- Exact review counts, ratings, rankings, award placements, category positions, and "leader" claims require direct verification on the source that owns the underlying evidence.
- Official professional, trade, academic, government, or regulatory bodies may be canonical primary sources when the claim appears on that body's own site. Example: an APMA Seal listing on APMA's site is allowed for the fact that APMA recognizes the product.
- User-review platforms such as G2, Gartner Peer Insights, app stores, BBB, Trustpilot, Capterra, or similar platforms may be canonical for their own current counts/ratings only when the primary page is accessible and checked. If inaccessible, mark `[HUMAN-VERIFY]` and exclude the number from summary tables.
- Third-party aggregators or republished paid-research summaries may be used as search leads or qualitative context, not as primary support for exact numbers. Example: a news article saying Forrester ranked a vendor as a Leader is blocked unless the Forrester report or an accessible official Forrester page is checked; if three or more independent named outlets corroborate the same non-numeric claim, it may be used at Medium confidence with the access limitation stated.
- Uncategorized third-party sources are case-by-case at Medium confidence at most unless they clearly disclose original methodology and directly host the underlying evidence.

Worked examples:

- APMA Seal page on `apma.org`: Authority = professional medical body; Primary = yes for its own seal; Access = open if checked; Specificity = official recognition. Canonical use allowed for "APMA Seal listed."
- G2 vendor scorecard: Authority = user-review platform; Primary = yes only for G2's own page; Access = checked or not; Specificity = exact rating/count. Block exact figures unless the current G2 page is readable and checked.
- Forrester Wave cited by Reuters or another news article: Authority = paid research; Primary = no unless the Forrester report or accessible Forrester page is checked; Access = paywalled original not fetched; Specificity = ranking/leader claim. Block exact canonical claim unless primary Forrester evidence is checked; if three or more independent named outlets corroborate a non-numeric claim, use at Medium confidence with the limitation stated.
- NICE TA875 patient page: Authority = government/regulator; Primary = yes; Access = open if checked; Specificity = official standard or patient guidance. Canonical use allowed for the claim actually stated by NICE.
- Trade-association industry report on its own site: Authority = trade/standards body; Primary = yes; Access = open if checked; Specificity = report statistic or directional claim. Canonical use allowed at Medium confidence unless methodology is weak or conflicted.
- Capterra-style review aggregator: Authority = user-review aggregator; Primary = yes only for its own page; Specificity = exact rating/count. Block exact figures unless the current platform page is readable and checked; otherwise use as a search lead only.
- WSJ news report citing an internal company memo: Authority = news outlet of record; Primary = derivative for the memo quote and primary for the reporting; Access = article checked; Specificity = company quote or interpretation. Use the quoted company statement at Medium confidence; keep the outlet's interpretation at Medium or lower.
- Statista chart with no upstream citation: Authority = derivative data publisher; Primary = no; Access = upstream opaque; Specificity = charted number. Block canonical use and search for the upstream source.

End `customer_perspective_codex.md` with this table:

```text
## Numeric customer claims requiring primary-source verification

| Claim | Primary source checked? | Canonical-use status | Notes |
|---|---|---|---|
| ... | YES/NO | ALLOWED/BLOCKED | ... |
```

Step 3 -- Record why each source was trusted:

- For every cited source, write a one-line credibility note.
- Example: `G2 Crowd: 4.3/5 from 847 verified enterprise reviews; G2 vets reviewers via LinkedIn; ad revenue from category but not exclusively this vendor -- independent under principle 3.`

If no qualifying independent sources exist for this product category, write:

```text
No qualifying independent sources found for [category]. Customer-perspective analysis unavailable for this ticker. Do not infer satisfaction from the company's own statements.
```

This is a valid finding, not a failure.

#### Research Depth

Use risk-based customer research depth instead of a fixed search count. Start with 4-8 targeted searches and review 5-8 credible sources when the product category has accessible industry-standard evidence. Stop once the canonical-use classifier has enough evidence to support the claims being made; do not continue searching merely to satisfy a numeric quota.

Escalate depth only when customer evidence is load-bearing, conflicted, fragmented, inaccessible, or central to the moat or market thesis. In those cases, review at least 10 sources and keep searching until the conflict is resolved or the unresolved claim can be clearly labeled `[HUMAN-VERIFY]`.

For every claim used canonically, verify it in the primary source or two independent sources, not the same source under different URLs. When exact review counts, ratings, rankings, award placements, category positions, or "leader" claims cannot be checked at the primary source, block the number and state what evidence would resolve it.

### Handoff

After no-flag all-in-one mode writes the six files, tell the user:

```text
Step 1A done -- six Codex summaries written (10k, 10q, proxy, insider, transcripts, customer_perspective). Switch to CC and run /stock-research TICKER --step1b. CC will summarize independently and cross-check this output.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

After a resumable substep writes one file, tell the user exactly which file was written and the next command:

```text
Step 1A substep done -- wrote raw/[filename]. Continue in a fresh Codex conversation with: $stock-research-codex TICKER [next-step1a-flag]

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

Use this next-command sequence:

- after `--step1a-10k`: `$stock-research-codex TICKER --step1a-10q`
- after `--step1a-10q`: `$stock-research-codex TICKER --step1a-proxy`
- after `--step1a-proxy`: `$stock-research-codex TICKER --step1a-insider`
- after `--step1a-insider`: `$stock-research-codex TICKER --step1a-transcripts`
- after `--step1a-transcripts`: `$stock-research-codex TICKER --step1a-customer`
- after `--step1a-customer`: `$stock-research-codex TICKER --step1a-status`

When `--step1a-status` finds all six files exist and are nonempty, tell the user:

```text
Step 1A done -- six Codex summaries are present (10k, 10q, proxy, insider, transcripts, customer_perspective). Switch to CC and run /stock-research TICKER --step1b. CC will summarize independently and cross-check this output.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

When `--step1a-status` finds missing or empty files, list the missing files and tell the user the first missing substep command to run next. Do not proceed to Step 1D until the user returns with `--step1d`.

Stop after any Step 1A handoff. Do not proceed to Step 1D until the user returns with `--step1d`.

## Step 1D

Run Step 1D only when the user invokes `$stock-research-codex TICKER --step1d`.

Read the six CC summaries, six Codex summaries, and raw files needed to resolve disputes:

- `10k_cc.md`, `10k_codex.md`, `10k_raw.txt`, `xbrl_summary.txt`, and `_chunks/` files if present
- `10q_cc.md`, `10q_codex.md`, `10q_raw.txt`
- `proxy_cc.md`, `proxy_codex.md`, `proxy_raw.txt`
- `insider_cc.md`, `insider_codex.md`, `insider_raw.txt`, `10q_raw.txt`
- `transcripts_cc.md`, `transcripts_codex.md`, `transcripts_raw.txt`
- `customer_perspective_cc.md` if present, `customer_perspective_codex.md`, and cited web sources as needed

Write these six files to `RAW`:

- `10k_codex_xcheck.md`
- `10q_codex_xcheck.md`
- `proxy_codex_xcheck.md`
- `insider_codex_xcheck.md`
- `transcripts_codex_xcheck.md`
- `customer_perspective_codex_xcheck.md`

Each cross-check file must include these sections:

```text
=== AGREEMENTS ===
=== DISCREPANCIES ===
=== CC FOUND, YOU MISSED ===
=== YOU FOUND, CC MISSED ===
```

For every item in `DISCREPANCIES`, `CC FOUND, YOU MISSED`, and `YOU FOUND, CC MISSED`, include an `ADOPTION TARGET` field naming the canonical file(s) that should change if CC accepts the catch. Use `ADOPTION TARGET: none` only when the item is useful context but should not change a canonical or step file.

Prefer this table shape when practical:

```text
| Finding | Source resolution | Direction | ADOPTION TARGET | Recommended change |
|---|---|---|---|---|
| ... | ... | CC missed / Codex missed / disagreement | raw/proxy.md; steps/step8_management.md | ... |
```

Mandatory Step 1D checks:

- Forward-contracted disclosures: check whether either side omitted material RPO/backlog, deferred revenue or contract liabilities, leases not yet commenced, partnership terms, segment GM%/OpInc%, or forward ETR that appear in the raw source. Put omissions in `CC FOUND, YOU MISSED` or `YOU FOUND, CC MISSED` with an `ADOPTION TARGET`.
- Non-standard metric expansion: flag any case where one side expands `ARR`, "annual revenue run rate", annualized revenue, bookings, backlog, or similar issuer metrics beyond the source wording. The side preserving issuer wording is correct unless the source explicitly defines the stronger recurrence claim.
- Recurrence proof: if a summary implies contracted recurrence from a point-in-time run-rate, require source language such as "recurring", "contracted", "remaining performance obligation", or a comparable issuer-defined contract term. Otherwise recommend `run-rate (point-in-time), not proven recurring`.
- Customer-perspective asymmetry: if `customer_perspective_cc.md` is absent, still write `customer_perspective_codex_xcheck.md`, but label the file `ONE-SIDED CUSTOMER CHECK` near the top. State that this is not an independent CC/Codex customer cross-check under the current sequencing; CC's customer counterpart is Agent F in Phase 3. Put the limitation in `DISCREPANCIES` with `ADOPTION TARGET: raw/customer_perspective.md; steps/step4b_customer_perspective.md; steps/step3.5_consistency_check.md`.

A zero-discrepancy result is a warning. Re-read both summaries and the source before accepting it.

After writing the six cross-check files, tell the user:

```text
Step 1D done. Switch to CC and run /stock-research TICKER --step1e to integrate both summaries and run downstream analysis.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Cross-Step Consistency

Run cross-step consistency when the user invokes `$stock-research-codex TICKER --consistency`.

This step runs after CC's Phase 3 parallel agents and before CC's Phase 4.
Do not read valuation files in this phase. `STEPS/step9_valuation_cc.md`, `STEPS/step9_valuation_codex.md`, `STEPS/step9_valuation_reconciled.md`, and `STEPS/step9_valuation.md` do not exist yet or are out of phase for `--consistency`.

### Inputs

Read:

- `CC_INBOX` if present. CC writes or updates this before Codex handoffs when it has catches against Codex; at minimum, read the current file before `--consistency`.
- `STEPS/step3_business_model.md`
- `STEPS/step4_industry.md`
- `STEPS/step5_moat_current.md`
- `STEPS/step7_accounting.md`
- `STEPS/step8_management.md`
- `RAW/10k.md`
- `RAW/10q.md`
- `RAW/proxy.md`
- `RAW/competitors.md`
- `RAW/transcripts.md`
- `RAW/recent_8k.txt` if present
- `STEPS/step4b_customer_perspective.md` if present
- `RAW/customer_perspective.md` if present
- `RAW/cc_catches_against_codex.md` if present

### Output

Write `STEPS/step3.5_consistency_check.md` with these sections:

```text
=== CC CATCHES AGAINST CODEX: INTEGRATION RISK ===
```

If `CC_INBOX` exists, classify each CC catch as `Accepted`, `Rejected`, `Already fixed`, or `Not visible in current files`. State which current canonical or step file is still exposed to the error. If `CC_INBOX` does not exist, write that no CC catch inbox was present and continue.

```text
=== FACTUAL CONSISTENCY ===
```

Check whether agents agree on basic facts: segments, revenue split, key competitors, headcount, and geography. For each disagreement, state which agent is right per source and which agent must correct.

Also check claim-date drift: older filing facts, contract terms, management titles, board composition, or product/partnership claims that were true as of a 10-K/proxy date but overridden by later 10-Q, 8-K, transcript, press release, or amended agreement evidence. For each drift issue, state the old source date, the newer source date, and the current framing that downstream files must use.

```text
=== THESIS-LEVEL CONTRADICTIONS ===
```

Check:

- Does management's candor judgment contradict accounting's 4-tier verdict, opt-out flag, or Tier-III culture/governance evidence from `step7_accounting.md`?
- Does accounting's opt-out flag or pre-valuation economic earnings bridge contradict the business-model, moat, or management claims without explanation?
- Does moat's brand-advantage claim have backing in business model's customer-choice mechanism?
- Does industry's consolidating framing match competitor file market-share trends?

For each contradiction, state both claims verbatim, name the missing evidence, and recommend which claim must be revised.

```text
=== COMPOUND ERROR PATHS ===
```

Identify cascades where an early-agent claim was carried into a later agent and amplified without verification. Flag the originating inference.

### Handoff

If contradictions exist, tell the user:

```text
Cross-step consistency check found N issues. CC must read step3.5 and revise affected step files before Phase 4. Switch to CC and run /stock-research TICKER --step3.5e.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

If clean, tell the user:

```text
Cross-step consistency: clean. Switch to CC and run /stock-research TICKER --step3.5e to proceed to Phase 4.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Independent Valuation

Run independent valuation when the user invokes `$stock-research-codex TICKER --valuation`.

This step runs after CC's Phase 5A valuation and before CC's valuation reconciliation. Independence is the point: do not read `STEPS/step9_valuation_cc.md`, `STEPS/step9_valuation_reconciled.md`, `STEPS/step9_valuation.md`, or `CC_INBOX` during this phase. Read only the inputs listed in `agents/valuation_codex.md`.

### Agent Instructions

Load and follow `agents/valuation_codex.md`. That file contains the precondition guard, shared-reference paths, input set, valuation framework, exact required output sections, file hygiene rules, and handoff.

### Output

Write only:

- `STEPS/step9_valuation_codex.md`

Do not write or modify:

- `STEPS/step9_valuation.md`
- `STEPS/step9_valuation_reconciled.md`
- `STEPS/step9_valuation_cc.md`
- `CC_INBOX`

After writing `STEPS/step9_valuation_codex.md`, append or update `CODEX_BUGS` using the standard Codex run-log block. Include valuation-phase assumption risks, missing optional inputs, and self-corrections. Do not append Codex-side issues to CC's `bugs_encountered.md`.

### Handoff

After writing `STEPS/step9_valuation_codex.md`, tell the user:

```text
Codex independent valuation written to step9_valuation_codex.md. Switch to CC and run /stock-research TICKER --reconcile-valuation.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Optional Adversarial Counter-Attack

Run the optional adversarial counter-attack when the user invokes `$stock-research-codex TICKER --attack`.

This opt-in step runs after CC's Phase 6 counter-attack and before CC's Phase 7 final memo. Independence is the point.

Use this step when adversarial depth is worth the added friction: BUY/WATCHLIST candidates, close valuation calls, contested theses, low-reliability outputs, or high-confabulation-risk memos. For clear valuation PASS cases, do not imply that `--attack` is required; it remains available only if the user wants the extra adversarial pass.

### Inputs

Read:

- `CC_INBOX` if present. Use the current version only for blind-spot adjustment, not to rewrite CC's thesis. If CC updated the inbox after `--consistency`, incorporate only the new blind-spot implications.
- `RAW/10k.md`
- `RAW/10q.md`
- `RAW/proxy.md`
- `RAW/competitors.md`
- `RAW/insider.md`
- `RAW/transcripts.md`
- `RAW/customer_perspective.md` if present
- `RAW/cc_catches_against_codex.md` if present
- `STEPS/step3.5_consistency_check.md` if present
- `STEPS/step4b_customer_perspective.md` if present
- All relevant step files from `STEPS/step3_business_model.md` through `STEPS/step9_valuation.md`

Do not read `STEPS/step9_valuation_cc.md`, `STEPS/step9_valuation_codex.md`, or `STEPS/step9_valuation_reconciled.md` during `--attack`; CC preserves the reconciled valuation as `STEPS/step9_valuation.md`, and that compatibility alias is the attack input. Do not read `STEPS/step10_counter_attack.md` or any CC counter-attack file before writing this output.

`CC_INBOX` is allowed because it contains corrections to Codex's prior work, not CC's attack thesis. If present, use it to add a concise "Codex blind-spot adjustment" inside `CONTRADICTIONS FOUND` or the most relevant section. Example: aggregator overreliance should make customer-satisfaction claims lower confidence; a missed buyback table should make extraction caveats more skeptical.

### Attack Framework

Apply these eight attacks:

1. False-quality attack: could current economics be cyclical, temporary, or accounting-inflated?
2. False-moat attack: what appears durable but may not be? Cite a specific historical precedent of a similar moat failing in this or an adjacent industry.
3. False-management attack: where could incentives, empire-building, or capital allocation behavior disappoint?
4. False-valuation attack: which assumptions carry too much weight?
5. Narrative lock-in or confirmation-bias attack: where is the research most vulnerable to selected evidence supporting a pre-formed conclusion?
6. Contradiction scan across all step files.
7. Pre-mortem: five years from now, this investment has lost 50% or more permanently. Write three plausible scenarios with concrete mechanisms, warning signs visible today, and probability estimates. Name real comparable companies that suffered similar losses, with verifiable years and mechanisms. If no verified analog is found, write `no verified analog found`.
8. Base-rate or outside view: anchor base rates to external published distributions such as Aswath Damodaran data sets, Kenneth French data library, S&P/MSCI sector return tables, or peer-reviewed papers. Cite external sources with URLs and source dates. Do not generate historical analog lists from training data. If citing a precise percentile, drawdown rate, beat rate, or other computed base-rate number, download/recompute the source data into `RAW/base_rate_<name>.txt` and cite that local file. If the data cannot be downloaded or recomputed, label the source `anchor only, not computed` and do not use it for a precise numeric claim.

### Output

Write `STEPS/step10_codex_attack.md`. The first line must be this process statement:

```text
PROCESS: I did not read STEPS/step10_counter_attack.md or any CC counter-attack file before writing this.
```

Then include these sections:

```text
=== STRONGEST ANTI-THESIS ===
=== FALSE-POSITIVE RISK MAP ===
=== MOST FRAGILE ASSUMPTIONS ===
=== CONTRADICTIONS FOUND ===
=== PRE-MORTEM SCENARIOS ===
=== BASE RATE ANCHOR ===
=== FALSIFYING EVIDENCE LIST ===
```

After writing `STEPS/step10_codex_attack.md`, write `CODEX_REVIEW`.

Then tell the user:

```text
Codex adversarial counter-attack written to step10_codex_attack.md. Switch to CC and run /stock-research TICKER --step11e to integrate both attack passes into the final memo.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Optional Deep Customer Research

Run optional deep customer research only when the user invokes `$stock-research-codex TICKER --deep-customer`.

This is opt-in. Do not run it by default. It is useful for messy review markets, fragmented product categories, or tickers where customer evidence is strategically important. It does not replace the customer evidence canonical-use classifier in `customer_perspective_codex.md`.

Use manual ChatGPT.com Deep Research, not OpenAI API deep research. Do not require `OPENAI_API_KEY`. Do not call `o3-deep-research` or `o4-mini-deep-research` from Codex. The user will run Deep Research inside ChatGPT.com and paste the output back into Codex.

If no Deep Research output is present in the user's message and `RAW/customer_perspective_deep_research.md` does not already exist, write `RAW/customer_perspective_deep_research_prompt.md` and stop. The prompt must ask ChatGPT Deep Research to:

- Research customer, buyer, user, and expert evidence for `TICKER`.
- Prefer primary review platforms, app stores, regulator/complaint databases, expert category sources, and user forums.
- Verify exact counts, ratings, rankings, award placements, category positions, and "leader" claims on the primary source only.
- Classify customer claims by Authority, Primary/Derivative status, Access, and Specificity. Mark exact numeric claims from derivative or inaccessible sources as blocked from canonical use unless the primary source is verified.
- Return source links, source publication/update dates or access dates, and a table of claims requiring primary verification. Flag current-state customer or competitive claims older than the recency rule as `[STALE-RISK]`.

Then tell the user:

```text
Deep customer prompt written to raw/customer_perspective_deep_research_prompt.md. Run it in ChatGPT.com Deep Research and paste the resulting report back into Codex. Codex will validate it before any canonical use.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

If the user has pasted a Deep Research report in the current request, or if `RAW/customer_perspective_deep_research.md` already exists, validate and normalize it. Treat Deep Research as an outside-source input, not as canonical fact. Check all customer claims against the canonical-use classifier and block unsupported exact numbers, rankings, ratings, award placements, and category-position claims.

Write `RAW/customer_perspective_deep_research.md` with:

```text
=== SOURCE MAP ===
=== CUSTOMER SENTIMENT THEMES ===
=== PRIMARY-SOURCE NUMERIC CLAIMS ===
=== CLAIMS BLOCKED FROM CANONICAL USE ===
=== CUSTOMER EVIDENCE THAT SHOULD CHANGE THE THESIS ===
```

Exact counts, ratings, rankings, award placements, and leader claims remain blocked unless verified on the primary source.

Then tell the user:

```text
Deep customer report validated and normalized to raw/customer_perspective_deep_research.md. Return to the stock-research phase that requested this optional appendix.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

## Optional Deep Attack Research

Run optional deep attack research only when the user invokes `$stock-research-codex TICKER --deep-attack-research`.

This is opt-in. Do not run it by default. It is useful for outside-view base rates, historical analogs, market-cycle precedent, and adversarial failure modes. It must not replace filing verification or canonical financial numbers.

Use manual ChatGPT.com Deep Research, not OpenAI API deep research. Do not require `OPENAI_API_KEY`. Do not call `o3-deep-research` or `o4-mini-deep-research` from Codex. The user will run Deep Research inside ChatGPT.com and paste the output back into Codex.

If no Deep Research output is present in the user's message and `STEPS/step10_deep_research_appendix.md` does not already exist, write `STEPS/step10_deep_research_prompt.md` and stop. The prompt must ask ChatGPT Deep Research to:

- Find outside-view base rates, historical analogs, market-cycle precedents, and adversarial failure modes for `TICKER`.
- Name each analog's company, years, mechanism, similarity, dissimilarity, and source.
- Reject weak analogs explicitly rather than forcing a comparison.
- Use primary or high-quality secondary sources for historical mechanisms.
- Return source links, source dates, and a table of claims requiring primary verification. Do not treat older historical/base-rate sources as stale unless they are being used for a current-state claim.

Then tell the user:

```text
Deep attack prompt written to steps/step10_deep_research_prompt.md. Run it in ChatGPT.com Deep Research and paste the resulting report back into Codex. Codex will validate it before any canonical use.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```

If the user has pasted a Deep Research report in the current request, or if `STEPS/step10_deep_research_appendix.md` already exists, validate and normalize it. Treat Deep Research as an outside-source input, not as canonical fact. Do not use unverified analog mechanics or base-rate figures in the attack without source support.

Write `STEPS/step10_deep_research_appendix.md` with:

```text
=== OUTSIDE-VIEW BASE RATES ===
=== HISTORICAL ANALOGS ===
=== ANALOGS REJECTED ===
=== FAILURE MODES NOT IN THE FILINGS ===
=== CLAIMS REQUIRING PRIMARY VERIFICATION ===
```

Every analog must name the company, years, mechanism, and source. If no verified analog exists, write `no verified analog found`.

Then tell the user:

```text
Deep attack report validated and normalized to steps/step10_deep_research_appendix.md. Return to the stock-research phase that requested this optional appendix.

CLEAR CODEX WINDOW RECOMMENDED: this Codex phase is complete. Start the next Codex phase in a fresh Codex conversation unless you are debugging this exact phase.
```
