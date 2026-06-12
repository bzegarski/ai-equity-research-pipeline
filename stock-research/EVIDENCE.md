# stock-research — empirical evidence and historical record

This file is loaded only when iterating on the stock-research skill. The everyday operational rules live in `CLAUDE.md`.

Holds the run-by-run evidence base, the catalogue of already-fixed bugs (with which run surfaced them), and the log of design decisions made and later unmade.

---

## Decisions made and unmade

A small log of architectural calls that were made on then-available evidence and later reversed. The point: a future reader can see what we tried, why we backed out, and what evidence justified the reversal. Don't redo what was deliberately undone.

- **COD-1 (made 2026-04-29 PANW; reversed 2026-05-10).** PANW's first run produced zero substantive Codex catches on the 10-K cross-check while CC alone caught four real items (proxy comp depth, ownership tables, CyberArk mechanics, GAAP-vs-non-GAAP gap). Decision: drop 10-K from Codex's Step 1A. **Reversed** 2026-05-10 on the user's call. The 10-K is the most important document; n=1 is too thin to justify asymmetric coverage; the n=6 cross-check value pattern is *distributed* across both sides, with no specialty clustering. 10-K returned to dual-summary + cross-check, like the other core documents. Codex shipped the Codex-side change in parallel with CC's planning (2026-05-10). Competitor narrowing is separate and stayed in place.

- **CAPM-creep (made 2026-05-09 Round 3; reversed 2026-05-12 post-CRWD).** The Round-3 valuation rewrite (per Feedbak research-c "DCF methodology for compounders") adopted "CAPM-consistent fair value + above-CAPM hurdle" as the synthesis. Fair value tier used `long_bond + ERP × beta`; Buffett-pure rate (no premium) was demoted to "diagnostic only — not a decision input." **Reversed** 2026-05-12 after the CRWD run exposed the user's stated framework being inverted in practice. CC and Codex independently read the full Berkshire transcripts 1994–2022 + letters 1977–2024 and converged on the Buffett-canonical framework: ONE rate (long-bond + mechanical real-rate cushion), no ERP, no beta. CAPM moved to clearly-labeled illustrative parallel that does NOT feed buy/keep/sell. Stage-0 underwriteability gate added as binary go/no-go filter (per Buffett 1998 [TX 19927]: *"if we think we simply don't know what's going to happen in the future... we just give up"*). Single conservative intrinsic value + mechanical sensitivity table replaces three-scenario structure (Buffett single-point estimation with scream filter, per [TX 61055]). SBC fully deducted via GAAP NI starting point; per-share intrinsic uses current diluted shares (NOT projected year-5) to avoid triple-counting for SBC-heavy SaaS. The reversal is grounded in 30 years of Buffett/Munger primary-source language; the CC ↔ Codex convergence after independent reads is the validation.

---

## Already-fixed bugs (with detection runs)

If a new bug appears in `bugs_encountered.md` or `bugs_encountered_codex.md`, add the entry here when fixed.

### PANW (2026-04-29) — 5 bugs surfaced, all fixed

- ✅ Form 4 padded CIK (BUG-1) → `parse_form4.py` strips leading zeros
- ✅ HTML stripping eliminated newlines (BUG-2) → `strip_10k.py` replaces block tags with `\n`
- ✅ Read tool failed on single-line large files → `extract_sections.py` writes per-section chunks to `_chunks/`
- ✅ Inverted `\xa0` convention for FTNT/CRWD competitors → gap-based section-pair fallback in `extract_sections.py`
- ✅ Stock-split distortion in `SharesOutstanding` → `extract_xbrl.py` detects >30% YoY jumps and prefers `dei/EntityCommonStockSharesOutstanding`
- ✅ Transcript-summary-vs-verbatim ambiguity → `detect_transcript_format.py` writes `TRANSCRIPT_SOURCE_QUALITY` header

### PAYX + MSFT — 5 more, all fixed

- ✅ CIK resolver false-match (MSFT: searching "MSFT" returned Activision Blizzard) → `resolve_cik.py` now requires the ticker as second arg and checks the result's display_name contains `(TICKER)`. The Phase 0 download instructions pass `{TICKER}` and `{COMP_TICKER}`.
- ✅ Working-directory fragility in `extract_8k.py` and `parse_form4.py` (MSFT: silent failure of all 30 sub-fetches via relative paths) → both scripts now derive base directory from the output-path argument, fail loud with non-zero exit if zero items recovered, and assert input files exist.
- ✅ Section-extraction TOC false positives (MSFT: AMZN/GOOGL competitor 10-Ks produced 29-byte chunks) → `extract_sections.py` now applies a `MIN_SECTION_LENGTH = 500` floor on each extracted slice; rejected matches retrigger the gap-based fallback.
- ✅ Transcript verbatim heuristic too narrow (MSFT: verbatim IR `.docx` tagged structured_summary) → `detect_transcript_format.py` now also matches `(operator direction.)` and CAPS-label speaker patterns (regex on original-case text).
- ✅ XBRL ratio anchor artifact (PAYX: OCF/NetIncome computed 2.82× because NetIncome anchor was 2015) → `extract_xbrl.py` now requires both endpoints of any computed ratio to share fiscal year; mismatched anchors emit `ANCHOR_INCOMPLETE` instead of a misleading number.

### CRWD (2026-05-10) — bugs surfaced, fixed in the v1.3 Buffett-framework iteration (2026-05-12)

- ✅ XBRL Revenue concept gap (CRWD reports under `RevenueFromContractWithCustomerIncludingAssessedTax`; `extract_xbrl.py` only checked the `Excluding` variant) → false `XBRL_MISSING: Revenue` warning forced manual fix during Codex `--audit`. Fixed: added `Including` variant to concept-fallback list with comment citing CRWD precedent.
- ✅ TOC strip survived inline duplicate (CRWD `clean_canonical.py` reported `STRIPPED_TOC: 31024 chars` but `10k_raw.txt` still started with inline TOC; manual +7,088-char trim needed). Fixed: added strict uppercase anchor `\bITEM\s*1\.\s*BUSINESS\b` for post-strip enforcement; if cleaned text doesn't start at this anchor within 200 chars, emit `CRITICAL_TOC_STRIP` audit-gate flag.
- ✅ Verification D ran inline instead of as cold subagent (final-memo agent was instructed to "dispatch" Verification D as a subagent but ran it inline; the fresh-context test that's the whole point of Verification D never fired). Fixed: orchestrator (parent skill `phases/step1e_pipeline.md` Phase 7) now dispatches the cold subagent directly after the final-memo agent completes. Final-memo agent's job ends at Verification C; explicit note in `agents/final_memo.md` forbids inline Verification D.
- ✅ FCF definition drift cascaded across files until Phase 3.5 caught it (CRWD step3 + raw/10k used 10-K convention $1.31B; raw/proxy + step8 used proxy/IR convention $1.24B; both labeled "FCF" without qualifier). Fixed: `references/owner_earnings.md` adds mandatory FCF-labeling rule (every file using "FCF" must label which definition); Step 3.5 propagation gate enforces.
- ✅ External-FCF ingestion poisoning (sell-side reports add SBC back as non-cash; if the skill consumes their "FCF" without conversion, owner earnings is silently over-stated). Fixed: `references/owner_earnings.md` adds external-FCF ingestion bridge rule with explicit conversion table.
- ✅ SBC double-counting in valuation framework (the Round-3 architecture deducted SBC from FCF AND modeled future dilution separately — triple-count for SBC-heavy SaaS). Fixed: `references/owner_earnings.md` adds canonical formula starting from GAAP NI (SBC already deducted there — do NOT add back) + conditional-on-starting-point table (NI / OCF / adjusted-FCF / non-GAAP) + per-share dilution rule (current shares as primary denominator; projected year-5 only as sensitivity input).
- ✅ CAPM rate as primary fair-value tier (decision-relevant rate used `long_bond + ERP × beta`; Buffett-pure rate was "diagnostic only"). Fixed: Buffett rate is now primary; CAPM moved to clearly-labeled illustrative parallel. See "CAPM-creep" in Decisions made and unmade.
- ✅ Buyback above intrinsic destroying value silently (CRWD bought back at $364 avg vs reconciled intrinsic $155–$295; framework treated buyback as universally positive TSR). Fixed: `references/valuation_methods.md` Stage 6B adds buyback/issuance asymmetry rule — buyback yield is positive ONLY if avg_buyback_price < intrinsic_conservative; symmetric mirror for share issuance.

### DECK + SNOW + NVO (n=6) — 5 more, fixed in the v1.2 iteration (2026-05-07)

- ✅ CIK resolver missed FPI multi-ticker patterns and tickers absent from full-text-search hits (NVO `(NVO, NONOF)`, SNOW returned Peak Resorts, DECK no display match) → `resolve_cik.py` loosens the regex to `[(,]\s*TICKER\s*[),]` AND falls back to `https://www.sec.gov/files/company_tickers.json` when the regex misses.
- ✅ Section-extraction TOC false-positive locked Item 8 in TOC region when Item 7 strict failed (DECK + SNOW: item7.txt missing, item1a.txt swallowed everything to end-of-file because the `run_pair_fallback` only fills `-1` slots) → `extract_sections.py` adds a `sequential_rescue` step that, when Item 7 is still missing after gap-fallback, finds the first body-prose Item 7 candidate after Item 1A and overrides Item 8 if it's positioned ahead of the new Item 7. Also adds `--chunks-dir` so competitor extractions land in `raw/_chunks_comp/{COMP}/` without clobbering the primary ticker's chunks (DECK regression).
- ✅ Transcript classifier auto-tagged Motley Fool / Yahoo / Investing.com LLM-passthroughs as verbatim (DECK + SNOW) → `detect_transcript_format.py` replaces text-only OR-logic with a weighted classifier: domain prior (negative for fool.com, yahoo, investing.com, marketwatch, globenewswire, seekingalpha; positive for q4cdn / IR domains / sec.gov) plus structure score (CAPS labels, Operator phrases, Q&A markers; minus for "key takeaways", "earnings call summary", Motley Fool boilerplate). Verbatim only if structure score clears threshold AND domain prior non-negative.
- ✅ Hardcoded `us-gaap` namespace in XBRL extractor (NVO IFRS filer required ad-hoc inline script) → new `scripts/extract_ifrs_xbrl.py` (33 IFRS concepts, USD>EUR>DKK>CHF>GBP currency preference, anchor-mismatch guard mirroring us-gaap version). `extract_xbrl.py` auto-delegates when `us-gaap` is empty and `ifrs-full` is present. Both extractors emit `TAXONOMY:` and `CURRENCY:` header lines so downstream agents read either uniformly.
- ✅ TOC/cover-page leak into raw text (NVO 1,305-char 6-K cover; DECK 10,794-char TOC) → new `scripts/clean_canonical.py` runs after `strip_10k.py` with `--track {10k|20f|fpi|6k}`. 10-K track scans for first body-prose `ITEM 1. BUSINESS` (≥200 alpha in next 1500 chars, not preceded by TOC page-number pattern) and trims everything before it. 20-F / FPI track tries `ITEM 4. INFORMATION ON THE COMPANY` then a loose `Introducing X` anchor. 6-K track strips only the SEC cover header. Skipped silently when no anchor found.

---

## Validated by PAYX + MSFT + DECK + SNOW + NVO + CRWD evidence (n=7 with PANW)

**Buffett-framework convergence (CRWD post-run, 2026-05-12).** After the CRWD run exposed CAPM creep in the decision-relevant valuation, CC and Codex independently read the full Berkshire transcripts 1994–2022 (115,552 lines) + letters 1977–2024 (41,564 lines) and arrived at the same Buffett-faithful framework: ONE rate (long-bond + mechanical real-rate cushion), no ERP, no beta; Stage-0 underwriteability gate before any DCF; owner earnings starting from GAAP NI (SBC already deducted — do NOT add back); ONE conservative intrinsic + mechanical sensitivity table (not three scenarios); MoS from a 3×3 Stage-0 × moat-tier matrix; opportunity-cost floor as separate concept; capital-allocation tests; CAPM only as illustrative parallel. This is the validated structural decision the v1.3 iteration ships. The CC ↔ Codex independent convergence is the validation; this is what falls out of reading both files end-to-end.

**Stage-0 underwriteability gate (added 2026-05-12).** Binary classification before any DCF: UNDERWRITABLE / PARTIAL / TOO HARD. Per Buffett 1998 [TX 19927]: *"if we think we simply don't know what's going to happen in the future... we just give up."* The gate eliminates the prior pattern of producing plausible-looking DCFs for businesses whose cash flows aren't defensibly forecastable. Regression tests: AAPL → UNDERWRITABLE; CRWD → PARTIAL; early-stage biotech → TOO HARD.


- **Dual-model substantive value generalizes — distributed, not concentrated.** PANW concentrated in 10-Q Item 5 (10b5-1 plans). PAYX caught BlackRock related-party (proxy), Gioja transition status (proxy), and the Bonadio omission via consistency check. MSFT caught buyback-table detail (10-Q), Numoto-son related-party (proxy), legal contingencies (10-Q), and finance-lease/capex framing (transcripts + attack). The catches are spread across document types — PANW's concentration was sample noise, not a structural feature.
- **Phase 3.5 consistency check is load-bearing.** Validated. PAYX caught the load-bearing FCF/float misframing and the four-vs-three related-party-transaction count. MSFT caught OpenAI Azure-exclusivity language carried forward from FY25 10-K despite Oct 2025 / Apr 2026 amendments removing it, plus a board-transition wording precision. SNOW caught direct internal contradiction. These are real inter-section contradictions Verification A/B/C cannot catch. Hit-rate is conditional on Phase 3 producing multiple layered claims that can contradict; for unusually thin Phase 3 outputs, expect lower yield.
- **Bidirectional correction integration mechanism.** CC writes `raw/cc_catches_against_codex.md` at end of Phase 3.4 (before `--consistency` handoff) and refreshes at end of Phase 6.5 (before `--attack`). Codex reads it in both phases. PAYX showed clear examples of CC catches (Comparisun/G2 number, "industry-leading HCM" claim, Hansen background) that Codex previously never saw. The inbox closes that loop.
- **Codex's own bug log + run review** (`bugs_encountered_codex.md`, `codex_run_review.md`) — Codex implements per-phase entries and end-of-`--attack` review. Mirror-format with five Codex-specific sections: CC catches against Codex seen too late; would output have changed; Codex catches adopted/rejected/unknown; gate value by phase; skill edits recommended.

---

## Empirical evidence base (run-by-run)

What we actually know vs. what we think we know.

**PANW (2026-04-29):**
- Verification A/B/C achieved 100% reliability on 50 verified claims, 0 corrections at any analytical phase.
- Codex's substantive cross-check value concentrated in 10-Q Item 5 (10b5-1 plan disclosures); CC missed these without IMP-1 fix.
- 10-K cross-check on this run: zero substantive Codex catches; CC alone caught proxy comp, ownership tables, CyberArk mechanics, GAAP-vs-non-GAAP gap. Drove the original COD-1 (later reversed; see "Decisions made and unmade").
- Phase 0 had two propagating bugs (Form 4 CIK, FTNT/CRWD inverted `\xa0`); both required human intervention.
- Final decision: WATCHLIST at $90-100 trigger vs market $182.90 (skill correctly identified overvaluation).

**PAYX (2026-05-05):**
- 13 Phase 0 / Step 1B+1C warnings, 8 corrections; final reliability 98.5% (66 of 67 verified, 1 HUMAN-VERIFY).
- Codex caught BlackRock related-party ($1.5M) and Gioja transition status (proxy); CC caught Comparisun/G2 aggregator number, "industry-leading HCM" overreach, Hansen director profile (post-proxy).
- Phase 3.5 consistency check caught load-bearing FCF/float misframing and Bonadio related-party omission propagated across 3 files.
- XBRL OCF/NetIncome ratio anchor artifact (NetIncome XBRL only had FY15 data) → fixed.
- Final decision: PASS at $93.02; watch trigger $65, buy zone <$55. Base intrinsic $70.76; combined-stress floor $42.89; counter-attack supported PASS.
- Key Insight authentic (dividend-defense feedback loop tying 87% payout, $4.6B debt, 0.08% CEO ownership, Feb 2026 service-hours cut).

**MSFT (2026-05-09):**
- 14 distinct bugs/corrections, including CIK false-match (Activision Blizzard returned for "MSFT" query) and working-directory fragility (silent failure of all 30 sub-fetches).
- Codex caught OpenAI Azure-exclusivity language carried forward from FY25 10-K despite Oct 2025 / Apr 2026 amendments removing it; CC adopted in Step 3.5.
- Codex caught Rainey/Rodriguez board-transition wording precision; finance-lease/capex economic-cash-flow attack from Codex Step 10.
- "Codex Unavailable" warning was a phantom — caused by `/` vs `$` activation-syntax confusion, not actual unavailability.
- Final decision: WATCHLIST at $220 (25% MoS on owner-earnings intrinsic of $291).
- Key Insight authentic ("paying twice for the same moat dollar" with Cisco-2000 vs 2014 analog).

**DECK (2026-05-05/06):** US-issuer, footwear consumer cyclical (UGG/HOKA). Codex caught the `phase0_audit.md` lingering CRITICAL flag despite the underlying file being fixed. CC caught primary-source aggregator over-block (APMA HOKA listings blocked alongside legitimate aggregator noise) — surfaced the binary primary-source rule's brittleness. Section extraction failed: item7.txt missing, item1a.txt swallowed everything (Item 8 TOC false-positive locked). Fixed in v1.2 via `sequential_rescue` in `extract_sections.py`. Final decision: stale memo claim of 25% MoS too strong given combined-bear is admitted plausible.

**SNOW (2026-05-06):** US-issuer, data cloud SaaS. Codex caught direct internal contradiction in memo (line 62 asserts CFLT puts a floor; line 127 admits Codex's caveat that strategic-acquisition multiples don't anchor public-market valuation). Append-only correction drift propagated stale phrasing. Same item7-missing extraction bug as DECK; same fix.

**NVO (2026-05-06):** Foreign private issuer (Denmark), IFRS, files 20-F + 6-K not 10-K. Stretched every Phase 0 step — manual workaround for IFRS XBRL (ad-hoc `extract_ifrs_inline.py`), manual workaround for 20-F section structure, TOC leaking into canonical, FY26 guidance carried stale (Feb baseline -5% to -13% never updated to Q1 2026 6-K's -4% to -12%), Phase 6 Sovaldi/Harvoni framed as clean patent-cliff analog when it was price + volume + competition collapse. v1.2 fixes promote IFRS extractor, add FPI track to Phase 0, add `clean_canonical.py`, add Step 3.5 propagation gate, and add the two-sentence analog rule (Phase 4 / 6).

### What this n=6 evidence supports

- Phase 3.5 consistency check is fully validated — caught compound errors in PAYX, MSFT, SNOW. NVO's stale guidance is the same class of bug (append-only drift), justifying the new Step 3.5 propagation gate.
- Cross-check value is distributed across document types and across both models — no specialty clustering at n=6.
- Verification A/B/C continued ~zero corrections at analytical phases — per-stage Codex audits remain correctly rejected.
- Codex's Phase 0 audit is a collection-integrity guardrail (low analytical yield, but DECK caught a stale audit-file flag and NVO/DECK upstream issues that propagated).
- The hard primary-source rule (post-PAYX) over-corrected on DECK (APMA blocked) — replaced with axis-based classifier.

### Still unknown after n=6

- Verification D rejection effectiveness — across all 6 runs, D has not been observed firing to reject a Key Insight yet.
- Deep Research API integration value (`--deep-customer`, `--deep-attack-research`) — opt-in, no run yet has invoked it.
- Wall-clock time per ticker (NVO Phase 5 ran 6h 37m before completing — this is what the new agent watchdog catches).
- Whether the new FPI track works end-to-end on a clean FPI filing whose 20-F uses Item 4 / Item 3D / Item 5 / Item 18 numbering (NVO's d2 annual-report exhibit doesn't, so that part of the FPI extraction is untested).

---

## Round 3 (2026-05-09) — what changed

Valuation went from one phase (~10% of the skill's emphasis) to three phases (Phase 5A CC valuation + Phase 5B Codex valuation + Phase 5C reconciliation; ~30-40% of the skill's emphasis per user direction). The framework is the dual-model multi-method three-tier architecture.

What's deferred (out of scope for Round 3, flag for next iteration):
- Dual-model architecture for Phase 6 counter-attack (currently Codex `--attack` is optional)
- Verification D never-fired observation — add a deliberately-confabulated Key Insight test ticker
- Quarterly review process for `outcomes_log.md`
- Asymmetric model specialization (still pending evidence at n>6)

What's now done that was previously deferred:
- ✅ Independent valuation recalculation by Codex (was deferred since PANW; now the centerpiece)
- ✅ Per-company discount rate (was hardcoded 10%; now max(long-bond, 10%) hurdle + long-bond + ERP for fair value)
- ✅ Per-company Stage-1 length (was hardcoded 5y; now 5-15 by moat tier)
- ✅ Equity vs EV unification (real bug Codex caught)
- ✅ Foreign-filer currency mixing (catastrophic bug fixed in extract_xbrl.py + extract_ifrs_xbrl.py)
- ✅ Reverse-split detection (silent bug fixed)
