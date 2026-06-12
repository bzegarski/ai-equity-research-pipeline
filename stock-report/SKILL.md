---
name: stock-report
description: Build an HTML investment writeup from a completed stock-research folder. The writeup is shaped as an operating manual the reader's future self can audit in five years — narrative-driven, one number per paragraph, jargon defined inline. Reader is an individual long-term investor in the Buffett / Graham / Fisher / Munger / Marks tradition. Run after /stock-research has completed end-to-end.
---

# /stock-report — Investment presentation builder

## What this skill produces

A single self-contained HTML file at `{BASE}/{TICKER}_full_report.html`. Inline SVG charts. CSS-only hover-tooltip glossary. No external assets. Opens in any browser. Print → PDF works.

The reader is *the writer's own future self in 2031*, glancing at a headline and needing to decide whether to add to the position, hold, or get out — plus, secondarily, the spouse at dinner who asks in good faith "wait, what does this company actually do?" and deserves a sentence rather than a lecture.

A writeup that serves those two readers will outlast every quarterly earnings cycle, every analyst-day deck, every macro panic. A writeup that doesn't, won't.

## Architecture — writing pipeline, not rendering pipeline

Two layers, hard boundary:

| Python does                                                                | Claude does                                                |
| --------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Read `raw/gics.txt` (authoritative; never guesses)                         | Resolve GICS via WebFetch and write `raw/gics.txt` if missing |
| Validate inputs (memo + verification A strict-required, rest soft)         | Read `report_data.json` + sector primer + industry primer + glossary core |
| Parse XBRL series; extract memo header                                     | Write each of 11 section drafts into `_report_drafts/section_NN_<slug>.md` |
| Index `[FACT\|source\|confidence]` records into structured JSON             | Build per-company glossary `_report_drafts/glossary_company.json` |
| Render SVG charts; build HTML template; auto-inject glossary spans         | Iterate sections via `--rebuild-section N` until verification gates pass |
| Emit final HTML                                                            | (Never) compose prose                                       |

**Python never paraphrases or composes.** **Claude never edits chart specs or the template.**

---

## When to invoke

After `/stock-research TICKER` completes (research memo + verification A/B/C/D done). Not before — the skill aborts if the memo or verification A is missing.

Usage: `/stock-report TICKER` (with optional `--base PATH` to override the default research base directory).

---

## Invocation flow (orchestration)

### Step 0 — Ensure `raw/gics.txt` exists

The skill never guesses GICS classification. Before anything else, verify `{BASE}/raw/gics.txt` exists and contains at minimum a `Sector:` line. If it does, proceed to Step 1.

If the file is missing, **look up the GICS classification — never guess**:

1. **First try Wikipedia.** WebFetch `https://en.wikipedia.org/wiki/<Company_Name>` (use the company name as it appears on the 10-K cover page, with underscores for spaces). Most U.S. listed companies have a Wikipedia infobox with an "Industry" or "Sector" field that maps to or names the GICS sector. If the infobox names a free-text industry (e.g. "Payroll services"), translate it to the matching GICS-11 sector and the most-specific GICS industry / sub-industry you can confirm.

2. **If Wikipedia is unhelpful**, try the company's investor-relations page (most public-company IR pages list GICS classification on their fact sheets) or Yahoo Finance (the "Industry" line on the company quote page is GICS-formatted).

3. **If web lookup still fails**, use AskUserQuestion to ask the user: "What is the GICS sector for this company? (Optionally, the industry and sub-industry too.)" One short answer is enough.

4. **Confirm cross-source agreement** when feasible — if Wikipedia and Yahoo disagree, prefer Yahoo (its classification is GICS-licensed) and cross-check with one more source.

5. **Write the result** at `{BASE}/raw/gics.txt` in the format:
   ```
   Sector: <GICS sector>
   Industry: <GICS industry>
   Sub-Industry: <GICS sub-industry>
   ```
   Sector is required. Industry and Sub-Industry are recommended but optional.

The same "look up — don't guess" rule applies to **every** other fact the skill needs that isn't in the research files: regulatory dates, association URLs, trade-group statistics, historical-analog timing, sub-industry typical metrics. Use WebFetch on a reliable source (SEC EDGAR, BLS, EIA, FDA, trade-group fact sheets, Wikipedia for non-controversial structural facts). If a claim cannot be sourced, mark it `[GAP]` rather than invent it.

### Step 1 — Run prep

```
py scripts/build_report.py TICKER --prep
```

Reads `raw/gics.txt`; parses XBRL; extracts memo header; checks for sector primer at `assets/sectors/<Sector>_primer.md` and industry primer at `assets/industries/<Industry>_primer.md`; writes `_report_drafts/report_data.json`. Prints status of both primers (present / missing). Never blocks on missing primers.

### Step 2 — Load inputs

Read `_report_drafts/report_data.json` (deterministic data prep). Read sector primer at `assets/sectors/<Sector>_primer.md` if present; otherwise note its absence. Read industry primer at `assets/industries/<Industry>_primer.md` if present; otherwise note its absence. Read `assets/glossary_core.json` (cross-cutting finance terms). Read `assets/learn_more_finance.json` (verified URLs for Learn-more callouts).

If a primer is missing, **the build proceeds without it**. The per-section prompts below all degrade gracefully — they describe how to write each section *with* the primer, and how to write each section *without* it. Primer is enrichment, not a dependency.

### Step 3 — Draft sections 1–11

For each section in order, follow the per-section prompt below. Save the draft to `_report_drafts/section_NN_<slug>.md`. The 11 Claude-written sections are the operating-manual anatomy from Part III of the wisdom-tradition research document at `compass_artifact_wf-73c18398-84f7-402f-af5c-5ab84e12a418_text_markdown.md`, plus the recommendation at the bottom (kept by user request, repositioned as output rather than frame).

### Step 4 — Build per-company glossary

Scan the canonical research files for product names, acronyms, and company-specific terms used more than once. Write `_report_drafts/glossary_company.json` with one entry per term: `{term, match: [strings], definition: "..."}`. The auto-injection wraps these for hover tooltips throughout the report.

### Step 5 — Run the coverage audit (cross-section gate)

Before assembling, run the coverage-audit gate described in detail below ("The coverage audit"). For each canonical research file, identify load-bearing items, search the section drafts for them, decide whether each missing item is material or appropriately omitted, and add material items to the relevant section. Output: `_report_drafts/coverage_audit.md`. *Never skip this step* — sections drafted from a focused subset of inputs will routinely miss material that lives in the other research files, and the audit is the systematic catch.

### Step 6 — Run assemble

```
py scripts/build_report.py TICKER --assemble
```

Reads section drafts, runs glossary auto-injection, renders SVG charts, assembles the final HTML at `{BASE}/{TICKER}_full_report.html`.

### Step 7 — Run the remaining verification gates

After assembling, read the HTML cold (do not consult source files while reading). Run the five verification tests below. The coverage-audit gate ran in Step 5 above; the other four (five-year, dinner, Cunningham, internalization) run here. For any section that fails, refine the prompt, run `--rebuild-section N` to clear that section's draft, re-draft, re-assemble.

---

## Inputs

Strict-required (skill aborts):
- `{TICKER}_research_memo.md`
- `raw/verification_a.md`
- `raw/gics.txt` (Step 0 produces it if absent)

Soft-required (skill degrades gracefully; sections mark `[GAP]` for any specific claim that can't be supported):
- `raw/10k.md`, `raw/10q.md`, `raw/proxy.md`, `raw/competitors.md`, `raw/insider.md`, `raw/transcripts.md`, `raw/customer_perspective.md`, `raw/xbrl_summary.txt`
- `steps/step3_business_model.md` through `steps/step11_final_memo.md`
- `steps/verification_b.md`, `steps/verification_c.md`
- `bugs_encountered.md`, `bugs_encountered_codex.md`, `raw/cc_catches_against_codex.md`

Primer-optional (enrichment when present, ignored when not):
- `assets/sectors/<Sector>_primer.md`
- `assets/industries/<Industry>_primer.md`

---

# Universal writing rules

These apply to every section. They are constraints, not aspirations. A section that fails them gets rebuilt, not shipped.

## The contract with the future reader

The reader is the writer's own future self in 2031, glancing at a headline and needing to know what to do. Everything in the writeup is in service of that decision. The secondary reader is the spouse at dinner who asks "what does this company actually do" and deserves a sentence.

After one careful reading and zero re-reading, the reader can:
- Explain at dinner what the business sells, who buys, why customers stay, where the cash goes, and what would break it
- Recall numbers because the numbers are tied to stories
- Know what news would matter, so when the news arrives in five years they can react instead of panic

That is the standard.

## The hard rules

1. **Don't guess — look up.** Whenever a claim is needed that isn't in the research files (regulatory dates, association URLs, historical analog timing, structural facts about an industry), use WebFetch on a reliable source. If web lookup fails, AskUserQuestion. If both fail, mark `[GAP]`. Never invent.

2. **No CAPM. Anywhere.** The /stock-research skill states a 10% equity hurdle directly, the way Buffett / Marks / Klarman / Munger think about discount rates. The /stock-report skill must not introduce CAPM, beta-derived costs of equity, or any "academic finance" risk substitute. From the wisdom-tradition document: *"Risk is the probability of permanent capital loss, and you assess it by understanding what could permanently impair the business. A discount rate that comes out of CAPM is a number derived from a model that defines risk in a way that contradicts how Buffett, Marks, Klarman, and Munger actually think about risk."*

3. **No target prices in body** (only inside Section 11, the recommendation block). The body uses *expectations* — what the price implies must be true — not target prices.

4. **No sensitivity tables.** Replace with three named scenarios (base / optimistic / pessimistic) in prose, one or two sentences each. The reader can hold three scenarios; they cannot hold thirty.

5. **No SWOT. No pasted Porter five-forces.** Both produce inventories that masquerade as analysis. Frameworks are question generators, not deliverables.

6. **No generic macro / ESG framing** that could apply to any company. ESG matters where it changes unit economics or capital allocation; address it there in context, not as its own paragraph.

7. **No throat-clearing prose.** Cut "It is important to note that…", "While there can be no assurance…", "From the perspective of a long-term investor…", "In light of the foregoing…" Begin each section with the first thing the writer actually has to say.

8. **No "we recommend" rhetoric in body sections.** The recommendation lives in Section 11 only. Sections 1–10 describe; they don't prescribe.

## The numbers-as-story discipline

9. **Anchor every number to a unit of human-scale reality.** Per-customer, per-store, per-truck, per-pound, per-employee, per-policy, per-domain. *"See's sells 33 million pounds of chocolate a year at $20 per pound"* beats *"See's revenue was $660M with gross margin 49%."*

10. **One number per paragraph; ratios in service of a claim.** A paragraph that opens with seven figures buries the point. A paragraph that opens with the point and uses two numbers to ground it lands. Damodaran's *narrative and numbers* test: read the paragraph aloud — does the number arrive at a place where the reader is ready for it?

11. **Refuse to compute when the inputs don't warrant it.** Klarman in *Margin of Safety*: *"Any attempt to value businesses with precision will yield values that are precisely inaccurate."* If you cannot defend a discount rate, do not produce a DCF. If you cannot defend a multiple, do not produce a target price. Write `[GAP]` and move on.

## The voice and prose discipline

12. **Concrete subjects acting on concrete objects.** *"Microsoft sells Office to about 450 million office workers"* — subject (Microsoft), verb (sells), object (Office), beneficiary (workers). Not *"Productivity & Business Processes is the segment containing M365 Commercial."*

13. **One specific testable example per abstract claim.** Every time you write an abstract sentence, the next sentence is the example that, if false, would falsify the claim. *"Costco has a wide moat" → "Costco's 90% membership renewal rate has held within roughly two points across the 2008–2009 recession, the 2020 pandemic, and the 2022 inflation spike."*

14. **Define jargon inline on first use, in plain English.** ARR (annualized recurring revenue — the run-rate of subscription billings, multiplied by twelve). RPO (remaining performance obligations — revenue under signed contracts but not yet delivered or recognized). Cap rate (capitalization rate, the inverse of a P/E for property). The reader is a future self who has forgotten what the term means.

15. **Sentence rhythm matters.** Mix short impact sentences with longer unfolding ones. Read three Buffett letters or one Howard Marks memo aloud and you will hear it.

16. **The small earned surprise.** One observation per writeup that the reader did not expect, that on reflection is obviously true and powerfully clarifying. Not contrarian for its own sake — but the reward of careful reading is finding something the reader didn't already think. Place it where it lands hardest, typically at the end of the moat section or beginning of the risk section.

16a. **Khan-Academy clarity, not Khan-Academy infantilism.** Buffett / Munger / Marks / Fisher / Graham are the *posture* references; Sal Khan's tutorial videos are an additional *clarity* reference. The reader benefits when the writing teaches as it argues — defining each piece as it's introduced, building from concrete to abstract, never assuming the reader brought a textbook with them. **What this looks like:** when the reader meets a new term (cap rate, NRR, owner earnings, finance-vs-operating lease, RPO), the next clause defines it in one short, plain-English sentence; the sentence after that ties it back to a specific number from the company being analyzed. *"Cap rate — the inverse of a P/E for property; NOI divided by property value — sits at 5.8% for the typical Class A office in this portfolio, which means the building costs 17 years of net operating income to buy."* That structure (term → plain definition → company-specific number) is the Khan move.

**What this is NOT:** childish framing, fake-naïve setups, or pretend-classroom devices. *Never* write "imagine you have three cakes" or "let's say you're the owner of a lemonade stand" or "picture a pie chart of your investments." Those work for tenth-graders learning compound interest; they patronize an investor reading a stock writeup. The audience has passed CFA Level 1 — assume they know what a basis point is, what gross margin means, what a 10-K is. They might not know what a *fiduciary blackout period* is, or how *finance leases* differ from *operating leases* in cash flow, or what *RPO* means inside a SaaS contract — define those *exactly once*, plainly, in the sentence they're introduced in. The Khan target is: *a smart, motivated reader with no domain training in this specific niche can follow every paragraph without external lookup.* Not: *a child can follow this through pictures of cakes.* The two aims look superficially similar; in practice they produce very different prose.

## What stays out of body

17. **No analyst-working-file metadata in body.** No `[FACT|source|confidence]` chips on every paragraph, no `Step 3 —`, no `=== ... ===`, no `Sources:`, `Inputs:`, `Scope:`, `Date of analysis:`, `Prompt-injection:`. The drafts are reader-facing; the working notebook stays in `steps/`. (Subtle inline epistemic markers — see rule 23 below — are different from working-file metadata and are preserved.)

18. **No fabrication.** If a claim is not supported by the inputs and cannot be looked up, mark `[GAP: <what's missing>]` rather than fill in. Better an honest gap than a polished invention.

19. **No fabricated URLs.** All `→ Learn more` callouts point to entries in `assets/learn_more_finance.json`, the sector primer's `Where to learn more` block (when the sector primer is present), or URLs the writer has just verified live via WebFetch. If no relevant pointer exists, omit the callout — don't invent.

## Primer-conditional writing

20. **When the sector primer at `assets/sectors/<Sector>_primer.md` exists**, weave concepts from it into the relevant sections (especially Sections 4 and 5 — the industry and moat sections). Use the primer's worked examples and key metrics where they clarify the company.

21. **When the industry primer at `assets/industries/<Industry>_primer.md` exists**, weave its concepts into Sections 2, 4, 5, 7 as the industry-specific economics arise.

22. **When primers are missing**, write from research files alone. The prose still works; it just doesn't get the sector apprenticeship layer. Do not invent industry-typical metrics or moat shapes — use only what's in the research files plus what can be looked up via WebFetch.

## Epistemic-discipline markers (subtle inline pills)

23. **Mark load-bearing claims with one of three tiny pills.** Distinguishing what's *verifiable from a primary source* from what's *the writer's interpretation* from what *needs human verification* is load-bearing for a reader who, in 2031, has to decide whether to trust each claim. The discipline carries forward from the research-pipeline `[FACT|source|confidence]` convention, but the visual treatment is reader-facing rather than analyst-facing: small, muted, opacity 0.45 by default, full color on hover, with the source / reasoning / verify-target in the `title` attribute.

The three pills, used at the end of a load-bearing claim:

- `<span class="claim-tag claim-fact" title="<source>">F</span>` — the claim is verifiable from a primary source named in the title attribute (10-K Item 7; FY25 proxy; Q3 FY26 transcript; SEC EDGAR; Wikipedia for non-controversial structural facts; etc.).
- `<span class="claim-tag claim-interpretation" title="<reasoning basis>">I</span>` — the claim is the writer's interpretation, derived from facts but dependent on a chain of reasoning the reader could disagree with. Examples: "the moat is X because Y," probability assessments, comparisons with historical analogs.
- `<span class="claim-tag claim-humanverify" title="<what to verify>">?</span>` — the claim relies on a source that hasn't been fully primary-sourced and the precision matters. Examples: a single-source citation that wasn't independently corroborated; a number that propagated through aggregator sites; a forward-looking management statement.

**How to use them well**:

- *Be selective.* Mark load-bearing claims, not every sentence. Five to ten markers per section is the right density. A reader who sees a pill on every sentence stops reading the pills.
- *Place the pill at the end of the claim, not the start.* The reader has the claim before the marker; the marker lets them assess what kind of claim they just read.
- *Always include the `title=` attribute.* The hover-tooltip is what makes the marker useful. `<span class="claim-tag claim-fact" title="10-K Item 7 line 5471">F</span>` lets the reader hover and see the source.
- *Default to FACT for direct citations from filings, transcripts, government data, and Wikipedia (for non-controversial structural facts about industries and history).*
- *Default to INTERPRETATION for derivations (cash-flow walks computed by the writer; probability assessments; "the implication is that..."; "this means..."; comparisons across companies the writer made).*
- *Default to HUMAN-VERIFY when (a) only a single source supports a claim that matters and the source isn't a primary one, (b) a number propagated through an aggregator, or (c) a management statement hasn't been independently confirmed.*

The pills are visually subtle — they don't break reading flow at default opacity 0.45, and a reader scanning quickly will glide past them. A reader looking carefully will see them, hover for the source, and have an honest assessment of how solid each claim is. That asymmetry is the point.

**The pills are different from analyst-working-file metadata** (rule 17). Working-file metadata is an artifact of the research pipeline that doesn't belong in front of a reader. Epistemic-discipline pills are a reader-facing tool that preserves the *distinction* between fact, interpretation, and unverified claim while staying out of the prose's way.

## Footnoting style

Inline parenthetical only: `(10-K p.42)`, `(FY25 proxy)`, `(Q3 FY26 transcript)`, `(2007 Berkshire letter)`. Never markdown footnote syntax `[^1]`. The Python source-trail in Section 14 closes the loop on what files were actually read.

## Formatting

Each draft is markdown. Permitted:
- Headings: `##` for section, `###` for sub-sections inside a section.
- Lists, tables (used sparingly — narrative beats tables), blockquotes, code spans.
- Inline links: `[anchor text](URL)` — only verified URLs.
- Callouts via raw HTML when needed: `<aside class="key-numbers"><h4>Key numbers</h4><dl>...</dl></aside>`, `<div class="callout insight">...</div>`, `<div class="callout warning">...</div>`, `<div class="callout learn">...</div>`, `<details class="explainer"><summary>Concept (more)</summary>...</details>`.

Avoid:
- HTML beyond the listed callouts/key-numbers/explainer.
- Manually-wrapped `<span class="gloss">` — `inject_glossary.py` handles that automatically.
- `<svg>` — Python renders charts; Claude inserts only the caption text where the prompt asks.

## The five verification gates

After each draft (and after each rebuild), run these tests on that section's prose:

- **The five-year test.** Imagine the reader hasn't thought about this company in three or four years. A piece of news arrives. Do they know what to do? If not, the section's job isn't done.

- **The dinner test.** After re-reading the section, can the reader explain its content to a curious friend at dinner in two minutes — without consulting the document? If they can't, the prose isn't sticky enough.

- **The Cunningham test.** Does the section organize around a category an *owner* would care about, the way Lawrence Cunningham's *Essays of Warren Buffett* organizes Buffett's letters thematically (corporate governance, capital allocation, accounting, business quality)? Or does it organize around a sell-side category (sentiment, technical setup, earnings revisions)? The first is right; the second is wrong.

- **The internalization test.** A week after first read, can the reader recall the section's load-bearing fact and one anchor story without consulting the report? If not, the writing failed the *sticky* bar — likely because the numbers weren't anchored to stories.

- **The coverage-audit gate** (cross-section, run after all 11 drafts are written). The other four gates check whether each section is well-written. The coverage-audit gate checks whether the *body of work* — all 11 sections together — has surfaced the load-bearing material from the research files. Procedure described in detail below; do not skip.

A section that fails any of the first four gates gets re-prompted (tighten the prompt, then `--rebuild-section N`). The coverage-audit gate produces additions to specific sections rather than full re-prompts.

## The coverage audit (Step 6 of the orchestration)

Run **after** the 11 section drafts are written and **before** `--assemble`. Without this gate, sections drafted from a narrow slice of the research (a single step file, the memo's verdict paragraph) will routinely miss material that lives in the broader research output.

**Why this gate exists.** The /stock-research pipeline produces ~15 canonical files (memo + step1 through step11 + raw filings + verification A/B/C/D). Each per-section writing prompt above lists a focused subset of those as inputs. That focus is right for writing — a writer trying to read every file at every section will produce nothing. But it means each section's writer has *not seen* most of the research. The risk is that a load-bearing fact in `step4_industry.md` or `raw/recent_8k.txt` or the latest earnings transcript never finds a section to live in. The coverage-audit gate is the systematic check that catches those gaps before the report ships.

**The procedure.** For each canonical research file, identify 5–10 load-bearing items (specific numbers with sources; named events; regulatory dates; key analogs; structural claims). For each item, ask:

1. *Does this item appear in the drafts?* (textual search across `_report_drafts/section_*.md`)
2. *If not, is it material to an operating-manual reader?* — i.e., would the reader's view of *what to do at this price* change if they saw this item?
3. *If material, which section should host it?* Add it there with a one-paragraph addition; mark with the appropriate epistemic-discipline pill (F/I/?).
4. *If not material, document the omission.* Not every research finding needs to surface in the report; the audit is a check on intentional omission, not a check on completeness.

**The required source-file checklist** (verified-present-or-not before audit; gates the audit's coverage):

| File | Look for |
|---|---|
| `{TICKER}_research_memo.md` | Verdict, Key Insight, scorecard, the 12 Buffett-Munger sub-sections |
| `steps/step3_business_model.md` | Revenue streams, what they sell, who buys, $1-of-revenue walk |
| `steps/step4_industry.md` | Industry sizing, profit pools, structural changes underway, regulatory tailwinds and headwinds, embedded-payroll / disintermediation dynamics, sub-industry-specific tailwinds (e.g. SECURE Act for payroll/HCM) |
| `steps/step4b_customer_perspective.md` | Verified review evidence per product, competitive comparisons, company-claim-vs-independent-evidence table |
| `steps/step5_moat_current.md` | The candidate advantages with evidence for/against, replication test |
| `steps/step6_moat_durability.md` | The disruption vectors, named historical analogs, what would change the assessment |
| `steps/step7_accounting.md` | Forensic flags (red flags 1–N), CAMs, items requiring manual verification |
| `steps/step8_management.md` | Capital allocation 5-year table, comp design specifics, related-party items, recent material events |
| `steps/step9_valuation.md` | Valuation inputs, base/stress range, what current price requires |
| `steps/step10_counter_attack.md` | The named attacks, base-rate citations, contradictions, falsifying evidence list |
| `steps/step10_codex_attack.md` (if present) | Codex's framing, agreement/disagreement with CC catches |
| `raw/recent_8k.txt` | Material 8-K events in the last 12 months — executive departures, board changes, credit-facility amendments, dividend declarations, special items |
| `raw/transcripts.md` | The most recent earnings call's reported figures and qualitative themes (synergy targets, AI commentary, retention claims) |
| `raw/proxy.md` | Comp design specifics, related-party transactions in full, board composition |
| `raw/insider.md` | Form 4 transactions in the trailing 6–12 months — buys, sells, 10b5-1 plan adoptions or terminations |
| `raw/cc_catches_against_codex.md` (if present) | Cross-model audit catches that should be reflected somewhere in the report |
| `bugs_encountered.md` (if present) | Data-extraction warnings worth disclosing in the reliability section |

**For each file, the audit produces a paragraph** in `_report_drafts/coverage_audit.md` of the form:

```
## step4_industry.md (audited 2026-05-06)

Load-bearing items reviewed:
- US payroll-services market $82B; HR-payroll software $16B; PEO industry $136-156B gross. → Added to Section 5 (industry). Material.
- SECURE Act 2.0 auto-enrollment mandate effective Jan 1, 2025. → Added to Section 5 (industry); referenced as positive tripwire in Section 11. Material.
- Embedded payroll: Gusto Embedded 1M+ SMBs, US Bank 1.4M-customer launch. → Added to Section 5 (industry). Material.
- Industry bifurcation framing (bottom fragmenting / middle consolidating / upper-mid concentrated). → Added to Section 5. Material.
- Rippling/Deel lawsuit, March 2025. → Omitted. Not material to operating-manual reader (no measurable impact on PAYX trajectory).
- DOL independent-contractor classification whiplash. → Omitted. Net-neutral impact per Step 4 own assessment.

Omitted items documented. No further additions required from this file.
```

**Verification of the audit itself.** A clean coverage-audit produces:
- One paragraph per audited file in `coverage_audit.md`.
- For each material item flagged, a corresponding addition (with epistemic pill) in the relevant section draft.
- For each omitted item, a documented decision *why* the omission is appropriate.

The audit is required before `--assemble`. A report that ships without coverage_audit.md is incomplete.

**Common categories of items the audit catches** (across many tickers' worth of /stock-research output):

- **Industry sizing and structural-trend material** in step4_industry — frequently buried in source file because it's *industry-level*, not *company-level*; frequently missing from the company-level prose.
- **Regulatory tailwinds and headwinds** that affect the company over a multi-year horizon (SECURE Act, IRA drug pricing, ESG mandates by state, SEC rule changes) — these belong in Section 5 (industry) or Section 9 (premortem).
- **Recent earnings-call proof points** from `raw/transcripts.md` — adjusted-margin highs, organic-growth splits between halves, capital-return run-rates. These belong in Section 8 (financial history) or Section 9 (premortem).
- **Material 8-K events** in the trailing 12 months — credit-facility amendments, executive departures, board changes — that color the management section's verdict.
- **Sub-products or product extensions** named in step3 / step4b but missed in Section 1 or Section 3 (e.g. Paychex Perks).
- **Open questions / undisclosed metrics** flagged in step4 unknowns or step6 — these belong as tripwires in Section 11.
- **Codex catches** in cross-model audit files that should be acknowledged in the reliability disclosure.

The audit is the discipline that produces durable coverage. Run it on every report.

---

# Per-section writing prompts

For each section, the prompt has five parts:
- **Reader's question** — the section must answer it.
- **Inputs** — read only these. Scope is a constraint.
- **Required content** — ordered components with word-count guidance.
- **Word band** — for the section as a whole.
- **Section-specific notes** — chart slots, callouts, recurring concepts, primer use.

Universal rules above apply on top of every prompt.

---

## Section 1 — The lede

**Reader's question:** "What does this company sell, who buys it, and what's the one anchor number?"

**Inputs:**
- `{TICKER}_research_memo.md` (Section 4 — THE BUSINESS — has the dense version)
- `raw/10k.md` Item 1 (the company's own description)

**Required content:**

One paragraph, roughly five sentences, structured tightly:
1. What the company sells, in objects a reader can picture (not segment names — *Office, Excel, Teams* not *Productivity & Business Processes*).
2. Who buys, characterized concretely (a 50-person business; a CFO of a Fortune 500; a household earning $100K+ shopping for groceries — pick one).
3. The unit of sale (per seat, per pound, per policy, per warehouse trip) and rough customer-base size.
4. How the customer pays and how soon the company sees the cash (subscription, by-use, royalty, one-time; cash up-front or on terms).
5. The anchor number — the single most useful piece of information about the business's scale or shape, stated concretely.

**Word band:** 60–100 words. One paragraph. No more.

**Section-specific notes:**
- Worked example from the operating-manual document, See's voice: *"See's Candies sells boxed chocolates — about 33 million pounds a year — almost entirely on the West Coast, mostly to people buying gifts in the four weeks before Christmas, Easter, Valentine's Day, and Mother's Day. Customers pay roughly $20 a pound at the register, in cash or by card, and walk out with the chocolate the same day; there is no shipping operation worth mentioning. The business needs about $40 million of capital to run, throws off most of its profits as cash, and has done so for fifty years (Berkshire 2007 letter)."*
- Worked example for PAYX-shape company: *"Paychex sells payroll services to about 800,000 small US businesses. About 50 employees per client on average; the bookkeeper and the CPA both have logins. Customers pay roughly $100–$300 per month per location for the bundle, and Paychex collects payroll-tax dollars from the employer days before remitting to the IRS — the float on those dollars throws off about $200M a year of interest income at peak rates. Service revenue last year was $5.4 billion."*
- **NOT** in the lede: a sector descriptor ("a leading consumer discretionary issuer"), a market-cap pleasantry ("a $35B mid-cap"), an analyst-flavored verb ("we initiate coverage with"), a verdict, a price target. If a sentence could appear in any company's lede, it doesn't belong in this one.

---

## Section 2 — Unit economics

**Reader's question:** "Show me the dollar — how does this business actually make a dollar?"

**Inputs:**
- `raw/10k.md` (Item 1; Item 7 MD&A; Note A on cost structure)
- `steps/step3_business_model.md`
- `_report_drafts/report_data.json` (chart specs and XBRL series)
- Industry primer at `assets/industries/<Industry>_primer.md` if present (for sub-industry-specific unit-economics framings)

**Required content:**

1. **Pick the smallest reproducible economic unit.** Per-warehouse, per-policyholder, per-seat, per-pound, per-truck, per-domain. The unit is something a human being can hold in their head. Open with naming it.

2. **Walk the unit from revenue to cash.** What does the customer pay per unit? What does it cost the company per unit at each stage of the income statement? Where does the cash end up — maintenance capex, growth reinvestment, dividends and buybacks?

3. **Connect each number to where the cash goes.** Use Buffett's owner-earnings framing (NI + D&A − maintenance capex − working-capital changes). The point isn't to compute the number to the dollar; it's to track each dollar of profit to one of three places.

**Three rules govern this section:**

- *One number per paragraph.* Readers cannot retain three numbers in a paragraph; they will retain one number tied to a story.
- *Make the number concrete by naming the unit.* "On an average $130 basket, Costco keeps about $4 of operating profit and another $3 of membership fee" beats "operating margins of 8%."
- *Connect each number to where the cash actually goes.* Maintenance capex / growth reinvestment / out the door to owners.

**Word band:** 400–600 words.

**Section-specific notes:**
- Worked example from the operating-manual document, FlightSafety voice: *"FlightSafety, which Berkshire bought in 1996, earned $111 million pre-tax that year and held about $570 million of fixed assets; by 2007 pre-tax earnings had grown to $270 million but capital expenditures of $1.6 billion (mostly for $12-million-each flight simulators) had outpaced depreciation by hundreds of millions — the business grew, but every dollar of growth had to be paid for in advance with another simulator (Berkshire 2007 letter)."* Notice the work that one sentence does: business model (sell training, but you must buy simulators first), capital intensity (fixed assets nearly six times pre-tax earnings), and the inescapable trade-off (growth requires reinvestment).
- The chart pack with `caption_slot_section: 2` (revenue donut + $1-of-revenue horizontal bar where available from `report_data.json`) is rendered into this section automatically. Claude writes one-sentence caption text per chart inside the draft using the `<figcaption>` HTML — the caption is the takeaway, not a description.
- A `<aside class="key-numbers">` callout with 4–5 bullets at the end of the section. Each bullet: one fact + one number + one short reason it matters. *"Free cash flow $1.7B (FY25), flat for two years despite +35% revenue — capex is eating the rent."*
- If the industry primer is present: weave its sub-industry-specific framings (e.g. for Professional Services: float economics on payroll-tax dollars; for Banks: net interest margin on deposits). If absent: write from research files alone.

---

## Section 3 — The product, judged by its users

**Reader's question:** "Are the products actually good? What do real users say?"

**Inputs:**
- `raw/10k.md` Item 1 (the product portfolio as the company describes it)
- `steps/step3_business_model.md` (the products and how they fit together)
- `steps/step4b_customer_perspective.md` (verified review evidence — G2, Capterra, App Store, Trustpilot, BBB; competitive positioning by product feature)
- `raw/customer_perspective.md`
- `raw/competitors.md` (for product-level comparisons with peers)

**Required content:**

This section answers a question the customer-and-demand section (Section 4) takes for granted: *are these products actually good?* It is structurally distinct from Section 4. Section 4 asks who buys and why they stay (Fisher's territory — demand-side moat). This section asks whether the products that drive that retention are genuinely good or merely sticky — a distinction the wisdom-tradition writers care about (Fisher's 15 points spend significant attention on product quality and R&D productivity; Buffett's See's Candies discussion repeatedly grounds the moat in the *quality* of the product, not just the brand).

Three parts:

1. **The product portfolio.** Name each of the company's actual products in plain English — what each is, who uses it, where it sits on the price-and-feature curve. Don't list segments; list products. For a SaaS company, name the platforms the customer logs into. For a pharma company, name the drugs. For a hotel REIT, name the brand mix. For Paychex specifically: Paychex Flex (the SMB platform), Paycor (the upmarket platform acquired April 2025), SurePayroll (the self-service micro-business product), the PEO co-employment service, the 401(k) recordkeeper, the brokered insurance line — six distinct products, each with different economics and a different customer.

2. **The verified review evidence per product, with platform-source caveats.** Not "customers love the product" — *G2 4.1/5 from 1,637 verified reviews. Capterra 4.2/5 from 1,757 reviews. Apple App Store 4.8/5 from 570,000 ratings. Trustpilot 1.1–1.5/5 from 679 unprompted reviews. BBB 1.03/5 from 327 reviews and 541 complaints.* Each platform selects a different population (G2/Capterra select for active paying users; Trustpilot/BBB select for unhappy departures); both are real signal about different things. State the platform reliability caveats explicitly so the reader knows what they're looking at.

3. **Product strengths, product failure modes, and the trajectory.** Where the product works (the things that get 4.5+ ratings consistently). Where it breaks (the recurring complaint shape — for Paychex, "wholly incapable of correcting its own errors" on tax-correction errors, W-2 misfilings, billing surprises). What's improving or degrading right now (Paycor's June 2025 broken reports and August 2025 PTO data loss; the February 2026 customer-service-hours cut). Compare each major product to its closest competitor on at least one dimension where the comparison clarifies the company's position — *Paychex Flex sits between Gusto (better UX for under-100-employee firms) and ADP RUN (better 24/7 specialist support) on the price/feature curve*.

**Word band:** 600–900 words.

**Section-specific notes:**
- Apply the rule-23 epistemic-discipline markers liberally here. Most number-with-source claims (G2 4.1/5 from 1,637) are FACT. Aggregate ratings cited by aggregator sites without primary verification are HUMAN-VERIFY. The bimodal-trajectory framing ("works on routine, breaks on service escalation") is INTERPRETATION.
- A `<aside class="key-numbers">` callout at the end with the headline ratings per product and the directional trajectory.
- The *aggregator-sourced numbers caveat* applies in full: if a number originated from a third-party aggregator (Comparisun, Software Advice rankings) and wasn't independently verified on the platform, mark it `?` for HUMAN-VERIFY rather than `F`.
- Buffett on See's Candies (1972 acquisition; 1983 letter; 2007 letter) is the wisdom-tradition reference for grounding moat in product quality. The line *"most lovers of chocolate prefer it to candy costing two or three times as much"* (1983 letter) is the canonical demonstration of how to evidence product quality concretely. The Paychex equivalent — if it existed — would be a comparable claim about product quality vs Gusto / ADP, supported by independent review evidence.

---

## Section 4 — The customer and demand

**Reader's question:** "Who specifically buys this, and why do they stay?"

**Inputs:**
- `raw/10k.md` Item 1 (customers, concentration, distribution channels)
- `steps/step3_business_model.md` (Who buys section)
- `steps/step4b_customer_perspective.md` (where it informs *why customers stay* rather than product quality — product-quality evidence lives in Section 3)
- `raw/customer_perspective.md`

**Required content:**

This is Fisher's territory — the section where someone who has *talked to customers, ex-employees, and competitors* writes differently from someone who only read the 10-K. Two parts.

1. **Who buys, concretely.** Not "consumers" or "small businesses" — a 50-person professional-services firm in suburban Cincinnati that's on its third generation of owner; a 40-something dual-income household earning $100–$200K driving 20 minutes to a warehouse and leaving with rotisserie chicken plus one impulse purchase; a hospital surgeon who has trained on this device for 200 procedures and resists relearning. Where filings disclose specific customers (Microsoft's Accenture 740K Copilot seats; Paychex's CPA-channel referrals at >50% of new clients), name them.

2. **Why customers stay.** This is the moat question dressed in customer clothing — and it's harder to fake from the demand side than from the marketing side. Walk through the actual mechanism that keeps the customer:
   - The cost they would bear to switch (in dollars, hours, and risk)
   - The bundle effect (would they have to replace four vendors, not one?)
   - The trust transfer that's already happened (who set them up; who they've called when something broke)
   - The verified review evidence (what real customers say in unprompted reviews, with the source-platform reliability caveats — G2 selects for current users; BBB selects for the unhappy 18%)

**Word band:** 500–700 words.

**Section-specific notes:**
- Worked example from the operating-manual document, GEICO voice: *"About one in three GEICO policyholders was referred by a friend or family member, which means GEICO acquires roughly half its new business at near-zero marginal cost — the math behind the gecko ads is that the ads are a tax on the business, not its engine, and the engine is the existing customer who is reasonably happy and tells someone else (Berkshire 1996 letter)."*
- Honest caveat on review-source reliability is required, not optional. G2/Capterra select for current paying users; Trustpilot/BBB select for unhappy departures. Both are real signals about different populations.
- If the industry primer is present and contains a "common pitfalls newcomers misread" section, draw on it where it clarifies. For example: in the Professional Services primer, the canonical lesson on distinguishing real switching costs from marketing claims.

---

## Section 5 — The industry, through this company

**Reader's question:** "What kind of business is this, and what's the one number that defines its economics?"

**Inputs:**
- `assets/sectors/<Sector>_primer.md` if present
- `assets/industries/<Industry>_primer.md` if present
- `raw/competitors.md`
- `steps/step4_industry.md`

**Required content:**

The mistake to avoid: a pasted Porter five-forces, a market-share pie chart, a five-page macro chapter. *Industry as apprenticeship.*

Three moves:

1. **Describe the industry as the company sees it.** Not what the GICS classification says it is. What is the company's actual competitive set? What is the dominant economic model in the company's specific corner of the industry (subscription vs metered vs license-and-services; toll-road vs price-taker; pooled-risk vs spread)?

2. **Identify the one number that defines this industry's economics**, anchor it to the company. *Load factor* for airlines (and the related fact that empty seats spoil more completely than unsold widgets). *Gross retention* for software (because every churned dollar is a dollar of CAC permanently wasted). *Per-capita consumption* for boxed chocolates (which barely grows, which is why pricing not volume is the engine). *Net interest margin* for banks. *Cap rate* for REITs. *Reserve replacement* for upstream oil & gas. State the number; explain what it controls.

3. **Use competitors as the sector's variation, introduced in context.** Don't list peers in their own section. Introduce each one at the moment it clarifies a point about the company. *Progressive enters the GEICO writeup at the loss-cost paragraph; Walmart enters the Costco writeup at the SKU-velocity paragraph.* By the end the reader has met four competitors, each in the place where they illuminate something — and has therefore mapped the sector.

**Word band:** 400–600 words.

**Section-specific notes:**
- This section is **shorter** than it would be if it were a standalone industry chapter, because much of the industry teaching happens *through* the company in Sections 2, 5, 7. This section consolidates the frame.
- If both sector primer and industry primer are missing: write from `raw/competitors.md` and `steps/step4_industry.md` alone. Use the `→ Learn more` callout to point to a sector trade-association primer if `assets/learn_more_finance.json` covers it. If not, mark a `[GAP: industry primer not yet authored — see SKILL.md for the prompt to run on Claude.ai]` so the gap is visible.
- A `→ Learn more` callout at the end pointing to: the sector primer's "Where to learn more" block (if primer present), or to a relevant trade-association URL from `assets/learn_more_finance.json`. Don't invent URLs.

---

## Section 6 — Moat

**Reader's question:** "Which of Pat Dorsey's four moat sources applies, and what would erode it?"

**Inputs:**
- `steps/step5_moat_current.md`
- `steps/step6_moat_durability.md`
- `assets/sectors/<Sector>_primer.md` (for which moat shapes are typical in the sector — if present)

**Required content:**

Pat Dorsey's *The Little Book That Builds Wealth* gives the cleanest taxonomy of durable competitive advantages: **intangible assets** (brand, patents, regulatory licenses), **switching costs**, **network effects**, **cost advantages**. Dorsey's contribution was to make the categories *exhaustive enough that you cannot wave at "moat" in the abstract* — you have to say which kind, and then defend the choice.

Four moves:

1. **The moat statement in one sentence.** Not "this company has a moat" but: *"Microsoft's moat is identity infrastructure: removing Active Directory from a Fortune 500 means rebuilding every login system the company uses."* ~25 words.

2. **Pick the kind, defend the choice.** State which of Dorsey's four sources applies and why. Brand among whom, in what geography, at what price point? Switching costs measured in what (dollars / hours / risk)? Network effects on what network, and what coordinates? Cost advantage on which cost line (distribution / scale / labor / regulatory)?

3. **Concrete mechanism per advantage.** Each named advantage, ~80–120 words: name the mechanism, give a worked example, test it with a counter-attack ("if a competitor offered identical functionality at half the price, would the customer switch? walk through the actual cost").

4. **Durability — what would erode it.** Buffett's 2007 letter warning is load-bearing: *"a moat that must be continuously rebuilt is eventually no moat at all."* For each named advantage, name the specific erosion vector and the leading indicator that would tell the writer it's happening. Mark each erosion risk with a probability adjective (low / medium / high).

**Word band:** 600–900 words.

**Section-specific notes:**
- A small-earned-surprise moment is most likely to land at the end of this section or the beginning of Section 8. One observation that reframes the reader's mental model — Buffett's *"paying twice for the same dollar of moat"* on Microsoft, or *"the brand moat travels east of the Rockies and stops"* on See's. One per writeup.
- A `→ Learn more` callout pointing to Pat Dorsey's *The Little Book That Builds Wealth* (book name; no URL needed) if this is the section that introduces moat taxonomy.
- If the sector primer is missing: cite specific historical analogs from the durability working file (Step 6) where they're verifiable. Do not invent analogs.

---

## Section 7 — Management and capital allocation

**Reader's question:** "Where has each retained dollar gone? Are the incentives aligned with mine? Has management told the truth in writing?"

**Inputs:**
- `steps/step8_management.md`
- `raw/proxy.md`
- `raw/insider.md`
- Berkshire shareholder letters where they discuss capital allocation in similar businesses (cite specifically; verifiable via web)

**Required content:**

Three questions, and only three, drive this section. Each gets meaningful attention; nothing else does.

1. **Where has each retained dollar gone over the last ten years?** Track the cash. Reinvested into the existing business (capex, working capital), acquisitions, dividends, buybacks, debt paydown, sitting in cash. For each bucket, what return has the company earned? Mauboussin's discipline applies: *"incremental returns on capital should be prioritized over growth."* A growing company that reinvests at 8% when it could buy back stock at an earnings yield of 12% is destroying value, however excited the press releases sound.

2. **Are the incentives aligned with owners?** Read the proxy carefully — quote it. If half the CEO's compensation is tied to revenue growth and zero is tied to ROIC, expect revenue growth and price-insensitive acquisitions. If management owns shares it bought with its own money rather than shares it received in grants, the calculus is different. Insider sales over five years exceeding insider buys 20:1 is data, not noise.

3. **Has management told the truth in writing?** Read the last ten letters or transcripts. When the business missed, did management explain why concretely, or did they blame "macro headwinds"? Did they revisit their previous claims and grade them? Bloomstran's annual Semper Augustus letters are exemplary — a writer who returns to old claims and either ratifies or amends them in writing where it can be checked.

**Word band:** 600–800 words.

**Section-specific notes:**
- Buffett's 1987 letter on Mr. Market and capital allocation, and the 1996 letter on circle of competence, are the canonical wisdom-tradition references. Cite by year.
- If a proxy red flag exists (related-party transactions, founder-CEO with low ownership, comp metric that incentivizes the wrong behavior), name it concretely with the dollar figure and the source.
- This section gets the *honesty about uncertainty without throat-clearing* treatment. *"I do not know whether the next CEO will allocate capital with the same discipline as the current one. The current one has allocated capital with above-average discipline since 2014, by the test of incremental ROIC; that is the evidence I have. The risk that this changes is one of the three things I would track most closely after a CEO transition."* That paragraph is honest, useful, and lacks every form of hedging language except the actual hedge.

---

## Section 8 — Financial history

**Reader's question:** "What does the cash conversion / ROIIC / reinvestment runway / balance-sheet posture across cycles actually tell me?"

**Inputs:**
- `_report_drafts/report_data.json` (chart specs and XBRL series — 5-year revenue, op margin, OCF, capex, shares, debt)
- `raw/xbrl_summary.txt`
- `steps/step9_valuation.md` (Stage 1 inputs; growth and margin assumptions)
- `steps/step7_accounting.md` (any accounting flags worth surfacing here)

**Required content:**

The mistake here is the seven-year financial summary table. Tables compress information into rows the eye scans without reading. Replace the table with a narrative that walks the reader through the same data with attention to inflection points.

Four threads to weave (the operating-manual document calls these out):

1. **Cash conversion.** Of every dollar of accounting profit, how much arrived as cash? When was the gap largest, and why? If GAAP earnings have run consistently above free cash flow for five years, what working-capital or capitalized-cost dynamic is driving the gap?

2. **Return on incremental invested capital (ROIIC).** John Huber at Saber Capital's recurring obsession. Total earnings growth divided by total reinvested capital across a period is a crude but sharp estimate of how productive the next dollar of retained earnings is likely to be. *A company earning 30% on existing capital but only 10% on incremental capital is a company in slow decay; a company earning 15% on both is a company you can sleep through.*

3. **Reinvestment runway.** How many more dollars can this business productively absorb at returns above its cost of capital? *See's, by Buffett's own admission, was a tiny runway — between 1972 and 2007 the business absorbed only $32 million of incremental capital despite generating $1.35 billion of pre-tax cash, because the boxed-chocolate market in California simply could not soak up more (Berkshire 2007 letter).* That's a feature when paired with a parent that can deploy the cash elsewhere; it's a flaw if the cash gets reinvested in the wrong adjacencies.

4. **Balance-sheet posture across cycles.** Did the company have to sell equity at the bottom in 2008–09? Did it raise rescue financing in March–April 2020? Did it suspend its buyback during the inflation spike of 2022? *A company's balance-sheet behavior across cycles tells the reader how its management thinks about risk in a way no policy statement ever will.*

**Word band:** 600–900 words.

**Section-specific notes:**
- The chart pack with `caption_slot_section: 7` (5-year revenue line, op margin, OCF, FCF-vs-capex paired bar, shares, debt) renders into this section automatically. Claude writes the takeaway caption per chart inline as `<figcaption>` text. Caption is the takeaway, not the description: *"Revenue grew 33% over three years, but the FCF line went flat — the gap is where the AI-infrastructure bet sits."*
- One key-metrics table is permitted at the end of this section if it earns its keep — 5–7 rows, each row tying back to a thread already developed in the prose. Tables should never substitute for narrative; they consolidate it.
- If the accounting working file (Step 7) flagged a load-bearing item, surface it here briefly with the dollar figure. The full accounting commentary lives in this section now (the prior 12-section design had a separate Section 9 — that's folded in here).

---

## Section 9 — Pre-mortem

**Reader's question:** "If this position dies in five years, what does the news headline say?"

**Inputs:**
- `steps/step10_counter_attack.md` (CC adversarial attack)
- `steps/step10_codex_attack.md` (Codex adversarial attack, if available)

**Required content:**

Munger's *invert, always invert*. Write the section that imagines the position has died in five years, and tell the story of how. Then ask whether the story is plausible.

Three rules govern this section:

1. **Every risk must be specific enough to be testable.** *"Regulatory risk"* is not a risk; it is a category. *"The CFPB rescinds the 2017 prepaid-card rule, forcing the company to re-document 30% of its account base within twelve months"* is a risk. The first you can ignore; the second has a probability and a magnitude.

2. **Separate the risks that would impair the business from the risks that would impair the price.** Buffett and Munger insist on this distinction because it's the entire content of Mr. Market: a stock can fall 40% in a year without the business value changing, and a stock can rise 40% while the business is quietly rotting. The 1987 Berkshire letter on Mr. Market and Marks's *On the Couch* (January 14, 2016) and *What Does the Market Know?* (January 19, 2016) are the canonical references.

3. **Quantify the things you can quantify, and refuse to quantify the things you cannot.** Klarman: *"any attempt to attach a probability to 'the risk that AI commoditizes the company's product' will be precisely inaccurate."* State the risk, describe the mechanism, name the leading indicators, stop. False precision is a form of dishonesty.

Three pre-mortem scenarios — 200–250 words each. Each: a one-sentence headline ("MSFT loses 50% as AI bubble pops and capex goes nowhere"); the chain (what happens, in what order, on what timeline); a probability adjective (plausible / unlikely / tail risk); a named verifiable historical analog if one exists, marked `[GAP]` if none.

**Word band:** 700–1000 words.

**Section-specific notes:**
- Anti-confabulation discipline is most load-bearing here. Cite analogs only when the writer has verified they exist (Salesforce vs Siebel 1999–2005; Costco-Amex 2016; H&R Block vs TurboTax 2003–2025; Insperity 2024–25). If a scenario has no verifiable analog, omit and mark `[GAP: no verifiable analog cited]`.
- A `→ Learn more` callout for Howard Marks's Oaktree memos at `oaktreecapital.com/insights/memos`, particularly the 2007–2009 cycle memos as the model of how to think about pre-mortem scenarios.

---

## Section 10 — Valuation as expectations

**Reader's question:** "What does the price imply must be true, and is that more or less likely than my inside view?"

**Inputs:**
- `steps/step9_valuation.md` (DCF inputs and outputs)
- `steps/verification_b.md` (the fresh-context recheck of valuation arithmetic)
- `_report_drafts/report_data.json` → `memo` block (intrinsic estimate)

**Required content:**

This is the section most often ruined. The sell-side error is to compute a target price by multiplying next-year EPS by an assumed P/E and pretend the result is a number. The academic error is to discount cash flows at a CAPM-derived cost of equity, with beta drawn from five years of historical price volatility, and pretend that result is a number. Both are in Klarman's gunsights in *Margin of Safety* Chapter 8, and both are the targets of Marks's repeated insistence that *"volatility is the academic's choice for defining and measuring risk … because volatility is quantifiable and thus usable in the calculations and models of modern finance theory"* — and that this convenience is the entire reason it is wrong.

The right move is Mauboussin and Rappaport's, in *Expectations Investing* (revised 2021): start from the price, work backward to what the price implies must be true, and judge whether the implied future is more or less likely than the writer's independent assessment of the future.

Three short parts.

1. **What does the price imply?** Translate the current price into expected sales growth, expected operating margin, expected investment rate, and the period over which excess returns persist (Mauboussin's "competitive advantage period"). The numbers will be approximate; that's fine. A reverse DCF is a useful exercise in producing the *implied* future, not the *forecast* future.

2. **How does that compare to base rates and to the inside view of the company?** Mauboussin's *Base Rate Book* provides the outside-view discipline: most companies do not sustain 20% sales growth for ten years, because most companies in the historical sample did not. That base rate matters even when, especially when, the inside view says "this one is different."

3. **What is the margin of safety?** Graham's central concept, restated by Klarman: the writer doesn't need to be precise; the writer needs to be sufficiently wrong-able. If the independent assessment of the implied future is materially better than what the price requires, and the gap can be described in plain English, there's a margin of safety. If the gap can't be described in plain English, there isn't.

**Word band:** 700–1000 words.

**Section-specific notes:**

- **NOT in this section:** a target price; a sensitivity table; a CAPM cost of equity; a beta; a comp table of peers ranked by EV/EBITDA; the words "we recommend." None of those are useful to an owner in five years.

- **Use a stated equity hurdle rate** in plain English. *"For an SMB-cyclical, AI-disruption-exposed, post-$4B-M&A operator, I require a 10% return; below that, I have other places to deploy capital."* That's the right shape. Not "WACC of 8.5% derived from a CAPM with beta 1.05."

- **Replace the sensitivity table with three named scenarios in prose.** *Base case ($X per share at 5.5% growth, 10% discount, 3% terminal). Optimistic ($Y at 7% growth). Pessimistic ($Z at 3% growth, margin compression).* One paragraph each. The reader can hold three scenarios; they cannot hold thirty.

- A `→ Learn more` callout for Aswath Damodaran's free *Investment Valuation* lectures (search "Damodaran reverse DCF" on YouTube — 12-minute walkthrough).

- Worked example, Costco voice: *"At today's price, Costco trades at a multiple that implies the next decade looks substantially like the last one — about 8% revenue growth, stable operating margin, continued membership renewal above 90%. Each of those is more likely than not, individually; collectively they leave little headroom. The expected return at this price is therefore close to the long-run market return, with a margin of safety derived not from a price gap but from the durability of the underlying business."*

---

## Section 11 — What would change my mind

**Reader's question:** "What three to seven specific, observable, falsifiable events would change my mind?"

**Inputs:**
- The writer's own draft of Sections 1–9 (this section is downstream of everything above it).

**Required content:**

A numbered list of three to seven things — concrete, observable, falsifiable — that, if any of them happened, would force the reader to rethink the position. Each item is a tripwire the reader has agreed in advance to take seriously. *"Membership renewal at Costco below 87%. GEICO's expense ratio rising more than three points above Progressive's. See's volume declining more than 3% per year for three consecutive years. Microsoft's commercial cloud growth dropping below 15%."*

The discipline matters because of Munger's *Tendency 13: Deprival-Superreaction Tendency* and *Tendency 17: Inconsistency-Avoidance Tendency*. Investors are systematically bad at changing their minds in real time; pre-committing on paper to what would change the writer's mind is the cheapest and most powerful debiasing technique available. **It is the single section in the writeup most likely to save the reader money in the next five years.**

The list should be short. Pabrai's *Dhandho Investor* makes the point that *few bets, big bets, infrequent bets* is the right posture for ideas, and the same logic applies to disconfirmers: too many tripwires and none get respected.

**Word band:** 200–400 words. Brevity is the discipline.

**Section-specific notes:**
- This is the only section the writeup should resemble a list, because the items work better as discrete tripwires than as woven prose.
- Each tripwire should be observable in the company's own disclosures within four quarters of happening. "If management changes its tone" is not observable; "if free cash flow declines for two consecutive quarters" is.
- Each tripwire should map back to a load-bearing claim made earlier in the writeup. If a tripwire doesn't map to a claim, either the claim was missing or the tripwire is filler.

---

## Section 12 — Recommendation

**Reader's question:** "Given everything above, what should I do at the current price?"

**Inputs:**
- `{TICKER}_research_memo.md` Section 1 (DECISION) and Section 8 (VALUATION's entry-band)
- The writer's own Section 9 expectations work

**Required content:**

This section was deleted in the operating-manual document's anatomy because the document's view is that *"you are not recommending anything; you are describing a business; the reader can decide what to do."* The user has chosen to keep a recommendation section but to position it at the bottom — as the *output* of the analysis, not the frame the analysis is wrapped around.

The recommendation has three parts:

1. **Price ladder.** Four bands — Strong Buy / Standard Buy / Watch / Pass — with the price threshold for each and a one-sentence rationale derived from Section 9. The base-case intrinsic, the adversarial floor (from Section 8 / Step 10), and the current price all sit on this ladder. The reader sees where today's price falls.

2. **Position sizing logic.** Brief — 80–120 words. What size position is defensible at each band given the conviction level Sections 1–10 supported. *"Strong Buy below $X warrants 5–7%. Standard Buy at $Y–$Z warrants 3–5%. Watch warrants a starter at most. Pass warrants no addition."*

3. **What changes the answer without the price changing.** Brief — 80–120 words. List 3–5 specific events (drawn from Section 10's disconfirmation register, plus a few positive flips) that would move the reader from Pass back toward Watchlist or Buy without requiring a price decline.

**Word band:** 250–450 words. The recommendation is *the output*, not *the show*. Sections 1–10 do the work; Section 11 reports the verdict and stops.

**Section-specific notes:**
- This is the only section where target prices and price ladders are permitted.
- Match the verdict tone to the price-vs-intrinsic gap. If the price is meaningfully below adversarial-floor intrinsic, the recommendation can be confidently positive. If the price is meaningfully above base-case intrinsic, the recommendation should be honestly negative — *"Pass at $93 with a Watch trigger at $65."* No softening with "but with the right catalyst…"
- A reader who skipped to Section 11 should still be able to defend the conclusion at dinner because the price ladder cites the load-bearing reasoning — but the body of the writeup is sections 1–10, not this.

---

# Sections 12–14 (Python auto-generates)

These do not get a Claude draft. The Python assembler builds them from the canonical files:

- **Section 12 — Reliability disclosure.** From `verification_c.md` / `verification_a.md` + `cc_catches_against_codex.md` + the bug logs.
- **Section 13 — Glossary.** A printable summary of every glossary term that was hover-tagged anywhere in the report.
- **Section 14 — Source trail.** List of every input file actually read.

If a future iteration calls for a Claude-written addendum to one of these, change `kind` from `"auto"` to `"claude"` in `build_report.py`'s `SECTIONS` constant and add the corresponding writing prompt here.

---

# Iteration

Build time: research takes ~90 minutes per ticker and is not re-run by `/stock-report`. Section drafts are cached; `--rebuild` clears all 11 Claude drafts; `--rebuild-section N` clears one. Iterating on writing prompts costs minutes, not hours.

If a section repeatedly fails its verification gates:
1. First — refine the prompt for that section in this file (often the issue is a missing constraint or word-band mismatch).
2. Second — refine the relevant primer's framing if the failure is sector / industry teaching.
3. Third — adjust the universal craft tactics or hard constraints if the failure pattern crosses sections.

Don't keep rebuilding without changing what you're prompting from.

---

# Files in this skill

- `SKILL.md` — this file. Per-section writing prompts.
- `scripts/build_report.py` — orchestrator. `--prep`, `--assemble`, `--rebuild`, `--rebuild-section N`, `--status`. Reads `raw/gics.txt` only; never guesses.
- `scripts/svg_charts.py` — line, bar, donut, scatter, heatmap, paired-bar, horizontal-bar.
- `scripts/inject_glossary.py` — post-processing pass that wraps glossary terms.
- `templates/report.html` — outer skin (CSS, hover tooltips, callouts, print rules).
- `assets/glossary_core.json` — 52 cross-cutting finance terms.
- `assets/learn_more_finance.json` — 16 verified-URL cross-cutting Learn-more pointers.
- `assets/sectors/<Sector>_primer.md` — per-sector resource libraries (just-in-time; user runs the prompt at `assets/sectors/_research_prompts/<Sector>_primer_prompt.md`).
- `assets/industries/<Industry>_primer.md` — per-industry resource libraries (just-in-time; user runs the prompt at `assets/industries/_research_prompts/<Industry>_primer_prompt.md`).

---

# What this skill does NOT do

- Run any research. Consumes post-verification files only.
- Guess GICS classification. Reads `raw/gics.txt` exclusively; if missing, Claude looks up via WebFetch.
- Use CAPM, beta-derived discount rates, target prices in body, sensitivity tables, SWOT, or pasted Porter five-forces.
- Modify the research files. Read-only on `raw/` and `steps/`; only writes `_report_drafts/` and the final HTML.
- Auto-open the report.

---

# Failure modes

- **Memo or `verification_a.md` missing.** Skill aborts. Run `/stock-research TICKER` first.
- **`raw/gics.txt` missing.** Skill aborts with a clear error. Resolve via Step 0 (WebFetch on Wikipedia / IR page; AskUserQuestion as fallback).
- **A step file is missing.** That section's draft marks the missing piece with `[GAP: <what's missing>]`. The build still produces.
- **Sector or industry primer missing.** Build proceeds without enrichment; the section prompt's "primer-conditional" branches kick in.
- **A required URL in `learn_more_finance.json` returns 404 at write time.** Skip that callout; flag the entry for re-verification. Don't silently substitute.
